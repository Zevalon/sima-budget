# SIMA Phase 1B — Fix 02

## Symptom

`make phase1b-check` reaches mypy and reports:

```text
app/modules/auth/repository.py:15:
error: Returning Any from function declared to return "User | None" [no-any-return]
```

## Cause

The configured SQLAlchemy/mypy typing path does not infer a precise return
type for `AsyncSession.scalar()` in this query.

## Fix

Use:

```python
result = await session.execute(select(User)...)
return result.scalar_one_or_none()
```

This preserves the same query semantics while giving mypy the correct
`User | None` type.

## Apply

Extract over the repository root and rerun:

```bash
cd ~/projects/sima-budget
make phase1b-check
```

No database reset, Alembic rollback, dependency reinstall, or Docker volume deletion is required.
