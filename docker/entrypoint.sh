#!/usr/bin/env sh
# Builds the warehouse (generate -> ingest -> dbt build) and trains the vector
# store when the container is created. They live in the container filesystem
# (no volume), so a recreated container (`up --build`, `down`) always rebuilds
# them from the current image; a plain `stop`/`start` keeps them and skips this.
set -e

WAREHOUSE=/app/data/warehouse/warehouse.duckdb
# Marker written only after training succeeds: chroma.sqlite3 alone is not
# enough, it is created as soon as training starts, even if it then fails.
TRAINED=/app/data/vector_store/.trained

if [ ! -f "$WAREHOUSE" ]; then
    echo "[entrypoint] No warehouse found -> generate + ingest + dbt build..."
    sql-query-agent generate
    sql-query-agent ingest
    sql-query-agent transform
fi

if [ ! -f "$TRAINED" ]; then
    echo "[entrypoint] Vector store not trained -> training..."
    sql-query-agent train
    touch "$TRAINED"
fi

exec "$@"
