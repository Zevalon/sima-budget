# SIMA Phase 3D — Fix 01: Ruff E501

## Symptom

Running:

```bash
uv run ruff check . --fix
```

leaves one error:

```text
E501 Line too long (101 > 100)
scripts/verify_phase3d.py:235:101
```

## Cause

The `item_payload()` function signature is one character over the configured
100-character limit.

## Fix

Expand the function signature to multiline form.

No business logic changes are made.

## Apply

```bash
unzip -o SIMA_Phase3D_Fix01_Ruff_E501.zip \
  -d ~/projects/sima-budget

cd ~/projects/sima-budget/apps/backend
uv run ruff format .
uv run ruff check . --fix

cd ~/projects/sima-budget
make phase3d-check
```

No migration, seed reset, database reset, or dependency reinstall is required.
