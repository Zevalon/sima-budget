# Phase 2B2 Test Cases

- Management Approver has `annual_budgets.approve`.
- System Administrator does not receive financial approval authority automatically.
- Budget Administrator does not receive approval authority automatically.
- Pending approval inbox lists submitted budgets.
- Approve/reject require CSRF.
- Reject requires a meaningful reason.
- Self-approval is rejected while `allow_self_approval=false`.
- Rejected budget can be revised; revision becomes DRAFT and increments version.
- Revised budget can be resubmitted as a new approval submission number.
- Approved budget is immutable.
- Approval/rejection decisions are audited.
