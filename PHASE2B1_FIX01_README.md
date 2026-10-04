# SIMA Phase 2B1 — Fix 01: FastAPI Query Annotation

## Symptom

Ruff reports:

```text
B008 Do not perform function call `Query` in argument defaults
```

at:

```python
fiscal_year_id: UUID | None = Query(default=None)
```

## Cause

The FastAPI query declaration uses a function call directly as a parameter
default. Ruff rule B008 rejects this pattern.

## Fix

Use FastAPI's `Annotated` form instead:

```python
fiscal_year_id: Annotated[UUID | None, Query()] = None
```

This preserves the API behavior while satisfying Ruff.

## Apply

```bash
unzip -o SIMA_Phase2B1_Fix01_Query_Annotation.zip \
  -d ~/projects/sima-budget

cd ~/projects/sima-budget/apps/backend
uv run ruff check . --fix
uv run ruff format .

cd ~/projects/sima-budget
make phase2b1-check
```

No database reset or migration change is required.
