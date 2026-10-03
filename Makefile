.PHONY: help bootstrap dev-db-up dev-db-down dev-db-status backend-dev frontend-dev lint typecheck test backend-test frontend-test openapi phase0-check

help:
	@echo "SIMA development commands"
	@echo "  make bootstrap       Bootstrap local development dependencies"
	@echo "  make dev-db-up       Start PostgreSQL development container"
	@echo "  make dev-db-down     Stop PostgreSQL development container"
	@echo "  make backend-dev     Run FastAPI hot reload"
	@echo "  make frontend-dev    Run Vite dev server"
	@echo "  make lint            Backend + frontend lint/format checks"
	@echo "  make typecheck       Backend + frontend type checks"
	@echo "  make test            Backend + frontend tests"
	@echo "  make openapi         Export OpenAPI schema"
	@echo "  make phase0-check    Run Phase 0 local checks"

bootstrap:
	./scripts/bootstrap-dev.sh

dev-db-up:
	docker compose -f compose.dev.yml up -d

dev-db-down:
	docker compose -f compose.dev.yml down

dev-db-status:
	docker compose -f compose.dev.yml ps

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
	cd apps/backend && uv run python scripts/export_openapi.py ../../../docs/api/openapi.json

phase0-check:
	./scripts/check-phase0.sh
