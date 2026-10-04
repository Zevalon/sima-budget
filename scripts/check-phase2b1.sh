#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[Phase 2B1] Running Phase 2A regression gate..."
./scripts/check-phase2a.sh

echo "[Phase 2B1] Applying latest database migration..."
cd apps/backend
uv run alembic upgrade head

echo "[Phase 2B1] Refreshing bootstrap permissions and role templates..."
uv run python -m scripts.bootstrap_foundation

echo "[Phase 2B1] Verifying annual budget core and submission workflow..."
uv run python -m scripts.verify_phase2b1

printf '\nPhase 2B1 checks passed.\n'
