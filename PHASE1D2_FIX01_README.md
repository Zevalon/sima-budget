# SIMA Phase 1D2 — Fix 01: Deterministic Last-Admin Verification

## Symptom

The hardening gate reaches:

```text
PUT /api/v1/admin/users/<verification-admin>/roles -> 200 OK
```

but the checker expects HTTP 409.

## Cause

The verification account `phase1d2_admin` is not necessarily the last System
Administrator in a real development database.

If the developer already has an active real administrator with
`SYSTEM_ADMIN + ALL`, removing the temporary verification administrator is
correctly allowed. The previous checker incorrectly assumed a pristine database.

## Fix

The checker now validates the last-administrator invariant in a temporary,
isolated organization containing exactly one temporary System Administrator.

It does **not** deactivate, modify, or remove any administrator from the real
`DEFAULT` organization.

The temporary isolated organization, role, assignment, and user are deleted
immediately after the assertion.

## Apply

```bash
unzip -o SIMA_Phase1D2_Fix01_Last_Admin_Verification.zip \
  -d ~/projects/sima-budget

cd ~/projects/sima-budget/apps/backend
uv run ruff check . --fix
uv run ruff format .

cd ~/projects/sima-budget
make phase1d2-check
```

No database reset or migration change is required.

The failed previous run may have left Phase 1D2 temporary records behind.
That is safe: the verifier begins with its own cleanup and will remove them
on the next run.
