#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[Phase 3B] Running Phase 3A regression gate..."
./scripts/check-phase3a.sh

echo "[Phase 3B] Applying latest database migration..."
cd apps/backend
uv run alembic upgrade head

echo "[Phase 3B] Refreshing bootstrap permissions and role templates..."
uv run python -m scripts.bootstrap_foundation

echo "[Phase 3B] Verifying Budget Plan submission, approval, rejection, and revision..."
uv run python -m scripts.verify_phase3b

cd "$ROOT_DIR"
echo
echo "Phase 3B checks passed."
