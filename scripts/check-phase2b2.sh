#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[Phase 2B2] Running Phase 2B1 regression gate..."
./scripts/check-phase2b1.sh

echo "[Phase 2B2] Refreshing bootstrap permissions and role templates..."
cd apps/backend
uv run python -m scripts.bootstrap_foundation

echo "[Phase 2B2] Verifying annual budget approval and rejection workflow..."
uv run python -m scripts.verify_phase2b2

printf '\nPhase 2B2 checks passed.\n'
