"""
Loads the raw CSVs verbatim (all columns as strings) into the `raw` schema of
the DuckDB warehouse. dbt takes it from there.

Run with:  sql-query-agent ingest
"""

from __future__ import annotations

import duckdb
import pandas as pd

from sql_query_agent.config import settings

FILES = {
    "orders": "orders_raw.csv",
    "customers": "customers_raw.csv",
    "products": "products_raw.csv",
}


def ingest() -> None:
    missing = [f for f in FILES.values() if not (settings.raw_dir / f).exists()]
    if missing:
        raise FileNotFoundError(
            f"Missing raw files in {settings.raw_dir}: {missing}. "
            "Run `sql-query-agent generate` first."
        )

    settings.warehouse_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[connect] DuckDB at: {settings.warehouse_path}")

    with duckdb.connect(str(settings.warehouse_path)) as con:
        con.execute("CREATE SCHEMA IF NOT EXISTS raw")

        for table_name, filename in FILES.items():
            df = pd.read_csv(settings.raw_dir / filename, dtype=str)
            print(f"[load] raw.{table_name:<10} {len(df):>6,} rows  <- {filename}")

            con.register("_temp_df", df)
            con.execute(f"CREATE OR REPLACE TABLE raw.{table_name} AS SELECT * FROM _temp_df")
            con.unregister("_temp_df")

    print("[done] Ingestion complete.")


def main() -> None:
    ingest()


if __name__ == "__main__":
    main()
