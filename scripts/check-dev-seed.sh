#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[Dev Seed] Starting PostgreSQL development container..."
docker compose --env-file .env -f compose.dev.yml up -d postgres

echo "[Dev Seed] Applying migrations..."
cd apps/backend
uv run alembic upgrade head

echo "[Dev Seed] Verifying deterministic development seed..."
uv run python -m scripts.verify_dev_seed

echo
echo "Development seed checks passed."
