#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[1/6] Repository structure"
for path in apps/backend apps/frontend docs test-cases compose.dev.yml .env; do
  if [[ ! -e "$path" ]]; then
    echo "ERROR: Missing required path: $path" >&2
    exit 1
  fi
done

echo "[2/6] Backend tests"
(cd apps/backend && uv run python -m pytest)

echo "[3/6] Database migration and readiness"

if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker engine tidak aktif. Buka Docker Desktop lalu jalankan ulang." >&2
  exit 1
fi

if ! grep -Eq '^POSTGRES_PASSWORD=.+$' .env; then
  echo "ERROR: POSTGRES_PASSWORD belum diisi di root .env." >&2
  exit 1
fi

echo "Starting PostgreSQL development container..."
docker compose --env-file .env -f compose.dev.yml up -d --force-recreate postgres

echo "Waiting for PostgreSQL to become healthy..."
DB_READY=0
for _ in $(seq 1 30); do
  STATUS="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{end}}' sima-postgres-1 2>/dev/null || true)"

  if [[ "$STATUS" == "healthy" ]]; then
    DB_READY=1
    break
  fi

  RUNNING="$(docker inspect -f '{{.State.Running}}' sima-postgres-1 2>/dev/null || true)"
  RESTARTING="$(docker inspect -f '{{.State.Restarting}}' sima-postgres-1 2>/dev/null || true)"

  if [[ "$RUNNING" == "false" || "$RESTARTING" == "true" ]]; then
    echo "ERROR: PostgreSQL container berhenti/restart. Recent logs:" >&2
    docker compose --env-file .env -f compose.dev.yml logs --tail=80 postgres >&2 || true
    exit 1
  fi

  sleep 2
done

if [[ "$DB_READY" -ne 1 ]]; then
  echo "ERROR: PostgreSQL belum healthy setelah 60 detik." >&2
  docker compose --env-file .env -f compose.dev.yml ps >&2 || true
  docker compose --env-file .env -f compose.dev.yml logs --tail=80 postgres >&2 || true
  exit 1
fi

echo "PostgreSQL readiness: OK"

(cd apps/backend && uv run alembic upgrade head)
(cd apps/backend && uv run python - <<'PY'
import asyncio
from app.core.database import ping_database

if not asyncio.run(ping_database()):
    raise SystemExit("Database readiness check failed")
print("Database application connection: OK")
PY
)

echo "[4/6] Backend lint/type"
(cd apps/backend && uv run ruff check .)
(cd apps/backend && uv run ruff format --check .)
(cd apps/backend && uv run mypy app tests)

echo "[5/6] Frontend checks"
(cd apps/frontend && npm run lint)
(cd apps/frontend && npm run format:check)
(cd apps/frontend && npm run typecheck)
(cd apps/frontend && npm run test)
(cd apps/frontend && npm run build)

echo "[6/6] OpenAPI export"
(cd apps/backend && uv run python scripts/export_openapi.py ../../docs/api/openapi.json)

if [[ ! -s docs/api/openapi.json ]]; then
  echo "ERROR: OpenAPI export tidak ditemukan di docs/api/openapi.json" >&2
  exit 1
fi

echo
echo "Phase 0 checks passed."
