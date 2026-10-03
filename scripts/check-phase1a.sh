#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[Phase 1A] Running Phase 0 regression gate first..."
./scripts/check-phase0.sh

echo "[Phase 1A] Applying latest database migration..."
(cd apps/backend && uv run alembic upgrade head)

echo "[Phase 1A] Running foundation bootstrap (pass 1)..."
(cd apps/backend && uv run python -m scripts.bootstrap_foundation)

echo "[Phase 1A] Running foundation bootstrap again to verify idempotency..."
(cd apps/backend && uv run python -m scripts.bootstrap_foundation)

echo "[Phase 1A] Verifying foundation schema and bootstrap data..."
(cd apps/backend && uv run python -m scripts.verify_foundation)

echo
echo "Phase 1A checks passed."
