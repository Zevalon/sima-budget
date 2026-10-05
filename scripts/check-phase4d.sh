#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[Phase 4D] Running Phase 4C regression gate..."
./scripts/check-phase4c.sh

echo "[Phase 4D] Refreshing bootstrap permissions and role templates..."
cd apps/backend
uv run python -m scripts.bootstrap_foundation

echo "[Phase 4D] Verifying realization workflow identity, scope, and aggregate consistency..."
uv run python -m scripts.verify_phase4d

cd "$ROOT_DIR"
echo
echo "Phase 4D checks passed."
