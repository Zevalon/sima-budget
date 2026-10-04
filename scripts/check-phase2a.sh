#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[Phase 2A] Running Phase 1D2 regression gate..."
./scripts/check-phase1d2.sh

echo "[Phase 2A] Applying latest database migration..."
(cd apps/backend && uv run alembic upgrade head)

echo "[Phase 2A] Refreshing bootstrap permissions and role templates..."
(cd apps/backend && uv run python -m scripts.bootstrap_foundation)

echo "[Phase 2A] Verifying fiscal year lifecycle and master data..."
(cd apps/backend && uv run python -m scripts.verify_phase2a)

echo
echo "Phase 2A checks passed."
