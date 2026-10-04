# SIMA Phase 3A — Fix 01: Explicit Financial Rounding

## Symptom

The Phase 3A unit test fails with:

```text
assert Decimal("308.62") == Decimal("308.63")
```

for:

```text
2.5000 × 123.45 = 308.625
```

## Cause

`Decimal.quantize()` uses the active decimal context rounding mode when no
rounding rule is supplied. The default Python context uses `ROUND_HALF_EVEN`.

For SIMA monetary line totals, we want the explicit business rule
`ROUND_HALF_UP`.

## Fix

Change:

```python
value.quantize(Decimal("0.01"))
```

to:

```python
value.quantize(
    Decimal("0.01"),
    rounding=ROUND_HALF_UP,
)
```

This makes monetary rounding deterministic and documents the financial rule
directly in code.

## Apply

```bash
unzip -o SIMA_Phase3A_Fix01_Financial_Rounding.zip \
  -d ~/projects/sima-budget

cd ~/projects/sima-budget/apps/backend
uv run ruff check . --fix
uv run ruff format .

cd ~/projects/sima-budget
make phase3a-check
```

No migration, seed reset, dependency reinstall, or database reset is required.
