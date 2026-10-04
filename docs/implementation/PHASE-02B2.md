# Phase 2B2 — Annual Budget Approval & Rejection

## Scope

Phase 2B2 completes the first Annual Budget approval workflow.

Implemented:

- Management Approver authority through `annual_budgets.approve`;
- dedicated Approval inbox;
- approve Annual Budget;
- reject Annual Budget with mandatory reason;
- self-approval guard using `allow_self_approval`;
- rejected budget revision back to DRAFT with version increment;
- resubmission after rejection;
- approved budget immutable;
- approval decision audit trail;
- approval-history continuity across submissions.

No new database migration is required because Phase 2B1 already created the
approval history and decision fields.
