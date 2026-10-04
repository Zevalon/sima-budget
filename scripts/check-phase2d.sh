#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[Phase 2D] Running Phase 2C regression gate..."
./scripts/check-phase2c.sh

echo "[Phase 2D] Refreshing bootstrap permissions and role templates..."
cd apps/backend
uv run python -m scripts.bootstrap_foundation

echo "[Phase 2D] Verifying budget-foundation hardening..."
uv run python -m scripts.verify_phase2d

printf '\nPhase 2D checks passed.\n'
