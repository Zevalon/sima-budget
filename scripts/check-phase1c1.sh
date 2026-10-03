#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[Phase 1C1] Running Phase 1B regression gate..."
./scripts/check-phase1b.sh

echo "[Phase 1C1] Verifying RBAC and administration read API..."
(cd apps/backend && uv run python -m scripts.verify_admin_api)

echo
echo "Phase 1C1 checks passed."
