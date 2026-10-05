#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[Phase 5A] Running Phase 4D regression gate..."
./scripts/check-phase4d.sh

echo "[Phase 5A] Applying latest database migration..."
cd apps/backend
uv run alembic upgrade head

echo "[Phase 5A] Refreshing bootstrap permissions and role templates..."
uv run python -m scripts.bootstrap_foundation

echo "[Phase 5A] Verifying canonical financial reporting and scoped aggregates..."
uv run python -m scripts.verify_phase5a

cd "$ROOT_DIR"
echo
echo "Phase 5A checks passed."
