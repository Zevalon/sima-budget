# SIMA Phase 5A — Fix 01: Ruff SIM108

## Symptom

`make phase5a-check` stops during backend lint/type with:

```text
SIM108 Use ternary operator ...
app/modules/reports/service.py:327
```

## Cause

The reporting service used a small `if/else` assignment that Ruff's
flake8-simplify rule requires to be expressed as a conditional expression.

## Fix

Only this assignment is changed:

```python
scope_budget_amount = (
    organization_budget_amount or ZERO if has_all_scope else allocated
)
```

No reporting formula, API contract, database schema, migration, seed, or
business rule changes.

## Apply

```bash
unzip -o SIMA_Phase5A_Fix01_Ruff_SIM108.zip   -d ~/projects/sima-budget

cd ~/projects/sima-budget/apps/backend
uv run ruff check . --fix
uv run ruff format .

cd ~/projects/sima-budget
make phase5a-check
```
