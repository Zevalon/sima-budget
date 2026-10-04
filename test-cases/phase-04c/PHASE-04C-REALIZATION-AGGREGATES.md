# Phase 4C Test Cases

1. Unit Allocation overview exposes realized amount from POSTED realizations only.
2. DRAFT realizations are reported separately as Realization Draft Pipeline.
3. REVERSED realizations are excluded from Realized.
4. CANCELLED realizations are excluded from Realization Draft Pipeline.
5. Remaining to Realize equals Committed minus Realized.
6. Realization context reports utilization percentage per approved plan.
7. Scope utilization percentage equals scoped Realized divided by scoped Approved Plan amount.
8. Two 600 postings against one 1,000 approved plan result in exactly one success and one 409 conflict.
9. Aggregate invariant remains `Realized <= Committed <= Allocated`.
10. Dashboard displays Allocated, Committed, Available, Realized, Draft Realization, and Remaining to Realize.
11. Realization page displays monitoring per approved plan.
12. Full Phase 0 through Phase 4B regression remains green.
