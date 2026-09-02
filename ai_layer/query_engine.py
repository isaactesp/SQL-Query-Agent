"""
query_engine.py
---------------
Ask a plain-English business question and get back a SQL result.
Requires setup.py to have been run first (trains ChromaDB).

Run with:  python ai_layer/query_engine.py
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from setup import get_vanna


def ask(question: str) -> None:
    vn = get_vanna()

    print(f"\nQuestion: {question}")
    print("-" * 60)

    sql = vn.generate_sql(question)
    print(f"Generated SQL:\n{sql}\n")

    result = vn.run_sql(sql)
    print("Result:")
    print(result.to_string(index=False))


if __name__ == "__main__":
    question = input("Ask a question: ")
    ask(question)