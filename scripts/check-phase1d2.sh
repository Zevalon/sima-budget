#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[Phase 1D2] Running Phase 1D1 regression gate..."
./scripts/check-phase1d1.sh

echo "[Phase 1D2] Verifying foundation hardening..."
(cd apps/backend && uv run python -m scripts.verify_foundation_hardening)

echo
echo "Phase 1D2 checks passed."
