# SIMA Phase 2A — Fix 01: Audit Authority Verification

## Symptom

The Phase 2A verifier reaches:

```text
GET /api/v1/audit?action=FISCAL_YEAR_REOPENED -> 403 Forbidden
```

and then fails because the checker expected HTTP 200.

## Cause

This is an error in the verifier, not in the application.

The verification user has role `BUDGET_ADMIN`.

By design, `BUDGET_ADMIN` owns budget-domain administration permissions but
does not automatically receive `audit.view`.

This preserves the rule that financial/operational authority does not imply
global audit authority.

Therefore HTTP 403 from the Audit Log API is the correct behavior.

## Fix

The verifier now performs two independent assertions:

1. `BUDGET_ADMIN` receives HTTP 403 when attempting to access `/api/v1/audit`.
2. The `FISCAL_YEAR_REOPENED` event is verified directly in PostgreSQL.

This validates both authorization separation and audit-event persistence.

## Apply

```bash
unzip -o SIMA_Phase2A_Fix01_Audit_Verification.zip \
  -d ~/projects/sima-budget

cd ~/projects/sima-budget/apps/backend
uv run ruff check . --fix
uv run ruff format .

cd ~/projects/sima-budget
make phase2a-check
```

No database reset, rollback, or migration change is required.

The frontend Fast Refresh warning shown by ESLint is non-blocking and does not
cause this gate failure.
