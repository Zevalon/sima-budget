# Phase 2B1 — Annual Budget Core & Submission

## Goal

Introduce the organization-wide annual budget after Fiscal Year foundation is stable.

## Scope

Phase 2B1 implements:

- one Annual Budget per Fiscal Year;
- monetary amount stored as PostgreSQL `NUMERIC(20,2)` and Python `Decimal`;
- DRAFT creation and editing;
- submit-for-approval transition;
- submission history records;
- backend permission enforcement;
- CSRF enforcement for mutations;
- audit events;
- Annual Budget frontend page bound to the global Fiscal Year selector.

## Lifecycle available in this slice

```text
DRAFT → PENDING_APPROVAL
```

The schema already reserves the complete workflow states:

```text
DRAFT
PENDING_APPROVAL
APPROVED
REJECTED
```

`APPROVED` and `REJECTED` decisions are implemented in Phase 2B2.

## Business rules

- annual budget may only be created for a Fiscal Year in `PLANNING`;
- only one annual budget may exist per organization + fiscal year;
- amount must be greater than zero;
- only DRAFT budgets can be edited;
- submission is concurrency-protected with a row lock;
- once submitted, the budget cannot be edited until the future approval flow returns it;
- each submission creates an immutable submission-history row;
- System Administrator receives read access only;
- Budget Administrator receives create/update/submit authority;
- Management Approver receives read access in preparation for Phase 2B2.

## Financial precision

The frontend sends the money amount as a string. The backend parses it as `Decimal`,
and PostgreSQL stores it as `NUMERIC(20,2)`. The UI formatter does not convert the
budget amount to a JavaScript floating-point number.

## Audit actions

- `ANNUAL_BUDGET_CREATED`
- `ANNUAL_BUDGET_UPDATED`
- `ANNUAL_BUDGET_SUBMITTED`

## Out of scope

- approve / reject action;
- annual-budget revision after approval;
- unit allocations;
- budget plan commitment;
- realization;
- financial reports.
