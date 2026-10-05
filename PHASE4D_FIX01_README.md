# SIMA Phase 4D — Fix 01: mypy RealizationStatus in Unit Tests

## Symptom

`make phase4d-check` fails during backend type checking with errors such as:

```text
Argument "expected_status" ... has incompatible type "str";
expected "RealizationStatus"
```

Affected tests:

- `tests/unit/test_phase4a_realizations.py`
- `tests/unit/test_phase4b_realization_workflow.py`

## Cause

Phase 4D hardening makes `expected_status` explicitly typed as the
`RealizationStatus` enum. The older tests still passed raw strings such as
`"DRAFT"` and `"REVERSED"`.

Pydantic may coerce these strings at runtime, but mypy correctly rejects them
at static type-check time.

## Fix

Use the enum directly:

```python
RealizationStatus.DRAFT
RealizationStatus.REVERSED
```

No production code, API contract, database schema, or business logic changes.

## Apply

```bash
unzip -o SIMA_Phase4D_Fix01_Mypy_RealizationStatus.zip \
  -d ~/projects/sima-budget

cd ~/projects/sima-budget/apps/backend
uv run ruff format .
uv run ruff check . --fix
uv run mypy app tests scripts

cd ~/projects/sima-budget
make phase4d-check
```

No database reset, seed reset, migration rollback, or Docker-volume deletion is
required.
