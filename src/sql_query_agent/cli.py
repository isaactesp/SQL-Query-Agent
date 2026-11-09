"""
Single entry point for the whole pipeline.

    sql-query-agent generate    # synthetic CSVs          -> data/raw/
    sql-query-agent ingest      # CSVs -> DuckDB raw schema
    sql-query-agent transform   # dbt build (run + test)
    sql-query-agent train       # train the Vanna vector store
    sql-query-agent ask "..."   # question -> SQL -> result
    sql-query-agent ui          # Streamlit app
    sql-query-agent pipeline    # generate + ingest + transform + train
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from sql_query_agent.config import settings


def _run(cmd: list[str], env: dict | None = None) -> None:
    print(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, check=True, env=env)


def cmd_generate(_: argparse.Namespace) -> None:
    from sql_query_agent.data.generate import main

    main()


def cmd_ingest(_: argparse.Namespace) -> None:
    from sql_query_agent.data.ingest import main

    main()


def cmd_transform(_: argparse.Namespace) -> None:
    project_dir = str(settings.dbt_project_dir)
    env = {**os.environ, "SQA_WAREHOUSE_PATH": str(settings.warehouse_path)}
    _run(["dbt", "build", "--project-dir", project_dir, "--profiles-dir", project_dir], env=env)


def cmd_train(_: argparse.Namespace) -> None:
    from sql_query_agent.agent.training import main

    main()


def cmd_ask(args: argparse.Namespace) -> None:
    from sql_query_agent.agent.query_engine import main

    main(" ".join(args.question) if args.question else None)


def cmd_ui(_: argparse.Namespace) -> None:
    app = Path(__file__).parent / "frontend" / "streamlit_app.py"
    _run([sys.executable, "-m", "streamlit", "run", str(app)])


def cmd_pipeline(args: argparse.Namespace) -> None:
    for step in (cmd_generate, cmd_ingest, cmd_transform, cmd_train):
        step(args)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="sql-query-agent",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("generate", help="Generate synthetic raw CSVs").set_defaults(func=cmd_generate)
    sub.add_parser("ingest", help="Load raw CSVs into DuckDB").set_defaults(func=cmd_ingest)
    sub.add_parser("transform", help="Run dbt build (models + tests)").set_defaults(
        func=cmd_transform
    )
    sub.add_parser("train", help="Train the Vanna vector store").set_defaults(func=cmd_train)
    ask = sub.add_parser("ask", help="Ask a question in plain English")
    ask.add_argument("question", nargs="*", help="Question (prompted if omitted)")
    ask.set_defaults(func=cmd_ask)
    sub.add_parser("ui", help="Launch the Streamlit app").set_defaults(func=cmd_ui)
    sub.add_parser("pipeline", help="generate + ingest + transform + train").set_defaults(
        func=cmd_pipeline
    )

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
