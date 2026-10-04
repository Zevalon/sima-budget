# Phase 2D — Budget Foundation Hardening & Completion

## Status

Pending local validation.

## Scope

Phase 2D closes the Budget Foundation before Phase 3 begins.

Hardening included:

- optimistic concurrency guard for Unit Allocation updates using `expected_version`;
- stale allocation edits return HTTP 409 instead of silently overwriting a newer update;
- organization units with allocations in open Fiscal Years cannot be deactivated or changed to `can_receive_budget=false`;
- allocations in CLOSED/ARCHIVED years remain historical and no longer block administrative cleanup;
- Unit Allocation empty states explain when no eligible unit exists or every eligible unit is already allocated;
- Dashboard now uses real Annual Budget / Allocated / Remaining data for the selected Fiscal Year;
- frontend Fast Refresh warning for the fiscal-year context is intentionally suppressed at the co-located hook export;
- the Phase 1D2 verification cleanup no longer emits the duplicate role DELETE warning;
- Phase 2D adds a final budget-foundation hardening regression gate.

## Allocation optimistic concurrency

`PATCH /api/v1/unit-allocations/{allocation_id}` now requires:

```json
{
  "expected_version": 2,
  "amount": "125000000000.00"
}
```

The server locks the Annual Budget and allocation row, then compares `expected_version` against the current allocation version.

If the record changed after the browser loaded it, the update is rejected with HTTP 409 and the user must refresh before retrying.

This prevents stale browser state from silently overwriting a more recent allocation adjustment.

## Organization-unit safety

An organization unit cannot be:

- deactivated; or
- changed from `can_receive_budget=true` to `false`

while it has a Unit Allocation in a Fiscal Year with status:

- DRAFT;
- PLANNING; or
- ACTIVE.

Historical allocations in CLOSED/ARCHIVED years do not permanently lock the organization structure.

## Dashboard

The dashboard now reflects the selected Fiscal Year and, for users with `unit_allocations.view`, displays:

- approved Annual Budget;
- allocated total;
- remaining amount;
- allocation percentage;
- number of allocated units;
- fiscal-year / Annual Budget readiness context.

Users without organization-wide allocation visibility do not receive the financial summary.

## Database

No migration is required for Phase 2D.

The existing Development Seed Baseline remains valid and does not require a schema/data extension in this phase.
