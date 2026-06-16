-- models/staging/stg_credit_applications.sql

WITH source_data AS (
    -- La macro source() de dbt permite parametrizar el origen de datos sin dejar nombres fijos de proyectos en el SQL
    SELECT * FROM {{ source('raw_synapse', 'tbl_crm_credit_app_raw') }}
)

SELECT
    -- Casting explícito de identificadores para asegurar consistencia en los JOINs
    CAST(id_app AS STRING) AS credit_application_id,
    CAST(cod_cli AS STRING) AS customer_id,
    CAST(cod_store AS STRING) AS store_id,

    -- Estandarización de cadenas de texto y manejo de nulos en variables categóricas
    LOWER(TRIM(txt_prod_cat)) AS product_category,
    COALESCE(LOWER(TRIM(status_op)), 'unknown') AS application_status,

    -- Normalización de tipos numéricos transaccionales a punto flotante de alta precisión
    CAST(amt_req AS FLOAT64) AS requested_credit_amount,
    CAST(val_income AS FLOAT64) AS declared_monthly_income,
    CAST(pct_debt_ratio AS FLOAT64) AS monthly_debt_ratio,

    -- Transformación estricta de cadenas de texto o enteros a objetos de tiempo de BigQuery
    PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', dt_created) AS application_created_at

FROM source_data
