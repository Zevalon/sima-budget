# SIMA Phase 1A — Fix 01

## Symptom

`make phase1a-check` reaches backend lint/type and Ruff reports:

```text
SIM300 Yoda condition detected
tests/unit/test_foundation_models.py
```

## Cause

The test used:

```python
assert EXPECTED_FOUNDATION_TABLES <= set(Base.metadata.tables)
```

The assertion is logically correct, but Ruff's SIM300 rule prefers a non-Yoda
comparison.

## Fix

The assertion is now:

```python
assert EXPECTED_FOUNDATION_TABLES.issubset(Base.metadata.tables)
```

## Apply

Extract this ZIP over the repository root:

```bash
unzip -o SIMA_Phase1A_Fix01.zip -d ~/projects/sima-budget
```

Then rerun:

```bash
cd ~/projects/sima-budget
make phase1a-check
```

No database reset, rollback, bootstrap reinstall, or volume deletion is required.
The Phase 1A Alembic migration already applied successfully and should remain in place.
