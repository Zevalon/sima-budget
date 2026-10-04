# SIMA Phase 2B1 — Fix 02: Decimal Test Typing

## Symptom

mypy reports:

```text
Argument "amount" to "AnnualBudgetCreateRequest" has incompatible type "str";
expected "Decimal"
```

in:

```text
tests/unit/test_phase2b1_annual_budgets.py
```

## Cause

The application schema correctly declares monetary input as `Decimal`,
but the unit test instantiated the typed Pydantic model using string literals.

Pydantic can coerce those strings at runtime, but mypy validates the Python
constructor type statically and therefore rejects them.

## Fix

Use explicit `Decimal` objects in the test:

```python
amount=Decimal("500000000000.25")
```

and:

```python
amount=Decimal("0")
```

The strings remain inside `Decimal(...)` intentionally so decimal precision
is exact and no binary floating-point value is introduced.

## Apply

```bash
unzip -o SIMA_Phase2B1_Fix02_Decimal_Test_Typing.zip \
  -d ~/projects/sima-budget

cd ~/projects/sima-budget/apps/backend
uv run ruff check . --fix
uv run ruff format .

cd ~/projects/sima-budget
make phase2b1-check
```

No migration, dependency installation, or database reset is required.
