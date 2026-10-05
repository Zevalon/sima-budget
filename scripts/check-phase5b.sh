#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[Phase 5B] Running Phase 5A regression gate..."
./scripts/check-phase5a.sh

echo "[Phase 5B] Refreshing bootstrap permissions and role templates..."
cd apps/backend
uv run python -m scripts.bootstrap_foundation

echo "[Phase 5B] Verifying scoped server-side report filters..."
uv run python -m scripts.verify_phase5b

cd "$ROOT_DIR"
echo
echo "Phase 5B checks passed."
