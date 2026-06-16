-- models/intermediate/int_customer_credit_profile.sql

WITH staging_data AS (
    SELECT * FROM {{ ref('stg_credit_applications') }}
),

window_aggregations AS (
    SELECT
        credit_application_id,
        customer_id,
        store_id,
        product_category,
        application_status,
        requested_credit_amount,
        declared_monthly_income,
        monthly_debt_ratio,
        application_created_at,

        -- 1. Total de solicitudes históricas del cliente hasta el momento actual
        COUNT(credit_application_id) OVER(
            PARTITION BY customer_id
            ORDER BY application_created_at
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS historical_application_count,

        -- 2. Monto total acumulado solicitado por el cliente en el pasado
        SUM(requested_credit_amount) OVER(
            PARTITION BY customer_id
            ORDER BY application_created_at
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS total_past_requested_amount,

        -- 3. Identificar el estado de la solicitud inmediatamente anterior usando LAG
        LAG(application_status) OVER(
            PARTITION BY customer_id
            ORDER BY application_created_at
        ) AS previous_application_status,

        -- 4. Calcular la diferencia en días desde su última solicitud de crédito
        TIMESTAMP_DIFF(
            application_created_at,
            LAG(application_created_at) OVER(
                PARTITION BY customer_id
                ORDER BY application_created_at
            ),
            DAY
        ) AS days_since_last_application

    FROM staging_data
)

SELECT
    credit_application_id,
    customer_id,
    store_id,
    product_category,
    application_status,
    requested_credit_amount,
    declared_monthly_income,
    monthly_debt_ratio,
    application_created_at,
    historical_application_count,
    
    -- Control de nulos para el primer registro histórico del cliente
    COALESCE(total_past_requested_amount, 0.0) AS total_past_requested_amount,
    COALESCE(previous_application_status, 'first_time') AS previous_application_status,
    COALESCE(days_since_last_application, -1) AS days_since_last_application,

    -- Métrica calculada intermedia: Ratio de ingresos sobre el monto solicitado actual
    CASE 
        WHEN declared_monthly_income > 0 THEN ROUND(requested_credit_amount / declared_monthly_income, 4)
        ELSE 0.0
    END AS income_to_gift_ratio

FROM window_aggregations
