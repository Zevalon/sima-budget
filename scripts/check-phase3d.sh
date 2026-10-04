#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[Phase 3D] Running Phase 3C regression gate..."
./scripts/check-phase3c.sh

echo "[Phase 3D] Applying latest database migration..."
cd apps/backend
uv run alembic upgrade head

echo "[Phase 3D] Refreshing bootstrap permissions and role templates..."
uv run python -m scripts.bootstrap_foundation

echo "[Phase 3D] Verifying workflow identity, stale-action guards, and scoped summaries..."
uv run python -m scripts.verify_phase3d

cd "$ROOT_DIR"
echo
echo "Phase 3D checks passed."
