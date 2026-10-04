# SIMA Phase 3A — Fix 02: Initial Plan Version Total

## Symptom

`make phase3a-check` fails while creating a Budget Plan with:

```text
psycopg.errors.CheckViolation:
new row for relation "budget_plan_versions" violates check constraint
"ck_budget_plan_version_total_nonnegative"
```

The failing row shows:

```text
total_amount = 0.00
```

## Cause

`create_budget_plan()` already calculates the final plan total before creating
the version, but the first `BudgetPlanVersion` was temporarily initialized with:

```python
total_amount=Decimal("0.00")
```

and immediately flushed to PostgreSQL.

The database constraint requires a positive total. Phase 3A request schemas also
require at least one item, positive quantity, and positive unit price, so a
created plan version should never need a temporary zero total.

## Fix

Initialize the first version with the already calculated total:

```python
total_amount=total
```

instead of:

```python
total_amount=Decimal("0.00")
```

The later item replacement/recalculation remains in place as an additional
consistency step.

This patch is cumulative and also preserves Fix 01 (`ROUND_HALF_UP`).

## Apply

```bash
unzip -o SIMA_Phase3A_Fix02_Initial_Version_Total.zip \
  -d ~/projects/sima-budget

cd ~/projects/sima-budget/apps/backend
uv run ruff check . --fix
uv run ruff format .

cd ~/projects/sima-budget
make phase3a-check
```

No Alembic migration, database reset, seed reset, or dependency reinstall is
required.
