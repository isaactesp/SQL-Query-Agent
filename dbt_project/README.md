# dbt project — transformation layer

Turns the `raw` schema (loaded by `sql-query-agent ingest`) into:

- `models/staging/` — silver layer: one cleaned view per source, plus source definitions and tests.
- `models/marts/` — gold layer: star schema (`fct_orders`, `dim_customers`, `dim_products`).
- `semantic/semantic_layer.yml` — business description of the gold layer, consumed by the AI layer.
- `analyses/validate_semantic_layer.sql` — sanity checks for the semantic-layer metrics.

Run from the project root with `sql-query-agent transform` (equivalent to `dbt build`),
or directly from this folder with `dbt run && dbt test`.
