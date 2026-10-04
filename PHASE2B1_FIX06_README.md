# SIMA Phase 2B1 — Fix 06: Data-Aware Phase 2A Regression Gate

## Symptom

During `make phase2b1-check`, the nested Phase 2A regression verifier fails at:

```text
POST /api/v1/fiscal-years/<temporary-id>/transition -> 409 Conflict
Hanya satu tahun anggaran ACTIVE yang diperbolehkan.
```

although Phase 2A previously passed.

## Cause

After the Phase 2A browser smoke test, the development database can legitimately
contain a real `ACTIVE` fiscal year.

The old Phase 2A verifier assumed there was no existing ACTIVE year and always
expected its temporary fiscal year to become ACTIVE.

## Fix

The verifier is now data-aware.

If no real ACTIVE fiscal year exists, it runs the complete original lifecycle,
including successful controlled reopen.

If a real ACTIVE fiscal year already exists, it:

- leaves the real fiscal year untouched;
- expects temporary activation attempts to return HTTP 409;
- verifies the one-ACTIVE invariant;
- verifies invalid reopen protection;
- continues budget-category and unit-of-measure verification;
- verifies a valid audit event for the path that actually ran.

The checker never closes, archives, or modifies real business data to make a
regression test pass.

## Apply

```bash
unzip -o SIMA_Phase2B1_Fix06_Data_Aware_Phase2A_Regression.zip \
  -d ~/projects/sima-budget

cd ~/projects/sima-budget/apps/backend
uv run ruff check . --fix
uv run ruff format .

cd ~/projects/sima-budget
make phase2b1-check
```

No database reset, rollback, or volume deletion is required.
