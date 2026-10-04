#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[Phase 2C] Running Phase 2B2 regression gate..."
./scripts/check-phase2b2.sh

echo "[Phase 2C] Applying latest database migration..."
cd apps/backend
uv run alembic upgrade head

echo "[Phase 2C] Refreshing bootstrap permissions and role templates..."
uv run python -m scripts.bootstrap_foundation

echo "[Phase 2C] Verifying unit allocation controls and concurrency safety..."
uv run python -m scripts.verify_phase2c

printf '\nPhase 2C checks passed.\n'
