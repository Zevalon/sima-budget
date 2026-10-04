#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[Phase 3C] Running Phase 3B regression gate..."
./scripts/check-phase3b.sh

echo "[Phase 3C] Applying latest database migration..."
cd apps/backend
uv run alembic upgrade head

echo "[Phase 3C] Refreshing bootstrap permissions and role templates..."
uv run python -m scripts.bootstrap_foundation

echo "[Phase 3C] Verifying commitment, available budget, and concurrent approval safety..."
uv run python -m scripts.verify_phase3c

cd "$ROOT_DIR"
echo
echo "Phase 3C checks passed."
