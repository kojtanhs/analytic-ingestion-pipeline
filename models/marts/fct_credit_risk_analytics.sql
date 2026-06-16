-- models/marts/fct_credit_risk_analytics.sql

{{
    config(
        materialized='table',
        partition_by={
            "field": "application_date",
            "data_type": "date",
            "granularity": "day"
        },
        cluster_by=["store_id", "application_status"]
    )
}}

WITH intermediate_profile AS (
    SELECT * FROM {{ ref('int_customer_credit_profile') }}
)

SELECT
    -- Llaves primarias y de negocio
    credit_application_id,
    customer_id,
    store_id,
    
    -- Dimensiones temporales particionadas
    CAST(application_created_at AS DATE) AS application_date,
    application_created_at,

    -- Atributos del contexto de la solicitud
    product_category,
    application_status,

    -- Variables financieras crudas estandarizadas
    requested_credit_amount,
    declared_monthly_income,
    monthly_debt_ratio,

    -- Variables de comportamiento histórico (Plata)
    historical_application_count,
    total_past_requested_amount,
    previous_application_status,
    days_since_last_application,
    income_to_gift_ratio,

    -- Ingeniería de Características Avanzada (Feature Engineering para IA)
    -- 1. Indicador binario si el cliente es de alto riesgo debido a deudas previas superiores al 50% de sus ingresos
    CASE 
        WHEN monthly_debt_ratio > 0.50 THEN 1
        ELSE 0
    END AS is_high_debt_risk,

    -- 2. Variable categórica combinada para detectar patrones de solicitudes consecutivas rechazadas
    CASE
        WHEN previous_application_status = 'rejected' AND application_status = 'pending' THEN 'high_risk_reapply'
        WHEN previous_application_status = 'approved' AND application_status = 'approved' THEN 'loyal_active_client'
        ELSE 'standard_evaluation'
    END AS behavioral_risk_segment,

    -- 3. Métrica de exposición financiera actual frente al historial del cliente
    CASE 
        WHEN total_past_requested_amount > 0 THEN ROUND(requested_credit_amount / total_past_requested_amount, 4)
        ELSE 1.0
    END AS credit_expansion_ratio

FROM intermediate_profile
