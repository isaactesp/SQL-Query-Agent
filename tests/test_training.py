import duckdb
import pytest
import yaml

from sql_query_agent.agent.training import build_ddl, build_semantic_docs, load_examples
from sql_query_agent.config import settings


def test_build_ddl_reads_columns_in_order():
    con = duckdb.connect()
    con.execute("CREATE SCHEMA main_marts")
    con.execute("CREATE TABLE main_marts.t (ORDER_ID VARCHAR, REVENUE DOUBLE)")
    ddl = build_ddl(con, "main_marts", "t")
    assert ddl == "CREATE TABLE main_marts.t (\n  ORDER_ID VARCHAR,\n  REVENUE DOUBLE\n);"


def test_build_ddl_missing_table_raises():
    with pytest.raises(ValueError):
        build_ddl(duckdb.connect(), "main_marts", "nope")


def test_semantic_layer_file_produces_docs():
    semantic = yaml.safe_load(settings.semantic_layer_path.read_text(encoding="utf-8"))
    docs = build_semantic_docs(semantic)
    assert any(d.startswith("Table: fct_orders") for d in docs)
    assert any(d.startswith("Metric: total_revenue") for d in docs)


def test_examples_reference_marts_schema():
    examples = load_examples()
    assert examples
    for _question, sql in examples:
        assert settings.marts_schema in sql
