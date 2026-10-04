# Phase 4A Test Cases — Realization Core

- [ ] Unit PIC only sees APPROVED plans in its unit scope.
- [ ] Realization cannot be created for non-APPROVED plan.
- [ ] Realization cannot be created outside ACTIVE Fiscal Year.
- [ ] Realization date must fall inside Fiscal Year dates.
- [ ] Draft amount must be positive.
- [ ] Draft edit uses expected row version.
- [ ] Stale draft update returns 409.
- [ ] POST requires CSRF.
- [ ] POSTED realization is immutable.
- [ ] Sum of POSTED realizations cannot exceed approved plan amount.
- [ ] Multiple realization records per approved plan are supported.
- [ ] Audit records exist for create/update/post.
- [ ] Development seed includes ACTIVE-year realization scenarios.
