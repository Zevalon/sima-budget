#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[Phase 4C] Running Phase 4B regression gate..."
./scripts/check-phase4b.sh

echo "[Phase 4C] Refreshing bootstrap permissions and role templates..."
cd apps/backend
uv run python -m scripts.bootstrap_foundation

echo "[Phase 4C] Verifying realization aggregates, monitoring, and concurrency safety..."
uv run python -m scripts.verify_phase4c

cd "$ROOT_DIR"
echo
echo "Phase 4C checks passed."
