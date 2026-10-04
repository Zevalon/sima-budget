# Phase 3C — Commitment & Available Budget Controls

## Status

Pending validation.

## Financial definitions

```text
Allocated = Unit Allocation
Committed = sum(current approved Budget Plan versions)
Available = max(Allocated - Committed, 0)
Draft Pipeline = sum(current DRAFT + PENDING_APPROVAL Budget Plans)
```

Rejected plans do not consume commitment. Draft Pipeline is informational only.

## Concurrency invariant

Approval of a Budget Plan locks its Unit Allocation row before calculating the committed aggregate. This serializes approvals affecting the same allocation and prevents concurrent approvals from overspending the allocation.

## Allocation hardening

A Unit Allocation cannot be reduced below the amount already committed by APPROVED plans.

## UI

Commitment, pipeline, and available amounts are shown in Budget Plan context, Unit Allocation, and Dashboard views.
