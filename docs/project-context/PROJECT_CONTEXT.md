# PROJECT CONTEXT — SIMA through Phase 4C

SIMA is an annual budget planning and monitoring application built with React + TypeScript,
FastAPI, PostgreSQL, SQLAlchemy, Alembic, and Docker.

## Completed milestones

- Phase 0 — Repository & Tooling
- Phase 1 — Foundation
- Phase 2 — Budget Foundation
- Phase 3 — Budget Plan
- CP-08 — Phase 3 Budget Plan Complete
- Phase 4A — Realization Core
- Phase 4B — Realization Correction, Cancellation & Reversal

## Realization lifecycle

```text
DRAFT -> POSTED -> REVERSED
  \-> CANCELLED

REVERSED -> linked correction DRAFT -> POSTED
```

Financial records are never hard-deleted. REVERSED and CANCELLED remain historical.

## Phase 4C — Aggregates & Monitoring

Cross-domain flow:

```text
Annual Budget
  -> Allocated
  -> Committed APPROVED Plans
  -> Realized POSTED Transactions
```

Formulas:

```text
Available for new plans = Allocated - Committed
Remaining to realize    = Committed - Realized
Plan remaining          = Approved Plan - Realized
```

Pipelines remain separate:

```text
Plan Draft Pipeline        = DRAFT + PENDING_APPROVAL plans
Realization Draft Pipeline = DRAFT realizations
```

Realization context includes utilization percentages and plan-level monitoring.
Dashboard and Unit Allocation views expose execution aggregates.

Concurrency rule:

```text
Realized <= Committed <= Allocated
```

Concurrent postings against one plan are serialized through the approved-plan lock so they cannot
jointly exceed the approved amount.

## Seed baseline

The Phase 4B cumulative development seed already contains DRAFT, POSTED, CANCELLED, REVERSED, and
correction DRAFT records and remains suitable for Phase 4C monitoring smoke tests.

## Next

Phase 4D — Realization Hardening & Phase 4 Completion.
