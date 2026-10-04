# Phase 4B Test Cases

1. UNIT_PIC receives `realizations.cancel` and `realizations.reverse`.
2. Budget/System admin do not gain financial mutation authority automatically.
3. DRAFT cancellation requires CSRF, scope, current row version, and reason.
4. Cancelled records remain queryable and do not contribute to Draft Pipeline.
5. POSTED reversal requires CSRF, scope, current row version, and reason.
6. Reversed records remain queryable and release realized amount.
7. Only REVERSED records can create a correction draft.
8. Only one direct correction record can be linked to a reversed source.
9. Correction draft starts as DRAFT and can be edited/post normally.
10. POSTED records cannot be cancelled.
11. All cancellation/reversal/correction actions are audited.
