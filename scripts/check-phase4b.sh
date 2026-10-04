#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[Phase 4B] Running Phase 4A regression gate..."
./scripts/check-phase4a.sh

echo "[Phase 4B] Applying latest database migration..."
cd apps/backend
uv run alembic upgrade head

echo "[Phase 4B] Refreshing bootstrap permissions and role templates..."
uv run python -m scripts.bootstrap_foundation

echo "[Phase 4B] Verifying cancellation, reversal, and correction workflow..."
uv run python -m scripts.verify_phase4b

cd "$ROOT_DIR"
echo
echo "Phase 4B checks passed."
