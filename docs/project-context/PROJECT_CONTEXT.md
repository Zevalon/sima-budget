# PROJECT CONTEXT — SIMA through Phase 4D

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
- Phase 4C — Realization Aggregates & Monitoring

## Realization lifecycle

```text
DRAFT -> POSTED -> REVERSED
  \-> CANCELLED

REVERSED -> linked correction DRAFT -> POSTED
```

Financial records are not hard-deleted.

## Financial execution formulas

```text
Available for new plans = Allocated - Committed
Remaining to realize    = Committed - Realized
Plan remaining          = Approved Plan - Realized
```

Only `POSTED` realization records count as Realized.

## Phase 4D hardening

All realization mutations are bound to an exact workflow snapshot:

```text
expected_row_version
expected_status
expected_plan_version_id
```

A mismatch returns `409 Conflict`.

Creating a correction also increments the source realization row version so the correction relationship invalidates stale source views.

Final execution invariant:

```text
Realized <= Committed <= Allocated
```

Scope enforcement remains authoritative on the backend. A user can only view and mutate realization data within the organizational-unit scope granted by RBAC.

## Next

After local/browser/CI validation and merge:

1. CP-09 — Phase 4 Realization Complete
2. Phase 5 — Monitoring, Reporting & Export
