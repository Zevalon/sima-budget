.PHONY: help bootstrap dev-db-up dev-db-down dev-db-status backend-dev frontend-dev lint typecheck test backend-test frontend-test openapi foundation-bootstrap foundation-verify bootstrap-admin phase0-check phase1a-check phase1b-check phase1c1-check phase1c2-check phase1d1-check phase1d2-check phase2a-check phase2b1-check phase2b2-check phase2c-check phase2d-check phase3a-check phase3b-check phase3c-check phase3d-check phase4a-check phase4b-check dev-seed dev-seed-reset dev-seed-verify

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
	@echo "  make phase1d2-check         Run Phase 1D1 regression + final hardening checks"
	@echo "  make phase2a-check          Run Phase 1 regression + fiscal/master foundation checks"
	@echo "  make phase2b1-check         Run Phase 2A regression + annual budget core checks"
	@echo "  make phase2b2-check         Run Phase 2B1 regression + annual budget approval checks"
	@echo "  make phase2c-check          Run Phase 2B2 regression + unit allocation checks"
	@echo "  make phase2d-check          Run Phase 2C regression + budget foundation hardening"
	@echo "  make phase3a-check          Run Phase 2 regression + Budget Plan core checks"
	@echo "  make phase3b-check          Run Phase 3A regression + Budget Plan approval checks"
	@echo "  make phase3c-check          Run Phase 3B regression + commitment controls"
	@echo "  make phase3d-check          Run Phase 3C regression + Budget Plan hardening"
	@echo "  make phase4a-check          Run Phase 3 regression + Realization core checks"
	@echo "  make phase4b-check          Run Phase 4A regression + correction/reversal checks"
	@echo "  make dev-seed               Refresh deterministic development seed"
	@echo "  make dev-seed-reset         RESET dev data; requires CONFIRM=RESET"
	@echo "  make dev-seed-verify        Verify deterministic development seed"

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

phase1d2-check:
	./scripts/check-phase1d2.sh

phase2a-check:
	./scripts/check-phase2a.sh

phase2b1-check:
	./scripts/check-phase2b1.sh


phase2b2-check:
	./scripts/check-phase2b2.sh

phase2c-check:
	./scripts/check-phase2c.sh

phase2d-check:
	./scripts/check-phase2d.sh

phase3a-check:
	./scripts/check-phase3a.sh

phase3b-check:
	./scripts/check-phase3b.sh

phase3c-check:
	./scripts/check-phase3c.sh

phase3d-check:
	./scripts/check-phase3d.sh

phase4a-check:
	./scripts/check-phase4a.sh

phase4b-check:
	./scripts/check-phase4b.sh

phase4c-check:
	./scripts/check-phase4c.sh

phase4d-check:
	./scripts/check-phase4d.sh

dev-seed:
	$(MAKE) dev-db-up
	cd apps/backend && uv run alembic upgrade head
	cd apps/backend && uv run python -m scripts.seed_dev
	$(MAKE) dev-seed-verify

dev-seed-reset:
	@if [ "$(CONFIRM)" != "RESET" ]; then \
		echo "Refusing destructive reset. Run: make dev-seed-reset CONFIRM=RESET"; \
		exit 2; \
	fi
	$(MAKE) dev-db-up
	cd apps/backend && uv run alembic upgrade head
	cd apps/backend && uv run python -m scripts.seed_dev --reset
	$(MAKE) dev-seed-verify

dev-seed-verify:
	./scripts/check-dev-seed.sh
