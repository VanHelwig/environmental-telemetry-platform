#!/usr/bin/env bash
set -euo pipefail

DB_CONTAINER="${DB_CONTAINER:-etp-postgres}"
DB_IMAGE="${DB_IMAGE:-docker.io/postgis/postgis:17-3.5}"
DB_VOLUME="${DB_VOLUME:-etp-postgres-data}"
DB_NETWORK="${DB_NETWORK:-kind}"
DB_NAME="${DB_NAME:-telemetry}"
DB_USER="${DB_USER:-etp}"
DB_PORT="${DB_PORT:-5432}"

if [[ -z "${POSTGRES_PASSWORD:-}" ]]; then
    echo "Error: POSTGRES_PASSWORD is not configured" >&2
    exit 1
fi

podman run -d \
    --name "$DB_CONTAINER" \
    --network "$DB_NETWORK" \
    -e POSTGRES_USER="$DB_USER" \
    -e POSTGRES_PASSWORD \
    -e POSTGRES_DB="$DB_NAME" \
    -p "127.0.0.1:$DB_PORT:5432" \
    -v "$DB_VOLUME:/var/lib/postgresql/data" \
    "$DB_IMAGE"
