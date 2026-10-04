# Phase 3D Test Cases — Budget Plan Hardening

## Automated

- stale DRAFT submit returns `409`;
- fresh submit succeeds;
- reject Submission 1 / Version 1 succeeds;
- revise creates Version 2;
- resubmit creates Submission 2;
- stale approver using Submission 1 / Version 1 identifiers returns `409`;
- fresh decision for Submission 2 / Version 2 succeeds;
- approval history retains both submissions and exact versions;
- scoped planning context reports allocation, committed, pipeline, and available totals;
- final approval commits only the reviewed Version 2;
- all Phase 0 → Phase 3C regression gates remain green.

## Browser smoke

1. Open the same pending plan in an approver tab.
2. In another workflow, reject it, revise, and resubmit it.
3. Attempt the old decision without reloading the stale approval page.
4. Confirm the action is rejected with a conflict message.
5. Reload approval inbox and approve the new submission.
6. Verify the Rencana Anggaran summary cards show scoped Allocation, Committed, Pipeline, Available.
7. Verify missing active budget category/UOM shows an explanatory empty state.
