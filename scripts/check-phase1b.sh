#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[Phase 1B] Running Phase 1A regression gate..."
./scripts/check-phase1a.sh

echo "[Phase 1B] Verifying login/session/CSRF flow..."
(cd apps/backend && uv run python -m scripts.verify_auth_flow)

echo
echo "Phase 1B checks passed."
