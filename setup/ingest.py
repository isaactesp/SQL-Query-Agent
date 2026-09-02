import os

import duckdb
import pandas as pd

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "warehouse", "warehouse.duckdb")
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")

FILES = {
    "orders": "orders_raw.csv",
    "customers": "customers_raw.csv",
    "products": "products_raw.csv",
}

# ── Make sure warehouse directory exists ─────────────────────────────────────
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# ── Connect ───────────────────────────────────────────────────────────────────
print(f"[connect] Connecting to DuckDB at: {DB_PATH}")
con = duckdb.connect(DB_PATH)

# ── Create raw schema ─────────────────────────────────────────────────────────
con.execute("CREATE SCHEMA IF NOT EXISTS raw")
print("[ok] Schema 'raw' ready")

# ── Load each CSV ─────────────────────────────────────────────────────────────
for table_name, filename in FILES.items():
    filepath = os.path.join(RAW_DIR, filename)

    if not os.path.exists(filepath):
        print(f"  [error] File not found: {filepath}")
        print("     Run: python data/raw/generate_dataset.py first")
        continue

    # Read with pandas (all columns as strings — DuckDB will infer types)
    df = pd.read_csv(filepath, dtype=str)
    print(f"\n[load] Loading raw.{table_name}...")
    print(f"   Source: {filename}")
    print(f"   Rows:   {len(df):,}")
    print(f"   Cols:   {list(df.columns)}")

    # Register DataFrame and create table
    con.register("_temp_df", df)
    con.execute(f"DROP TABLE IF EXISTS raw.{table_name}")
    con.execute(f"CREATE TABLE raw.{table_name} AS SELECT * FROM _temp_df")
    con.unregister("_temp_df")

con.close()
print("\n[done] Ingestion complete!")
