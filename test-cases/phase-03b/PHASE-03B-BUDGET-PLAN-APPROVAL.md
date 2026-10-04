# Phase 3B Test Cases

1. Unit PIC can submit own-unit DRAFT plan.
2. Submit locks ordinary draft editing.
3. Unit PIC does not receive approval permission by default.
4. Unit Approver sees only pending plans within assigned scope.
5. Approval/rejection requires CSRF.
6. Self-approval is rejected when `allow_self_approval=false`.
7. Reject requires a meaningful reason.
8. Rejected plan can be revised by Unit PIC.
9. Revision creates version N+1 and preserves version N.
10. Resubmission creates submission N+1 tied to the new version.
11. Unit Approver can approve resubmitted plan.
12. Approved plan cannot be draft-edited.
13. Approval history keeps exact version numbers and decisions.
14. Audit events exist for submit/reject/revise/approve.
15. Development seed contains pending and rejected plan scenarios.
