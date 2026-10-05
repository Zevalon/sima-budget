# Phase 4D Test Cases

## Workflow identity

- [ ] Update with wrong expected status returns 409.
- [ ] Update with wrong expected plan version returns 409.
- [ ] Correct DRAFT snapshot updates successfully.
- [ ] Posting with stale workflow status returns 409.
- [ ] Posting with exact snapshot succeeds.
- [ ] Reversal with wrong plan-version identity returns 409.
- [ ] Reversal with exact POSTED snapshot succeeds.
- [ ] Correction with wrong expected status returns 409.
- [ ] Correction from exact REVERSED snapshot succeeds.
- [ ] Creating a correction increments source row version.
- [ ] Old source snapshot cannot create another correction.

## Aggregate consistency

- [ ] Reversed source is removed from Realized.
- [ ] Posted correction contributes to Realized.
- [ ] Realization context and Unit Allocation overview agree.
- [ ] `Realized <= Committed <= Allocated` remains true.

## Scope

- [ ] PIC from another unit cannot open the realization detail.
- [ ] Out-of-scope realization context contains no plans or realized amount.

## Regression

- [ ] `make phase4d-check` passes.
- [ ] Browser smoke test passes.
- [ ] GitHub CI passes before merge.
