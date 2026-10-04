#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[Phase 4A] Running Phase 3D regression gate..."
./scripts/check-phase3d.sh

echo "[Phase 4A] Applying latest database migration..."
cd apps/backend
uv run alembic upgrade head

echo "[Phase 4A] Refreshing bootstrap permissions and role templates..."
uv run python -m scripts.bootstrap_foundation

echo "[Phase 4A] Verifying realization core, scope, and strict posting limits..."
uv run python -m scripts.verify_phase4a

cd "$ROOT_DIR"
echo
echo "Phase 4A checks passed."
