"""
Central configuration: every path and tunable lives here.

Values can be overridden with environment variables (or a `.env` file at the
project root), so nothing else in the codebase hard-codes a location.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Local (editable) install: src/sql_query_agent/config.py -> root is two levels up.
# Non-editable install (e.g. Docker) the package lives in site-packages, so the
# root must be given explicitly with SQA_PROJECT_ROOT.
PROJECT_ROOT = Path(os.getenv("SQA_PROJECT_ROOT") or Path(__file__).resolve().parents[2])

load_dotenv(PROJECT_ROOT / ".env")


def _path(env_var: str, default: Path) -> Path:
    value = os.getenv(env_var)
    return Path(value).expanduser().resolve() if value else default


@dataclass(frozen=True)
class Settings:
    # -- Data ----------------------------------------------------------------
    raw_dir: Path = _path("SQA_RAW_DIR", PROJECT_ROOT / "data" / "raw")
    warehouse_path: Path = _path(
        "SQA_WAREHOUSE_PATH", PROJECT_ROOT / "data" / "warehouse" / "warehouse.duckdb"
    )

    # -- dbt -----------------------------------------------------------------
    dbt_project_dir: Path = PROJECT_ROOT / "dbt_project"
    semantic_layer_path: Path = PROJECT_ROOT / "dbt_project" / "semantic" / "semantic_layer.yml"
    marts_schema: str = "main_marts"
    mart_tables: tuple[str, ...] = ("fct_orders", "dim_customers", "dim_products")

    # -- AI layer ------------------------------------------------------------
    vector_store_path: Path = _path("SQA_VECTOR_STORE_PATH", PROJECT_ROOT / "data" / "vector_store")
    ollama_model: str = os.getenv("SQA_OLLAMA_MODEL", "llama3.1")
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    # CPU-only inference (e.g. Docker without GPU) can take minutes per question;
    # Vanna's own default (240 s) is too short for that.
    ollama_timeout: float = float(os.getenv("SQA_OLLAMA_TIMEOUT", "600"))
    # Keep the model loaded between questions (Ollama unloads it after 5 min by
    # default, and reloading ~5 GB on CPU takes minutes).
    ollama_keep_alive: str = os.getenv("SQA_OLLAMA_KEEP_ALIVE", "1h")


settings = Settings()
