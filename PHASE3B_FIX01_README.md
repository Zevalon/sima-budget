# SIMA Phase 3B — Fix 01: Ruff E501 Formatting

## Symptom

Running:

```bash
uv run ruff check . --fix
```

reports three remaining `E501 Line too long` errors in:

- `apps/backend/scripts/seed_dev.py`
- `apps/backend/scripts/verify_phase3b.py`

## Cause

These are formatting-only issues. Ruff's `--fix` does not automatically rewrite
every E501 case.

## Fix

The long conditional assignment and SQLAlchemy scalar queries are expanded to
multiline form.

No business logic changes are made.

## Apply

```bash
unzip -o SIMA_Phase3B_Fix01_Ruff_E501.zip \
  -d ~/projects/sima-budget

cd ~/projects/sima-budget/apps/backend
uv run ruff format .
uv run ruff check . --fix

cd ~/projects/sima-budget
make phase3b-check
```

No migration rollback, seed reset, or database reset is required.
