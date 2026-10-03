#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

for cmd in uv npm docker; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "ERROR: '$cmd' belum tersedia di PATH." >&2
    exit 1
  fi
done

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

if [[ ! -f apps/backend/.env ]]; then
  cp apps/backend/.env.example apps/backend/.env
  echo "Created apps/backend/.env"
fi

if [[ ! -f apps/frontend/.env ]]; then
  cp apps/frontend/.env.example apps/frontend/.env
  echo "Created apps/frontend/.env"
fi

echo "==> Installing backend dependencies and generating uv.lock"
(
  cd apps/backend
  uv sync
)

echo "==> Installing frontend dependencies and generating package-lock.json"
(
  cd apps/frontend
  npm install
)

echo "==> Starting PostgreSQL"
docker compose -f compose.dev.yml up -d

echo
cat <<'EOF'
Bootstrap selesai.

IMPORTANT:
1. Review local .env values.
2. Commit apps/backend/uv.lock and apps/frontend/package-lock.json after they are generated.
3. Run backend:  make backend-dev
4. Run frontend: make frontend-dev
5. Verify:       make phase0-check
EOF
