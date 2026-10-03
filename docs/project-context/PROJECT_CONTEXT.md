# PROJECT CONTEXT — SIMA through CP-05

## Project
SIMA — Sistem Informasi Monitoring Anggaran.

Default name is configurable from Application Settings.

Initial target is a private university, but domain is intentionally generic for other organizations.

## Product Scope
Annual budget:
Fiscal Year
→ Annual Budget
→ Unit Allocation
→ Budget Plan
→ Plan Items
→ Approval
→ Realization
→ Monitoring/Reporting.

Not an accounting/GL, procurement, payroll, SIAKAD, or ERP replacement.

## Technology
Frontend:
React + TypeScript + Vite.

Backend:
FastAPI + Python 3.14 baseline.

Database:
PostgreSQL.

Architecture:
Modular monolith + monorepo.

Dev infrastructure:
Docker Compose.

Redis:
not part of V1 until a real need exists.

## Auth
Server-side opaque sessions using HttpOnly cookies.
CSRF protection for unsafe cookie-authenticated requests.
Argon2id password hashing.
No auth token in localStorage.

## Authorization
RBAC + scope:
OWN
OWN_UNIT
OWN_UNIT_AND_CHILDREN
ALL.

System Administrator is separate from financial authority.

## Core Financial Rules
- Annual Budget cannot be silently overwritten after approval.
- Approved Plan cannot be silently edited.
- Revision retains history.
- Allocation <= Annual Budget.
- Approved commitments <= Unit Allocation.
- Realization <= approved plan by default.
- Draft Plan does not reserve official balance.
- Final Plan approval creates commitment.
- Financial constraints are rechecked inside DB transaction.
- Processed financial documents are not hard-deleted.
- Audit trail covers critical financial/security changes.

## UI/UX
Desktop-first responsive.
Sidebar + topbar.
Global Fiscal Year context.
Role-aware dashboards.
Multi-step Plan form.
Approval Inbox.
Separate workflow/execution statuses.
Tree organization management.
Server-side tables.
Explicit loading/empty/error/conflict states.
Configurable branding.

## Engineering Baseline
Monorepo:
apps/backend
apps/frontend
docs
test-cases
logs/testing
.github
docker/scripts.

Backend:
SQLAlchemy 2 async, psycopg 3, Alembic, Pydantic.
Ruff + mypy + pytest.

Frontend:
React Router, TanStack Query, RHF, Zod, TanStack Table, Tailwind, Radix/shadcn-style primitives.
Vitest + RTL + MSW + Playwright.
OpenAPI generated TypeScript contract.

## Environment
Development
Test
Staging recommended
Production

Each has isolated database/secrets/storage.

## Database
PostgreSQL integration tests.
No SQLite as primary integration substitute.
Alembic required for all schema changes.

## CI
Backend lint/type/migration/test.
Frontend lint/format/type/test/build.
OpenAPI contract freshness.
Critical E2E.
Security/dependency checks.

## Documentation
CP-01: Requirement & Business Rules — COMPLETE
CP-02: Data Model & ERD — COMPLETE
CP-03: Architecture & API — COMPLETE
CP-04: UI/UX & Navigation — COMPLETE
CP-05: Development Readiness — COMPLETE

## Current Project Status
**READY FOR IMPLEMENTATION**

## Next Work
Implementation Phase 0:
Repository & Tooling Scaffold.

The first implementation should create the real repository structure and runnable skeleton, not financial features yet.

Exit criteria:
- clean clone starts;
- PostgreSQL works;
- backend health works;
- frontend shell loads;
- formatting/lint/type/test commands work;
- CI skeleton exists;
- docs/checkpoints are copied into repository;
- `.env.example` exists;
- no secrets are committed.

## Recovery Rule
If chat context is lost:
1. read PROJECT_CONTEXT;
2. read CP-01 through CP-05;
3. continue from current implementation phase;
4. do not silently change baseline business/architecture decisions.
