# Phase 2B1 Test Cases

## Automated gate

Run:

```bash
make phase2b1-check
```

Expected:

```text
Phase 2B1 annual budget core verification: OK
Phase 2B1 checks passed.
```

## Required behaviors

- regression gates through Phase 2A pass;
- migration creates annual-budget tables;
- bootstrap adds Phase 2B1 permissions;
- System Administrator has `annual_budgets.view` but not create/update/submit;
- Budget Administrator has view/create/update/submit;
- missing CSRF rejects create;
- annual budget requires a PLANNING fiscal year;
- one budget per fiscal year is enforced;
- decimal amount round-trips exactly;
- DRAFT budget can be edited;
- submit changes status to `PENDING_APPROVAL`;
- submission creates history row #1;
- submitted budget cannot be edited;
- submit action is auditable.

## Browser smoke

Use a Budget Administrator with scope `ALL`:

1. select a PLANNING fiscal year;
2. open **Anggaran**;
3. create a draft annual budget;
4. edit amount / notes;
5. submit it for approval;
6. confirm status becomes `PENDING_APPROVAL`;
7. confirm editing is no longer available;
8. confirm submission history shows one pending submission.

Use System Administrator:

- page may be viewed;
- create/edit/submit controls must not appear.
