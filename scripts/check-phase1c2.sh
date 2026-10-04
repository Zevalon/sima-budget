#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[Phase 1C2] Running Phase 1C1 regression gate..."
./scripts/check-phase1c1.sh

echo "[Phase 1C2] Verifying administration write operations..."
(cd apps/backend && uv run python -m scripts.verify_admin_mutations)

echo
echo "Phase 1C2 checks passed."
