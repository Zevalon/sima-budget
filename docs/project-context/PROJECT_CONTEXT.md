# PROJECT CONTEXT — SIMA through Phase 3A

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

### Phase 2 — Budget Foundation

Complete through CP-07:

- Fiscal Year lifecycle;
- budget categories and units of measure;
- Annual Budget draft/submission/approval/rejection/revision;
- Unit Allocation;
- aggregate budget ceilings;
- PostgreSQL concurrency protection;
- optimistic concurrency;
- real dashboard budget summary;
- deterministic development seed.

## Current Phase 3A

Budget Plan draft foundation introduces:

```text
UnitAllocation
  └── BudgetPlan
        └── BudgetPlanVersion
              └── BudgetPlanItem[]
```

Rules:

- plan belongs to one unit and one Unit Allocation;
- unit must be allowed to create plans;
- draft creation/editing is allowed only in PLANNING;
- Unit PIC access follows OWN_UNIT / OWN_UNIT_AND_CHILDREN scope;
- each item stores quantity, unit price, category, UOM, and backend-computed amount;
- plan total cannot exceed its source Unit Allocation;
- draft plan editing uses optimistic row-version protection;
- draft plans do not consume official committed balance yet;
- Phase 3B/3C will add submission, approval, immutable approved versions, and committed-budget controls.

## Development Seed

The cumulative development seed is extended with representative FY2026 draft plans for IT and FTI.

Reset command:

```bash
make dev-seed-reset CONFIRM=RESET
```

## Core financial invariants

- money uses Decimal / PostgreSQL NUMERIC;
- Annual Budget approval locks the official pagu;
- Unit Allocation aggregate may not exceed Annual Budget;
- Budget Plan approval in later Phase 3 must preserve committed total <= Unit Allocation;
- concurrent writes must preserve financial ceilings;
- System Administrator does not imply financial authority;
- material financial/security mutations are audited.

## Next

After Phase 3A validation, smoke testing, CI, and merge:

**Phase 3B — Budget Plan Submission & Approval.**
