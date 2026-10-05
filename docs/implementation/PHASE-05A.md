# Phase 5A — Reporting Foundation & Financial Summary API

## Objective

Establish one authoritative, scope-aware reporting calculation layer before implementing the full reporting UI and export surface.

## Included

- `reports.view` permission and role-template bootstrap.
- Scoped `GET /api/v1/reports/financial-summary` endpoint.
- Canonical financial summary values:
  - Scope Budget
  - Allocated
  - Unallocated
  - Committed
  - Plan Draft Pipeline
  - Available
  - Realized
  - Realization Draft Pipeline
  - Remaining to Realize
  - Utilization
- Per-unit summary.
- Twelve-month realization summary.
- Plan-category committed/pipeline summary.
- Minimal Reports screen used to validate the canonical read model.
- Phase 5A regression verifier.

## Scope semantics

- `ALL`: report covers all active organization units and uses the annual budget as the scope ceiling.
- `OWN_UNIT`: report covers the assigned unit.
- `OWN_UNIT_AND_CHILDREN`: report covers the assigned unit and its descendants.
- `OWN`: report maps to the user's active unit memberships.

For unit-scoped reports, `scope_budget_amount` is the sum of unit allocations visible in the user's scope.

## Financial formulas

```text
Available = Allocated - Committed
Remaining to Realize = Committed - Realized
Utilization = Realized / Committed * 100
```

Only `POSTED` realizations contribute to Realized.
Only `DRAFT` realizations contribute to Realization Draft Pipeline.
Only `APPROVED` plan current versions contribute to Committed.
`DRAFT` and `PENDING_APPROVAL` current plan versions contribute to Plan Draft Pipeline.

## Important limitation

Realization is currently recorded at Budget Plan level, not at Budget Plan Item/category level. Therefore Phase 5A does not invent a category-level Realized value. Category summaries expose plan commitment and plan pipeline only.

## No migration

Phase 5A introduces no new database table or column.
