#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[Phase 5C] Running Phase 5B regression gate..."
./scripts/check-phase5b.sh

echo "[Phase 5C] Refreshing bootstrap permissions and role templates..."
cd apps/backend
uv run python -m scripts.bootstrap_foundation

echo "[Phase 5C] Verifying CSV, Excel, and PDF report exports..."
uv run python -m scripts.verify_phase5c

cd "$ROOT_DIR"
echo
echo "Phase 5C checks passed."
