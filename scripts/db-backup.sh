#!/usr/bin/env bash
set -euo pipefail

DB_CONTAINER="${DB_CONTAINER:-etp-postgres}"
DB_NAME="${DB_NAME:-telemetry}"
DB_USER="${DB_USER:-etp}"
BACKUP_DIR="${BACKUP_DIR:-backups}"

# Keep backups in the repository regardless of the caller's working directory.
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$REPO_ROOT/$BACKUP_DIR"
backup_file="$REPO_ROOT/$BACKUP_DIR/$DB_NAME-$(date +%Y%m%d-%H%M%S).dump"

trap 'rm -f "$backup_file"' ERR

podman exec "$DB_CONTAINER" \
    pg_dump -U "$DB_USER" -d "$DB_NAME" -Fc \
    > "$backup_file"

trap - ERR
echo "Database backup created: $backup_file"
