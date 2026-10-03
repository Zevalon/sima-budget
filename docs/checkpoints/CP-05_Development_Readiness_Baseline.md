# CP-05 — Development Readiness Baseline

**Project:** SIMA — Sistem Informasi Monitoring Anggaran  
**Checkpoint:** CP-05  
**Status:** BASELINE / IMPLEMENTATION GATE  
**Purpose:** Mengunci standar engineering dan urutan implementasi sebelum source code V1 dibuat.

---

## 1. Tujuan

CP-05 memastikan development dimulai dengan fondasi yang konsisten, dapat diuji, dapat direview, dan aman untuk dikembangkan jangka panjang.

Checkpoint ini mengunci:

- struktur repository;
- dependency strategy;
- coding standards;
- environment strategy;
- Docker Compose;
- database migration;
- bootstrap/seed;
- authentication/security baseline;
- testing strategy;
- CI;
- logging/health checks;
- documentation;
- test-case/log structure;
- Definition of Done;
- implementation roadmap;
- release readiness.

---

## 2. Final Technology Baseline

### Frontend
- React
- TypeScript
- Vite
- React Router
- TanStack Query
- React Hook Form
- Zod
- TanStack Table
- Tailwind CSS
- Radix UI primitives / shadcn-style generated components where useful
- Lucide icons
- Recharts for standard dashboards
- `openapi-typescript` + typed OpenAPI client

### Backend
- Python 3.14 baseline
- FastAPI
- Pydantic v2 family
- SQLAlchemy 2.x
- PostgreSQL
- psycopg 3 async driver
- Alembic
- Argon2id password hashing
- server-side opaque sessions
- structured logging
- OpenAPI as API contract

### Infrastructure
- Docker / Docker Compose
- PostgreSQL container for local development
- file storage abstraction
- local filesystem storage in development
- production storage can be local managed volume or S3-compatible implementation later
- Redis intentionally deferred

### Engineering Tooling
Backend:
- Ruff lint + format
- mypy
- pytest
- pytest-asyncio
- httpx

Frontend:
- ESLint
- Prettier
- TypeScript compiler
- Vitest
- React Testing Library
- MSW
- Playwright

### Dependency Rule

Exact versions are pinned by lock files at scaffold time.

Do not depend on floating `latest` in production/development lock files.

Major dependency upgrades are explicit engineering changes and require:
1. changelog review;
2. tests;
3. migration review where relevant;
4. checkpoint/ADR update if architectural behavior changes.

---

## 3. Monorepo Structure

```text
sima-budget/
├── apps/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   ├── core/
│   │   │   ├── modules/
│   │   │   ├── shared/
│   │   │   └── main.py
│   │   ├── alembic/
│   │   ├── tests/
│   │   ├── scripts/
│   │   ├── pyproject.toml
│   │   ├── alembic.ini
│   │   └── .env.example
│   │
│   └── frontend/
│       ├── src/
│       │   ├── app/
│       │   ├── components/
│       │   ├── features/
│       │   ├── layouts/
│       │   ├── lib/
│       │   ├── routes/
│       │   ├── styles/
│       │   └── types/
│       ├── tests/
│       ├── e2e/
│       ├── package.json
│       ├── package-lock.json
│       └── .env.example
│
├── docs/
│   ├── project-context/
│   ├── checkpoints/
│   ├── architecture/
│   ├── adr/
│   ├── database/
│   ├── api/
│   ├── installation/
│   ├── deployment/
│   ├── testing/
│   ├── security/
│   └── user-guide/
│
├── test-cases/
│   ├── auth/
│   ├── users-rbac/
│   ├── organization/
│   ├── fiscal-year/
│   ├── annual-budget/
│   ├── allocations/
│   ├── plans/
│   ├── approvals/
│   ├── realizations/
│   ├── reports/
│   └── regression/
│
├── logs/
│   └── testing/
│
├── scripts/
├── docker/
├── .github/
│   ├── workflows/
│   ├── pull_request_template.md
│   └── ISSUE_TEMPLATE/
│
├── compose.yml
├── compose.dev.yml
├── .editorconfig
├── .gitignore
├── .env.example
├── Makefile
├── README.md
├── CONTRIBUTING.md
├── SECURITY.md
├── CHANGELOG.md
└── LICENSE
```

---

## 4. Backend Module Structure

Backend remains modular monolith.

Example:

```text
app/modules/budget_plans/
├── api.py
├── models.py
├── schemas.py
├── repository.py
├── service.py
├── permissions.py
├── events.py
├── exceptions.py
└── tests/
```

Rules:

- API/router handles HTTP only.
- Service layer owns business use-cases.
- Repository owns persistence queries.
- SQLAlchemy models do not become API response models directly.
- Pydantic schemas are explicit.
- Authorization is checked before business action.
- Financial invariants are checked again inside database transaction when required.
- Cross-module access should prefer service interfaces rather than direct table manipulation.

---

## 5. Frontend Feature Structure

Frontend is feature-oriented.

Example:

```text
src/features/budget-plans/
├── api/
├── components/
├── hooks/
├── pages/
├── schemas/
├── types/
└── utils/
```

Shared visual primitives go to `src/components/`.

Global infrastructure goes to `src/app/` and `src/lib/`.

Do not create one global folder containing hundreds of unrelated hooks/services.

---

## 6. API Contract Strategy

FastAPI OpenAPI is the canonical HTTP contract.

Development flow:

```text
Backend schema
→ OpenAPI
→ generated TypeScript API types/client
→ frontend
```

Rules:

- generated API types are not manually edited;
- CI checks generated contract is not stale;
- breaking API changes require explicit review;
- API V1 uses `/api/v1`;
- error envelope is consistent.

---

## 7. Environment Strategy

Environments:

- Development
- Test
- Staging (recommended before production)
- Production

Each environment has separate:
- database;
- secrets;
- file storage;
- session configuration.

Production data is never copied casually into development.

If production-derived data is needed for debugging, it must be anonymized.

---

## 8. Environment Variables

### Root / Compose
Example categories:

```text
COMPOSE_PROJECT_NAME
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_PORT
BACKEND_PORT
FRONTEND_PORT
```

### Backend
Typical:

```text
APP_ENV
APP_NAME
APP_DEBUG
DATABASE_URL
SESSION_COOKIE_NAME
SESSION_SECRET
SESSION_TTL_SECONDS
CSRF_SECRET
FRONTEND_ORIGIN
TRUSTED_HOSTS
FILE_STORAGE_DRIVER
FILE_STORAGE_PATH
MAX_UPLOAD_SIZE_MB
LOG_LEVEL
```

Optional later:

```text
SMTP_*
S3_*
SENTRY_DSN
```

### Frontend

Only public values:

```text
VITE_APP_ENV
VITE_API_BASE_URL
```

Never put secrets in `VITE_*`.

All `.env` files containing secrets are gitignored.
Only `.env.example` is committed.

---

## 9. Docker Development Strategy

Default developer workflow:

```text
Docker Compose:
- PostgreSQL

WSL:
- backend hot reload
- frontend dev server
```

This reduces container overhead on the user's development device.

Full-container workflow must also remain available for CI/staging consistency.

Compose services baseline:

```text
postgres
backend
frontend
```

Optional profiles later:

```text
mailpit
reverse-proxy
```

Redis is not added without an actual use-case.

---

## 10. Database Migration Policy

Alembic is mandatory.

Rules:

1. No manual production schema changes.
2. Every schema change has a migration.
3. Migration files are committed.
4. Migration is reviewed with code.
5. Migrations should be forward-safe.
6. Destructive migrations require explicit backup/rollout plan.
7. Development reset is allowed only for local dev data.
8. Staging/production migrations run before application traffic uses new schema when required.

CI runs:

```text
alembic upgrade head
```

against a clean PostgreSQL test database.

A migration graph with multiple accidental heads fails CI.

---

## 11. Seed and Bootstrap Strategy

Separate concepts:

### System Bootstrap
Idempotent and safe to run repeatedly.

Creates:
- permission catalog;
- default role templates;
- default application settings;
- base workflow templates where appropriate;
- document-number pattern defaults.

### Development Seed
Development only.

Creates:
- sample organization;
- units;
- users;
- annual budget;
- allocations;
- sample plans.

Never runs automatically in production.

### First Administrator

No committed default password.

Production administrator is created through an explicit bootstrap command, for example:

```text
make bootstrap-admin
```

or backend CLI with prompted/secure credentials.

---

## 12. Authentication Baseline

- Opaque random session ID.
- Session persisted server-side.
- Browser receives session through HttpOnly cookie.
- `Secure` in production.
- `SameSite=Lax` baseline.
- Session rotation after authentication/security-sensitive changes.
- Logout invalidates server session.
- Password hashing: Argon2id.
- Password reset tokens are single-use and expire.
- Account inactive state immediately prevents new access.
- Session revocation supported.

No auth token stored in `localStorage`.

---

## 13. CSRF Baseline

Because browser authentication uses cookies:

- unsafe methods require CSRF protection;
- GET/HEAD remain non-mutating;
- CSRF token is distinct from session ID;
- frontend API layer sends token on protected mutations;
- same-origin deployment is preferred;
- CORS allowlist is restrictive.

---

## 14. Authorization Baseline

Every sensitive backend action evaluates:

```text
Authenticated user
+ Permission
+ Scope
+ Entity state
+ Business rule
```

Never rely only on frontend route guards.

Example:

```text
plan.approve + OWN_UNIT
```

does not authorize approval of another unit.

Self-approval rule is independently checked.

---

## 15. File Upload Security

Baseline:

- allowlist MIME/extensions;
- maximum upload size;
- generated storage name, not trusted raw filename;
- preserve original display name as metadata;
- path traversal prevention;
- access through authorized application endpoint where needed;
- file metadata stored in database;
- attachment operations audited when sensitive.

Future production deployment may add antivirus scanning.

---

## 16. Backend Coding Standards

### Python
- type annotations on public service/repository interfaces;
- async database flow consistently;
- Ruff formatting;
- no wildcard imports;
- no broad `except Exception` without rethrow/log rationale;
- domain exceptions map centrally to HTTP errors;
- UTC timestamps in database;
- monetary values use Decimal/NUMERIC;
- UUID/opaque identifiers for internal public IDs;
- business document number is separate from primary ID.

Naming:
- snake_case variables/functions;
- PascalCase classes;
- explicit enum names;
- no cryptic abbreviations.

---

## 17. Frontend Coding Standards

- TypeScript strict mode.
- Avoid `any`; use explicit narrow types.
- Server data via TanStack Query.
- Forms via React Hook Form + Zod.
- UI components do not directly construct arbitrary API calls.
- Route pages compose feature components.
- Generated OpenAPI types are preferred over duplicated manual interfaces.
- Monetary display uses shared formatter.
- Permission checks use common guard/helper.
- No business security logic only in UI.

Naming:
- PascalCase components;
- camelCase variables/functions;
- feature folder names kebab-case.

---

## 18. Git Workflow

Branches:

```text
main
feature/*
fix/*
chore/*
docs/*
```

`main` represents releasable code.

Normal change:

```text
branch
→ commits
→ push
→ Pull Request
→ CI
→ review
→ merge
```

Direct pushes to protected `main` are disabled once repository collaboration starts.

---

## 19. Commit Convention

Use Conventional Commits style:

```text
feat:
fix:
docs:
refactor:
test:
chore:
ci:
build:
perf:
```

Example:

```text
feat(plans): add budget item validation
fix(approval): prevent self approval
```

This supports readable history and future changelog automation.

---

## 20. Versioning

Use Semantic Versioning:

```text
MAJOR.MINOR.PATCH
```

Examples:

```text
0.1.0 development milestone
1.0.0 first production V1
1.1.0 backward-compatible feature
1.1.1 bug fix
2.0.0 breaking change
```

Release tag:

```text
v1.0.0
```

---

## 21. Backend Test Strategy

### Unit Tests
Target:
- pure calculation;
- status transitions;
- policy logic;
- permission/scope helpers.

### Service / Integration Tests
Use PostgreSQL test database.

Critical because:
- NUMERIC behavior;
- constraints;
- transactions;
- row locking;
- concurrent approval behavior.

Do not use SQLite as the primary backend integration database.

### API Tests
FastAPI + httpx.

Cover:
- authentication;
- validation;
- permission denial;
- correct response contracts;
- business conflicts.

---

## 22. Frontend Test Strategy

### Unit
Vitest.

### Component
React Testing Library.

Test:
- form behavior;
- status rendering;
- permission-aware actions;
- error states;
- validation.

### API Mocking
MSW for deterministic frontend tests.

### E2E
Playwright against a real test stack.

Critical paths:
- login;
- create fiscal year;
- annual budget;
- allocation;
- create plan;
- submit;
- approve;
- realization;
- report visibility.

---

## 23. Financial Concurrency Tests

Mandatory integration tests include:

1. Two plans competing for remaining allocation.
2. Two final approvals at near-same time.
3. Realization submitted against nearly exhausted remaining plan.
4. Revision approval while another operation changes available budget.
5. Allocation reduction while commitments exist.

Expected invariant:

```text
financial limits can never become negative or exceed approved ceilings.
```

---

## 24. Test Case Repository

User-requested manual test instructions live in:

```text
test-cases/
```

Each case has:

```text
Test ID
Module
Preconditions
Role
Steps
Input
Expected Result
Actual Result
Status
Evidence
Notes
```

Example:

```text
TEST ID: PLAN-APPROVAL-004

Scenario:
Final approval when unit budget is no longer sufficient.

Expected:
Approval rejected with budget conflict.
```

---

## 25. Test Logs

Generated/manual execution records:

```text
logs/testing/YYYY-MM-DD/
├── backend-tests.log
├── frontend-tests.log
├── e2e-tests.log
├── manual-test-summary.md
└── failures/
```

Important:
- application runtime production logs are not committed;
- normal generated test logs should generally not pollute Git history;
- curated test summaries/evidence for release may be committed under docs/testing/releases if required.

---

## 26. CI Pipeline

Pull Request checks:

### Backend
1. dependency install
2. Ruff check
3. Ruff format check
4. mypy
5. PostgreSQL service
6. Alembic clean migration
7. pytest

### Frontend
1. npm ci
2. ESLint
3. Prettier check
4. TypeScript typecheck
5. Vitest
6. build

### Contract
- generate/check OpenAPI client/types.

### E2E
- start test stack;
- Playwright critical-path suite.

### Security Baseline
- dependency vulnerability scan;
- secret scanning where available.

Merge blocked if required checks fail.

---

## 27. GitHub Actions Baseline

Recommended workflows:

```text
.github/workflows/
├── backend-ci.yml
├── frontend-ci.yml
├── contract-ci.yml
├── e2e-ci.yml
└── security-ci.yml
```

Do not add deployment workflow until the real production target is known.

---

## 28. Logging

Backend logs are structured.

Fields where applicable:

```text
timestamp
level
service
environment
request_id
method
path
status_code
duration_ms
user_id
```

Do NOT log:
- passwords;
- session IDs;
- reset tokens;
- CSRF secrets;
- full sensitive file contents.

Financial Audit Log is separate from operational application logs.

---

## 29. Request Correlation

Each API request gets/request accepts a request ID.

Response returns correlation ID.

Errors shown to users may include a support/reference code derived from request ID, for example:

```text
Reference: 01H...
```

This makes troubleshooting easier without exposing stack traces.

---

## 30. Error Handling

Production never returns raw traceback.

Canonical categories:

```text
VALIDATION_ERROR
AUTHENTICATION_REQUIRED
PERMISSION_DENIED
NOT_FOUND
CONFLICT
BUSINESS_RULE_VIOLATION
INSUFFICIENT_BUDGET
STALE_VERSION
RATE_LIMITED
INTERNAL_ERROR
```

Frontend maps these to understandable messages.

---

## 31. Health Checks

Backend:

```text
GET /health/live
GET /health/ready
```

`live`:
application process running.

`ready`:
critical dependencies such as database reachable and app ready to serve.

Health response never exposes secrets.

---

## 32. Performance Baseline

V1 rules:

- server-side pagination;
- explicit eager loading to avoid N+1;
- index foreign keys/search fields;
- avoid dashboard query-per-card patterns;
- aggregate reporting in database;
- uploads streamed rather than fully loaded unnecessarily;
- expensive export may move to background job in future.

Performance optimization follows evidence, not premature caching.

No Redis cache in V1 by default.

---

## 33. Security Checklist Baseline

Required before V1:

- [ ] strong password hashing
- [ ] secure cookie production flags
- [ ] CSRF protection
- [ ] CORS allowlist
- [ ] trusted host configuration
- [ ] upload allowlist/limits
- [ ] RBAC + scope tests
- [ ] self-approval tests
- [ ] no secrets committed
- [ ] production debug off
- [ ] HTTPS at edge
- [ ] dependency scan
- [ ] account deactivation behavior
- [ ] session invalidation
- [ ] financial concurrency tests
- [ ] audit trail verification
- [ ] database backup documented
- [ ] restore test procedure documented

---

## 34. Documentation Structure

```text
docs/
├── project-context/
│   └── PROJECT_CONTEXT.md
├── checkpoints/
│   ├── CP-01...
│   ├── CP-02...
│   ├── CP-03...
│   ├── CP-04...
│   └── CP-05...
├── architecture/
├── adr/
├── database/
├── api/
├── installation/
├── deployment/
├── testing/
├── security/
└── user-guide/
```

README is an entry point, not a replacement for all docs.

---

## 35. ADR Policy

Use Architecture Decision Record only for major decisions that may need future explanation.

Initial ADR candidates:

```text
ADR-0001 Modular Monolith
ADR-0002 PostgreSQL as Primary Database
ADR-0003 Server-side Opaque Sessions
ADR-0004 RBAC with Data Scope
ADR-0005 Financial Versioning and No Silent Overwrite
ADR-0006 OpenAPI-generated Frontend Contract
```

Not every implementation detail needs an ADR.

---

## 36. Definition of Done — Feature

A feature is not DONE only because the screen works.

Required where applicable:

- [ ] acceptance criteria met
- [ ] backend business rules implemented
- [ ] authorization implemented
- [ ] audit event implemented
- [ ] DB migration included
- [ ] backend tests pass
- [ ] frontend tests pass
- [ ] E2E critical flow updated
- [ ] loading/empty/error states exist
- [ ] accessibility basics reviewed
- [ ] no hardcoded organization-specific data
- [ ] documentation updated
- [ ] manual test case added/updated
- [ ] CI green
- [ ] code reviewed

---

## 37. Definition of Done — Financial Feature

Additional requirements:

- [ ] Decimal/NUMERIC used
- [ ] transaction boundary reviewed
- [ ] concurrency behavior tested
- [ ] before/after audit data correct
- [ ] revision/history behavior validated
- [ ] no unauthorized destructive update
- [ ] report totals reconcile to source data

---

## 38. Implementation Roadmap

### Phase 0 — Repository & Tooling
- initialize monorepo;
- config files;
- Docker PostgreSQL;
- backend/frontend scaffold;
- CI skeleton;
- health check;
- base docs.

Exit:
clean clone can boot project.

### Phase 1 — Foundation
- application settings;
- authentication/session;
- user management;
- RBAC + scope;
- organization units;
- audit infrastructure;
- application shell.

Exit:
authorized users can login and see role-aware navigation.

### Phase 2 — Budget Foundation
- fiscal year;
- budget categories;
- units of measure;
- annual budget;
- annual budget approval;
- unit allocation.

Exit:
approved annual budget can be distributed without exceeding total.

### Phase 3 — Budget Planning
- budget plan header;
- versioning;
- items;
- attachments;
- validation;
- draft/submit.

Exit:
unit can create and submit detailed plan.

### Phase 4 — Approval Engine
- workflow templates;
- workflow steps;
- approval instance;
- approve/reject/revision;
- self-approval prevention;
- final budget commitment transaction.

Exit:
submitted plans can complete configurable approval safely.

### Phase 5 — Realization
- realization draft;
- submit;
- verification;
- attachments;
- amount limits;
- execution status.

Exit:
approved plan can be realized incrementally and reconciled.

### Phase 6 — Monitoring & Reporting
- role dashboards;
- standard reports;
- filters;
- PDF/Excel/CSV exports where planned;
- utilization warnings.

Exit:
management and unit users can monitor budget position.

### Phase 7 — Operational Completeness
- notification center;
- revision workflows;
- allocation revision;
- advanced audit views;
- branding/settings completion;
- system information.

Exit:
feature-complete V1 candidate.

### Phase 8 — Hardening
- regression;
- E2E;
- security;
- performance;
- backup/restore;
- staging;
- UAT;
- documentation completion.

Exit:
release candidate.

---

## 39. Development Order Rule

Do not build dashboard calculations before source financial flows are stable.

Do not build elaborate report export before database rules are tested.

Do not build AI features in V1 before baseline financial accuracy is proven.

Correctness > convenience > decoration.

---

## 40. Release Candidate Gate

Before V1 RC:

- all migrations apply to clean database;
- CI green;
- critical E2E green;
- no Critical/High unresolved functional defects;
- permission matrix regression complete;
- concurrency financial tests green;
- report reconciliation complete;
- staging smoke test complete;
- backup + restore procedure tested;
- admin/user documentation usable;
- release notes prepared.

---

## 41. Production Deployment Assumptions

Production hosting is not yet fixed.

Therefore CP-05 does NOT lock:
- cloud provider;
- VPS vendor;
- reverse proxy product;
- domain;
- deployment automation target.

The application must remain deployable behind a standard HTTPS reverse proxy.

Deployment-specific checkpoint/runbook is created after infrastructure is known.

---

## 42. Initial V1 Non-goals

Do not include unless requirement changes:

- full accounting/general ledger;
- procurement lifecycle;
- vendor management suite;
- payroll;
- SIAKAD functions;
- native mobile app;
- microservices;
- Kubernetes;
- Redis without measured need;
- AI chatbot;
- custom no-code workflow builder.

---

## 43. Implementation Gate Decision

CP-01 through CP-05 provide sufficient baseline to begin implementation.

Implementation may reveal small adjustments. These are normal.

Rules:
- minor implementation clarification → update current docs;
- architectural/business-rule change → create checkpoint revision/ADR;
- do not silently diverge from baseline.

---

## 44. Checkpoint Status

- CP-01 Requirement & Business Rules — COMPLETE
- CP-02 Data Model & ERD — COMPLETE
- CP-03 Architecture & API — COMPLETE
- CP-04 UI/UX & Navigation — COMPLETE
- CP-05 Development Readiness — COMPLETE

**Project Status: READY FOR IMPLEMENTATION**

Next:
**Implementation Phase 0 — Repository & Tooling Scaffold**
