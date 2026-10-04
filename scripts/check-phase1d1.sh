#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[Phase 1D1] Running Phase 1C2 regression gate..."
./scripts/check-phase1c2.sh

echo "[Phase 1D1] Verifying settings and audit administration..."
(cd apps/backend && uv run python -m scripts.verify_foundation_admin)

echo
echo "Phase 1D1 checks passed."
