-- =============================================================================
-- Semantic Layer Validation Queries
-- dbt tests cover column quality (nulls, uniqueness, relationships).
-- These cover what dbt tests cannot: business KPIs and cross-model
-- consistency. Run each block independently.
-- =============================================================================


-- METRICS: confirm each aggregation resolves against real data.
-- Expected: three positive numbers; avg_order_value must equal manual_check.
SELECT
    SUM(REVENUE)                              AS total_revenue,
    COUNT(ORDER_ID)                           AS order_count,
    ROUND(AVG(REVENUE), 2)                    AS avg_order_value,
    ROUND(SUM(REVENUE) / COUNT(ORDER_ID), 2)  AS manual_check
FROM main_marts.fct_orders;


-- CROSS-CHECK: revenue consistency between fct_orders and dim_customers.
-- Expected: gap is zero, or a few cents from rounding at different grains.
SELECT
    (SELECT ROUND(SUM(REVENUE), 2) FROM main_marts.fct_orders)                  AS revenue_from_fact,
    (SELECT ROUND(SUM(CUSTOMER_LIFETIME_VALUE), 2) FROM main_marts.dim_customers) AS revenue_from_dim,
    (SELECT ROUND(SUM(REVENUE), 2) FROM main_marts.fct_orders)
      - (SELECT ROUND(SUM(CUSTOMER_LIFETIME_VALUE), 2) FROM main_marts.dim_customers) AS gap;


-- DIMENSIONS: inventory of every value the AI will encounter.
-- Expected: no nulls, no surprises. Anything here that is not described in
-- semantic_layer.yml is a gap in the AI's knowledge - go add it.
SELECT 'CATEGORY'     AS dimension, CATEGORY     AS value, COUNT(*) AS orders FROM main_marts.fct_orders GROUP BY CATEGORY
UNION ALL
SELECT 'BRAND_NAME'   AS dimension, BRAND_NAME   AS value, COUNT(*) AS orders FROM main_marts.fct_orders GROUP BY BRAND_NAME
UNION ALL
SELECT 'COUNTRY_CODE' AS dimension, COUNTRY_CODE AS value, COUNT(*) AS orders FROM main_marts.fct_orders GROUP BY COUNTRY_CODE
UNION ALL
SELECT 'ORDER_STATUS' AS dimension, ORDER_STATUS AS value, COUNT(*) AS orders FROM main_marts.fct_orders GROUP BY ORDER_STATUS
ORDER BY dimension, orders DESC;