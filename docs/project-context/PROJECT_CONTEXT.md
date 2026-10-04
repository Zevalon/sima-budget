# PROJECT CONTEXT — SIMA through Phase 3D

SIMA is an annual budget planning and monitoring application built with React + TypeScript,
FastAPI, PostgreSQL, SQLAlchemy, Alembic, and Docker.

## Completed foundation

Phase 0, Phase 1, and Phase 2 are complete. CP-07 is the Phase 2 checkpoint.

## Phase 3A — Budget Plan Core

Implemented:

```text
Unit Allocation
  -> Budget Plan
     -> Budget Plan Version
        -> Budget Plan Items
```

Plan items use Decimal arithmetic and unit-scoped access.

## Phase 3B — Submission & Approval

Workflow:

```text
DRAFT
  -> PENDING_APPROVAL
       -> APPROVED
       -> REJECTED
            -> revise -> DRAFT (new version)
```

Each approval record references the exact submitted `BudgetPlanVersion`.

## Phase 3C — Commitment Controls

Financial definitions:

```text
Committed = APPROVED current plan versions
Draft Pipeline = DRAFT + PENDING_APPROVAL current plan versions
Available = Unit Allocation - Committed
```

Approval locks Unit Allocation before validating aggregate commitment, preventing concurrent
overspending.

## Phase 3D — Hardening

Workflow actions are protected from stale browser state.

Submit requires the expected Budget Plan row version. Approval decisions require:

```text
expected row_version
expected submission_no
expected version_no
```

A stale approver who reviewed an earlier submission cannot approve a newer resubmission without
reloading and reviewing the new version.

The Budget Plan page also shows scoped Allocation, Committed, Draft Pipeline, and Available totals.

## Development seed

The cumulative development seed remains the standard reproducible local baseline. Phase 3D does
not add persistent tables, so no new seed entity is required.

## Next milestone

After Phase 3D gate, smoke test, CI, and merge: create CP-08 — Phase 3 Budget Plan Complete.
