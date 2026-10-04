# Phase 3B — Budget Plan Submission & Approval

## Scope

Phase 3B turns draft Budget Plans into reviewable, version-bound financial proposals.

Implemented:

- `budget_plan_approvals` history table;
- submitted/approved/rejected metadata on Budget Plan;
- submit endpoint;
- scoped Unit Approver inbox;
- approve and reject endpoints;
- mandatory rejection reason;
- self-approval guard;
- rejected-plan revision creating a new immutable version;
- resubmission with incrementing submission number;
- approval history API;
- Approval landing page and Budget Plan approval UI;
- cumulative development seed scenarios for PENDING and REJECTED plans.

## Important boundary

Phase 3B approves a plan version but does **not yet implement aggregate commitment** across
multiple approved plans. `Committed` and `Available` enforcement is Phase 3C.

Approved plans are locked from ordinary draft editing.
