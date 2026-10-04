# Phase 2C Test Cases — Unit Allocation

## Automated gate

Run:

```bash
make phase2c-check
```

Expected terminal markers:

```text
Phase 2C unit allocation verification: OK
Phase 2C checks passed.
```

## Core cases

1. Budget Administrator has create/update allocation permissions.
2. System Administrator has allocation view only.
3. Management Approver has allocation view only.
4. Unit PIC is not granted organization-wide allocation visibility.
5. Unsafe write without CSRF is rejected.
6. Unit with `can_receive_budget=false` is rejected.
7. Annual Budget must be APPROVED.
8. Fiscal Year must be PLANNING for allocation mutation.
9. Duplicate allocation for the same Annual Budget + unit is rejected.
10. Aggregate allocation cannot exceed Annual Budget.
11. Concurrent writes cannot jointly over-allocate.
12. Valid allocation update increments version.
13. Allocation create/update actions are audited.
14. Overview returns Annual Budget, allocated, and remaining totals.
