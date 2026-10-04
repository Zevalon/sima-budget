# Phase 4C — Realization Aggregates & Monitoring

Status: implementation / validation.

## Scope

Phase 4C connects Budget Foundation, approved plans, and realization execution into a consistent monitoring view.

Cross-domain financial flow:

```text
Annual Budget
  -> Allocated
  -> Committed APPROVED Plans
  -> Realized POSTED Transactions
```

Key formulas:

```text
Available for new plans = Allocated - Committed
Remaining to realize    = Committed - Realized
Plan remaining          = Approved Plan - Realized
```

Informational pipelines remain separate:

```text
Plan Draft Pipeline        = DRAFT + PENDING_APPROVAL plans
Realization Draft Pipeline = DRAFT realizations
```

`REVERSED` and `CANCELLED` realization records remain historical and are excluded from active financial totals.

## Monitoring

- Unit Allocation overview now exposes Realized, Draft Realization, and Remaining to Realize.
- Dashboard shows cross-domain execution metrics.
- Realization context exposes utilization percentages per plan and across the current user scope.
- Realization page displays plan-by-plan monitoring.

## Concurrency

Posting keeps the approved Budget Plan row locked during aggregate validation. Concurrent postings against the same approved plan cannot jointly exceed the approved amount.

Invariant:

```text
Realized <= Committed <= Allocated
```

No database migration is required for Phase 4C because all values are derived aggregates from existing records.
