#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[Phase 5D] Running Phase 5C regression gate..."
./scripts/check-phase5c.sh

echo "[Phase 5D] Refreshing bootstrap permissions and role templates..."
cd apps/backend
uv run python -m scripts.bootstrap_foundation

echo "[Phase 5D] Verifying reporting hardening and historical safety..."
uv run python -m scripts.verify_phase5d

cd "$ROOT_DIR"
echo
echo "Phase 5D checks passed."
