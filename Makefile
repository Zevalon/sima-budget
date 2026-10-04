.PHONY: help bootstrap dev-db-up dev-db-down dev-db-status backend-dev frontend-dev lint typecheck test backend-test frontend-test openapi foundation-bootstrap foundation-verify bootstrap-admin phase0-check phase1a-check phase1b-check phase1c1-check phase1c2-check phase1d1-check

help:
	@echo "SIMA development commands"
	@echo "  make bootstrap              Bootstrap local development dependencies"
	@echo "  make dev-db-up              Start PostgreSQL development container"
	@echo "  make dev-db-down            Stop PostgreSQL development container"
	@echo "  make dev-db-status          Show PostgreSQL development status"
	@echo "  make backend-dev            Run FastAPI hot reload"
	@echo "  make frontend-dev           Run Vite dev server"
	@echo "  make lint                   Backend + frontend lint/format checks"
	@echo "  make typecheck              Backend + frontend type checks"
	@echo "  make test                   Backend + frontend tests"
	@echo "  make openapi                Export OpenAPI schema"
	@echo "  make foundation-bootstrap   Seed idempotent foundation data"
	@echo "  make foundation-verify      Verify foundation data"
	@echo "  make bootstrap-admin        Create/reset the first System Administrator"
	@echo "  make phase0-check           Run Phase 0 local checks"
	@echo "  make phase1a-check          Run Phase 0 regression + Phase 1A checks"
	@echo "  make phase1b-check          Run Phase 1A regression + authentication checks"
	@echo "  make phase1c1-check         Run Phase 1B regression + RBAC/admin API checks"
	@echo "  make phase1c2-check         Run Phase 1C1 regression + admin mutation checks"
	@echo "  make phase1d1-check         Run Phase 1C2 regression + settings/audit checks"

bootstrap:
	./scripts/bootstrap-dev.sh

dev-db-up:
	docker compose --env-file .env -f compose.dev.yml up -d

dev-db-down:
	docker compose --env-file .env -f compose.dev.yml down

dev-db-status:
	docker compose --env-file .env -f compose.dev.yml ps

backend-dev:
	cd apps/backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend-dev:
	cd apps/frontend && npm run dev -- --host 0.0.0.0

lint:
	cd apps/backend && uv run ruff check . && uv run ruff format --check .
	cd apps/frontend && npm run lint && npm run format:check

typecheck:
	cd apps/backend && uv run mypy app tests
	cd apps/frontend && npm run typecheck

test: backend-test frontend-test

backend-test:
	cd apps/backend && uv run python -m pytest

frontend-test:
	cd apps/frontend && npm run test

openapi:
	cd apps/backend && uv run python scripts/export_openapi.py ../../docs/api/openapi.json

foundation-bootstrap:
	cd apps/backend && uv run python -m scripts.bootstrap_foundation

foundation-verify:
	cd apps/backend && uv run python -m scripts.verify_foundation

bootstrap-admin:
	cd apps/backend && uv run python -m scripts.bootstrap_admin

phase0-check:
	./scripts/check-phase0.sh

phase1a-check:
	./scripts/check-phase1a.sh

phase1b-check:
	./scripts/check-phase1b.sh

phase1c1-check:
	./scripts/check-phase1c1.sh

phase1c2-check:
	./scripts/check-phase1c2.sh

phase1d1-check:
	./scripts/check-phase1d1.sh
