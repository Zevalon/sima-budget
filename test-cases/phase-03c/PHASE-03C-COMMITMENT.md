# Phase 3C Test Cases

1. Two PENDING_APPROVAL plans of 600 against an allocation of 1000 are approved concurrently.
2. Exactly one approval succeeds and one returns HTTP 409.
3. Committed becomes 600; Draft Pipeline remains 600; Available becomes 400.
4. Reducing allocation to 500 returns HTTP 409 because committed is 600.
5. Reducing allocation to 800 succeeds; Available becomes 200.
6. Budget Plan context reports the same committed/pipeline/available values.
7. Approval audit records committed_before, committed_after, and available_after.
8. Full regression Phase 0 → Phase 3B remains green.
