#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[Phase 3A] Running Phase 2D regression gate..."
./scripts/check-phase2d.sh

echo "[Phase 3A] Applying latest database migration..."
cd apps/backend
uv run alembic upgrade head

echo "[Phase 3A] Refreshing bootstrap permissions and role templates..."
uv run python -m scripts.bootstrap_foundation

echo "[Phase 3A] Verifying budget plan core, scoped access, and versioned items..."
uv run python -m scripts.verify_phase3a

cd "$ROOT_DIR"
echo
echo "Phase 3A checks passed."
