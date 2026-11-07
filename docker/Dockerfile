# syntax=docker/dockerfile:1

# --- Builder: compiles chroma-hnswlib (no py3.12 Linux wheel) ---
FROM python:3.12-slim-bookworm AS builder

COPY --from=ghcr.io/astral-sh/uv:0.12.6 /uv /usr/local/bin/

RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential \
 && rm -rf /var/lib/apt/lists/*

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY README.md ./
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

# --- Runtime: just the venv + dbt project, no compiler ---
FROM python:3.12-slim-bookworm

ENV PATH="/app/.venv/bin:$PATH" \
    SQA_PROJECT_ROOT=/app \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true

RUN useradd --create-home --uid 1000 app

WORKDIR /app

COPY --from=builder --chown=app:app /app/.venv .venv
COPY --chown=app:app dbt_project dbt_project
COPY --chmod=755 docker/entrypoint.sh /usr/local/bin/

RUN mkdir -p data && chown app:app /app data

USER app

EXPOSE 8501
ENTRYPOINT ["entrypoint.sh"]
CMD ["sql-query-agent", "ui"]
