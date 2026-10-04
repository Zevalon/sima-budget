# Phase 3A — Budget Plan Core & Versioned Items

Status: pending local validation.

## Goal

Allow organizational units to build detailed draft spending plans against their
approved Unit Allocation.

## Domain

```text
UnitAllocation
  └── BudgetPlan
        └── BudgetPlanVersion
              └── BudgetPlanItem[]
```

Phase 3A creates version 1 and allows that draft version to be edited. Later
approval/revision phases will create immutable approved versions and new
revision versions rather than rewriting approved data.

## Financial rule

For a single draft plan:

```text
sum(quantity × unit_price) <= source UnitAllocation.amount
```

Draft plans do not reserve or commit allocation in Phase 3A.

## Access

- UNIT_PIC: scoped view/create/update.
- UNIT_APPROVER: scoped read.
- Budget Administrator: organization-wide read.
- Management Approver: organization-wide read.
- Auditor/Viewer/System Administrator: read according to assigned scope.

Backend scope checks are authoritative.

## Validation

`make phase3a-check` runs the full Phase 2D regression chain, applies the new
migration, refreshes role permissions, then verifies scoped access, Decimal item
math, allocation ceilings, draft update, audit, and stale-update conflicts.
