# Phase 2D Test Cases — Budget Foundation Hardening

## Automated gate

Run:

```bash
make phase2d-check
```

Expected terminal markers:

```text
Phase 2D budget foundation hardening verification: OK
Phase 2D checks passed.
```

## Core cases

1. All Phase 2C regression checks still pass.
2. Unit Allocation update requires `expected_version`.
3. Valid update with current version succeeds and increments version.
4. Reusing a stale version after a successful update returns HTTP 409.
5. Unit with an allocation in an open Fiscal Year cannot be changed to `can_receive_budget=false`.
6. Unit with an allocation in an open Fiscal Year cannot be deactivated.
7. Historical allocation in a CLOSED Fiscal Year does not permanently block unit deactivation.
8. Dashboard shows real Annual Budget / Allocated / Remaining values for users with allocation-view permission.
9. Allocation page explains when no eligible receiving unit exists.
10. Allocation page explains when all eligible units already have allocations.
11. Frontend lint runs without the prior Fast Refresh warning.
12. Phase 1D2 verifier runs without the prior duplicate role DELETE warning.
