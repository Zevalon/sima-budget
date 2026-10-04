# SIMA Phase 1D1 — Fix 01

Fixes mypy error:

```text
Argument 1 to "append" of "list" has incompatible type "ColumnElement[bool]";
expected "BinaryExpression[bool]"
```

Cause:
mypy inferred the dynamic SQLAlchemy filter list too narrowly.

Fix:
explicitly type the collection as:

```python
filters: list[ColumnElement[bool]] = []
```

Apply over the repository root and rerun:

```bash
cd ~/projects/sima-budget/apps/backend
uv run ruff check . --fix
uv run ruff format .

cd ~/projects/sima-budget
make phase1d1-check
```

No database reset, migration rollback, or dependency reinstall is required.
