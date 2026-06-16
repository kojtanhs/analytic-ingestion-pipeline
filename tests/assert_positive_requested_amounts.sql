-- tests/assert_positive_requested_amounts.sql
-- dbt test fails if this query returns any rows.

SELECT
    credit_application_id,
    requested_credit_amount
FROM {{ ref('stg_credit_applications') }}
WHERE requested_credit_amount <= 0
