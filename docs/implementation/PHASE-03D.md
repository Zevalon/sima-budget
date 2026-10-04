# Phase 3D — Budget Plan Hardening & Phase 3 Completion

## Status

Pending validation.

## Goals

Phase 3D closes the Budget Plan domain before Realization work begins.

Hardening focuses on workflow identity and stale-action safety:

- submit requires the row version the PIC actually reviewed;
- approve/reject requires the exact row version, submission number, and plan version shown to the approver;
- a stale approval tab cannot accidentally approve a later resubmission;
- scoped planning context exposes aggregate Allocated / Committed / Draft Pipeline / Available amounts;
- UI explains missing plan master data instead of silently hiding creation controls.

## Approval identity invariant

An approval decision must refer to one exact review target:

```text
Budget Plan row_version
+ submission_no
+ plan version_no
```

If any of these changed after the approver loaded the inbox, the server returns `409 Conflict`.

This prevents a stale browser tab that reviewed Version 1 / Submission 1 from approving
Version 2 / Submission 2 after a reject → revise → resubmit cycle.

## Financial summary

For all allocations visible in the current user's scope:

```text
Scope Allocation = sum(Unit Allocation)
Scope Committed = sum(APPROVED current plan versions)
Scope Draft Pipeline = sum(DRAFT + PENDING_APPROVAL current plan versions)
Scope Available = sum(Unit Allocation - Committed)
```

Draft Pipeline remains informational and does not reserve official budget.

## Migration

No new database migration is required. Phase 3D hardens API contracts and workflow logic
using the Phase 3A/3B schema.

## Exit

After gate + browser smoke + CI + merge, Phase 3 is ready for CP-08.
