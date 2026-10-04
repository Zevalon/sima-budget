# PROJECT CONTEXT — SIMA through Phase 3B

SIMA is an annual budget planning and monitoring application built with React + TypeScript,
FastAPI, PostgreSQL, SQLAlchemy, Alembic, and Docker.

## Completed foundation

Phase 0, Phase 1, and Phase 2 are complete. CP-07 is the Phase 2 checkpoint.

## Phase 3A

Budget Plan core is implemented:

```text
Unit Allocation
  -> Budget Plan
     -> Budget Plan Version
        -> Budget Plan Items
```

Draft plan items use Decimal financial arithmetic and are scoped to organizational units.

## Phase 3B

Budget Plan workflow becomes:

```text
DRAFT
  -> PENDING_APPROVAL
       -> APPROVED
       -> REJECTED
            -> revise -> DRAFT (new version)
```

Every submission stores the exact plan version reviewed. Rejected revisions create a new
`BudgetPlanVersion`; approved versions are not silently overwritten.

Unit PIC owns create/update/submit/revise within scope. Unit Approver owns approve/reject
within scope. Self-approval follows application settings and is disabled by default.

## Important Phase 3B boundary

Approval is implemented, but aggregate financial commitment across multiple approved plans
is intentionally deferred to Phase 3C.

Phase 3C must enforce:

```text
Committed approved plans <= Unit Allocation
Available = Unit Allocation - Committed
```

The aggregate check must be concurrency-safe using the PostgreSQL locking principles
established in Phase 2C.

## Development seed

The cumulative development seed is extended with pending and rejected Budget Plan scenarios.
Future phases continue extending the same seed baseline.
