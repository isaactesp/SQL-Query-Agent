"""Vanna client: ChromaDB (vector store) + Ollama (LLM), connected to DuckDB."""

from __future__ import annotations

from vanna.chromadb import ChromaDB_VectorStore
from vanna.ollama import Ollama

from sql_query_agent.config import settings


class VannaEcommerce(ChromaDB_VectorStore, Ollama):
    def __init__(self, config: dict | None = None):
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)


def get_vanna() -> VannaEcommerce:
    vn = VannaEcommerce(
        config={
            "model": settings.ollama_model,
            "ollama_host": settings.ollama_host,
            "ollama_timeout": settings.ollama_timeout,
            "keep_alive": settings.ollama_keep_alive,
            "path": str(settings.vector_store_path),
        }
    )
    vn.connect_to_duckdb(url=str(settings.warehouse_path))
    return vn
