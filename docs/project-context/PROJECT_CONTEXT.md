# PROJECT CONTEXT — SIMA through Phase 2D

## Project

SIMA — Sistem Informasi Monitoring Anggaran.

A generic web application for annual budget planning, allocation, approval, realization, monitoring, and reporting. Initial deployment target is a private university.

## Technology

- React + TypeScript + Vite
- FastAPI + Python
- PostgreSQL
- SQLAlchemy 2 async + psycopg 3
- Alembic
- Docker Compose
- modular monolith / monorepo

## Completed implementation

### Phase 1 — Foundation

Authentication, server-side sessions, CSRF, users, roles, permissions, scoped RBAC, organization hierarchy, settings, audit, and administration hardening are complete.

### Phase 2A — Budget master foundation

- Fiscal Year lifecycle;
- budget categories;
- units of measure.

Fiscal Year lifecycle:

```text
DRAFT → PLANNING → ACTIVE → CLOSED → ARCHIVED
```

### Phase 2B — Annual Budget

- one Annual Budget per Fiscal Year;
- Decimal / NUMERIC monetary values;
- draft and submission;
- Management Approval / rejection;
- rejection revision and resubmission;
- approved budget locking;
- self-approval disabled by default;
- audit history.

### Phase 2C — Unit Allocation

- one allocation per Annual Budget + organization unit;
- only eligible active units can receive allocation;
- Annual Budget must be APPROVED;
- writes allowed only in PLANNING;
- total allocation <= approved Annual Budget;
- PostgreSQL row locking protects concurrent aggregate writes;
- allocation changes are versioned and audited.

### Development Seed Baseline

Deterministic development seed covers all implemented tables through Phase 2C and provides representative roles, users, units, Fiscal Years, Annual Budgets, approvals, and allocations.

Reset command:

```bash
make dev-seed-reset CONFIRM=RESET
```

## Current Phase 2D hardening

- allocation optimistic concurrency using `expected_version`;
- organization units with open-year allocations cannot become ineligible or inactive;
- Dashboard shows real Annual Budget / Allocated / Remaining values;
- clearer Unit Allocation states;
- regression-warning cleanup;
- final Phase 2 gate.

## Core financial invariants

- money uses Decimal / PostgreSQL NUMERIC;
- Annual Budget approval locks the official pagu;
- Unit Allocation aggregate may not exceed Annual Budget;
- concurrent writes must preserve financial ceilings;
- System Administrator does not imply financial authority;
- processed financial records are not hard-deleted;
- material financial/security mutations are audited.

## Next

After Phase 2D passes automated validation, browser smoke testing, CI, and merge:

1. create CP-07 — Phase 2 Budget Foundation Complete;
2. begin Phase 3 — Budget Plan / Rencana Anggaran.
