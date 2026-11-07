"""
Trains the Vanna RAG store on the mart DDL, the semantic layer and a set of
example question -> SQL pairs. Run once (and again whenever the marts, the
semantic layer or the examples change):

    sql-query-agent train
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import duckdb
import yaml

from sql_query_agent.config import settings

if TYPE_CHECKING:
    from sql_query_agent.agent.vanna_client import VannaEcommerce

EXAMPLES_PATH = Path(__file__).with_name("examples.yml")


# -- Pure builders (no LLM / no vector store: easy to unit-test) ----------------
def build_ddl(con: duckdb.DuckDBPyConnection, schema: str, table: str) -> str:
    cols = con.execute(
        """
        SELECT column_name, data_type
        FROM duckdb_columns()
        WHERE table_name = ? AND schema_name = ?
        ORDER BY column_index
        """,
        [table, schema],
    ).fetchall()
    if not cols:
        raise ValueError(
            f"Table {schema}.{table} not found. Did you run `sql-query-agent transform`?"
        )
    body = ",\n".join(f"  {name} {dtype}" for name, dtype in cols)
    return f"CREATE TABLE {schema}.{table} (\n{body}\n);"


def build_semantic_docs(semantic: dict) -> list[str]:
    layer = semantic.get("semantic_layer", {})
    docs: list[str] = []

    for model in layer.get("models", []):
        docs.append(
            f"Table: {model['name']}\n"
            f"Schema: {model.get('schema', settings.marts_schema)}\n"
            f"{model['description']}"
        )
    for metric in layer.get("metrics", []):
        docs.append(
            f"Metric: {metric['name']}\n"
            f"Description: {metric['description']}\n"
            f"Model: {metric['model']}\n"
            f"SQL aggregation: {metric['aggregation']}"
        )
    for dim in layer.get("dimensions", []):
        docs.append(
            f"Dimension: {dim['name']}\n"
            f"Description: {dim['description']}\n"
            f"Model: {dim['model']}\n"
            f"Column: {dim['column']}\n"
            f"Type: {dim['type']}"
        )
    return docs


def load_examples(path: Path = EXAMPLES_PATH) -> list[tuple[str, str]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [(ex["question"], ex["sql"].strip()) for ex in data["examples"]]


# -- Training --------------------------------------------------------------------
def train(vn: VannaEcommerce) -> None:
    # Same config as the connection Vanna already holds: DuckDB refuses a second
    # connection to the same file with a different config (e.g. read_only=True).
    with duckdb.connect(str(settings.warehouse_path)) as con:
        for table in settings.mart_tables:
            vn.train(ddl=build_ddl(con, settings.marts_schema, table))
            print(f"[trained] DDL: {table}")

    semantic = yaml.safe_load(settings.semantic_layer_path.read_text(encoding="utf-8"))
    for doc in build_semantic_docs(semantic):
        vn.train(documentation=doc)
        print(f"[trained] doc: {doc.splitlines()[0]}")

    for question, sql in load_examples():
        vn.train(question=question, sql=sql)
        print(f"[trained] example: {question}")

    print("\n[done] Training complete. Vector store is ready.")


def main() -> None:
    from sql_query_agent.agent.vanna_client import get_vanna

    print(f"Training Vanna (Ollama {settings.ollama_model} + ChromaDB)...\n")
    train(get_vanna())


if __name__ == "__main__":
    main()
