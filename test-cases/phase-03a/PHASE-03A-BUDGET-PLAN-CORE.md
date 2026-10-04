# Phase 3A Test Cases

1. Unit PIC sees only Unit Allocations allowed by role scope.
2. Unit PIC cannot create a plan for an out-of-scope unit.
3. Plan requires at least one item.
4. Item amount is calculated by backend as quantity × unit price.
5. Plan total above source Unit Allocation is rejected with conflict.
6. Draft update succeeds with current row version.
7. Stale row version is rejected with conflict.
8. Draft remains version 1 during Phase 3A editing.
9. Audit records create/update events.
10. Seed contains representative FY2026 draft plans for IT and FTI.
