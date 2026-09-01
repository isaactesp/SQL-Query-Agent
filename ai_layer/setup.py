"""
setup.py
--------
One-time setup: trains the Vanna RAG model on the semantic layer and mart DDL.
Run once before using query_engine.py or the Streamlit app.

Run with:  python ai_layer/setup.py
"""

import os
import yaml
import duckdb
from vanna.ollama import Ollama
from vanna.chromadb import ChromaDB_VectorStore

# -- Paths --------------------------------------------------------------------
PROJECT_ROOT        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH             = os.path.join(PROJECT_ROOT, "data", "warehouse", "warehouse.duckdb")
SEMANTIC_LAYER_PATH = os.path.join(PROJECT_ROOT, "dbt_project", "semantic", "semantic_layer.yml")
CHROMA_PATH         = os.path.join(PROJECT_ROOT, "ai_layer", "vanna_store")


# -- Vanna class: ChromaDB (vector store) + Ollama (LLM) ----------------------
class VannaEcommerce(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)


def get_vanna() -> VannaEcommerce:
    vn = VannaEcommerce(config={"model": "llama3.1", "path": CHROMA_PATH})
    vn.connect_to_duckdb(url=DB_PATH)
    return vn


def train(vn: VannaEcommerce) -> None:
    # -- 1. Train on mart DDL --------------------------------------------------
    con = duckdb.connect(DB_PATH)
    for table in ("fct_orders", "dim_customers", "dim_products"):
        cols = con.execute(f"""
            SELECT column_name, data_type
            FROM duckdb_columns()
            WHERE table_name = '{table}' AND schema_name = 'main_marts'
        """).fetchall()
        ddl = f"CREATE TABLE main_marts.{table} (\n"
        ddl += ",\n".join(f"  {col[0]} {col[1]}" for col in cols)
        ddl += "\n);"
        vn.train(ddl=ddl)
        print(f"[trained] DDL: {table}")
    con.close()

    # -- 2. Train on semantic layer documentation ------------------------------
    with open(SEMANTIC_LAYER_PATH, "r") as f:
        semantic = yaml.safe_load(f)

    for model in semantic.get("semantic_layer", {}).get("models", []):
        doc = f"Table: {model['name']}\nSchema: {model.get('schema', 'main_marts')}\n{model['description']}"
        vn.train(documentation=doc)
        print(f"[trained] model doc: {model['name']}")

    for metric in semantic.get("semantic_layer", {}).get("metrics", []):
        doc = (
            f"Metric: {metric['name']}\n"
            f"Description: {metric['description']}\n"
            f"Model: {metric['model']}\n"
            f"SQL aggregation: {metric['aggregation']}"
        )
        vn.train(documentation=doc)
        print(f"[trained] metric doc: {metric['name']}")

    for dim in semantic.get("semantic_layer", {}).get("dimensions", []):
        doc = (
            f"Dimension: {dim['name']}\n"
            f"Description: {dim['description']}\n"
            f"Model: {dim['model']}\n"
            f"Column: {dim['column']}\n"
            f"Type: {dim['type']}"
        )
        vn.train(documentation=doc)
        print(f"[trained] dimension doc: {dim['name']}")

    # -- 3. Seed example question-SQL pairs ------------------------------------
    examples = [
        (
            "What is total revenue by product category?",
            "SELECT CATEGORY, SUM(REVENUE) AS total_revenue FROM main_marts.fct_orders GROUP BY CATEGORY ORDER BY total_revenue DESC",
        ),
        (
            "What is total revenue for completed orders only?",
            "SELECT SUM(REVENUE) AS total_revenue FROM main_marts.fct_orders WHERE ORDER_STATUS = 'completed'",
        ),
        (
            "Who are the top 5 customers by lifetime value?",
            "SELECT NAME, CUSTOMER_LIFETIME_VALUE FROM main_marts.dim_customers ORDER BY CUSTOMER_LIFETIME_VALUE DESC LIMIT 5",
        ),
        (
            "How many orders were placed per country?",
            "SELECT COUNTRY_CODE, COUNT(ORDER_ID) AS order_count FROM main_marts.fct_orders GROUP BY COUNTRY_CODE ORDER BY order_count DESC",
        ),
        (
            "What is total revenue in the last year?",
            "SELECT SUM(REVENUE) AS revenue_last_year FROM main_marts.fct_orders WHERE ORDER_DATE >= (SELECT MAX(ORDER_DATE) FROM main_marts.fct_orders) - INTERVAL '1 year'",
        ),
    ]
    for question, sql in examples:
        vn.train(question=question, sql=sql)
        print(f"[trained] example: {question}")

    print("\n[done] Training complete. ChromaDB is ready.")


if __name__ == "__main__":
    print("Setting up Vanna with Ollama (llama3.1) + ChromaDB...\n")
    vn = get_vanna()
    train(vn)