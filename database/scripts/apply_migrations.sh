#!/usr/bin/env bash
# ----------------------------------------------------------------------------
# Apply all database migrations in order. Usage:
#
#   ./database/scripts/apply_migrations.sh [DATABASE_URL]
#
# If DATABASE_URL is omitted, the script falls back to the env var
# DATABASE_URL or the local docker-compose default.
# ----------------------------------------------------------------------------
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DSN="${1:-${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/stridealytics}}"

echo "Applying migrations from $ROOT/database/migrations/ to $DSN"
echo

for f in $(ls "$ROOT/database/migrations/"*.sql | grep -v '_down.sql' | sort); do
    if [[ "$(basename $f)" == *"_down.sql" ]]; then
        continue
    fi
    echo "  -> $(basename $f)"
    psql "$DSN" -v ON_ERROR_STOP=1 -f "$f" >/dev/null
done

echo
echo "All migrations applied."
echo
echo "Verifying schema:"
psql "$DSN" -c "\dt" -c "\dv"
