"""
Question -> SQL -> result. Requires the vector store to be trained first
(`sql-query-agent train`).
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from sql_query_agent.agent.vanna_client import VannaEcommerce, get_vanna


@dataclass
class QueryResult:
    question: str
    sql: str
    data: pd.DataFrame


def ask(question: str, vn: VannaEcommerce | None = None) -> QueryResult:
    vn = vn or get_vanna()
    sql = vn.generate_sql(question)
    data = vn.run_sql(sql)
    return QueryResult(question=question, sql=sql, data=data)


def main(question: str | None = None) -> None:
    question = question or input("Ask a question: ")
    result = ask(question)
    print(f"\nQuestion: {result.question}\n{'-' * 60}")
    print(f"Generated SQL:\n{result.sql}\n")
    print("Result:")
    print(result.data.to_string(index=False))


if __name__ == "__main__":
    main()
