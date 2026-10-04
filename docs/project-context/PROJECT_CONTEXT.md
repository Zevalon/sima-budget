# PROJECT CONTEXT — SIMA through Phase 4B

SIMA is an annual budget planning and monitoring application built with React + TypeScript,
FastAPI, PostgreSQL, SQLAlchemy, Alembic, and Docker.

## Completed milestones

- Phase 0 — Repository & Tooling
- Phase 1 — Foundation
- Phase 2 — Budget Foundation
- Phase 3 — Budget Plan
- CP-08 — Phase 3 Budget Plan Complete
- Phase 4A — Realization Core

## Phase 4A — Realization Core

Realization is linked to the exact APPROVED Budget Plan version.

```text
Approved Plan
- POSTED Realization
= Remaining To Realize
```

DRAFT records are informational pipeline only. Posting uses concurrency-safe aggregate validation
and optimistic row-version checks.

## Phase 4B — Correction Workflow

Financial realization records are never hard-deleted.

```text
DRAFT -> POSTED -> REVERSED
  \-> CANCELLED

REVERSED -> linked correction DRAFT -> POSTED
```

Rules:

- DRAFT cancellation requires a reason;
- POSTED reversal requires a reason;
- REVERSED no longer counts toward Realized;
- CANCELLED no longer counts toward Draft Pipeline;
- one direct correction DRAFT may be created from a reversed source;
- source/correction linkage remains queryable;
- cancel/reverse/correction use optimistic concurrency;
- all actions are unit-scoped and audited;
- only ACTIVE Fiscal Years allow financial mutations.

## Seed baseline

The cumulative development seed now contains representative DRAFT, POSTED, CANCELLED,
REVERSED, and correction DRAFT realization records for FY2025.

## Next

Phase 4C — Realization Aggregates & Monitoring.
