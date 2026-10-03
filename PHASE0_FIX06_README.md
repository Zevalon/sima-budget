# SIMA Phase 0 — Fix 06 (Backend Ruff lint)

## Symptom

Phase 0 reaches `[4/6] Backend lint/type` and Ruff reports:

- `I001` import order in `alembic/env.py`
- `F401` unused `typing.Any` in `app/core/errors.py`
- `E402` late import in `scripts/export_openapi.py`

## Fix

1. Reorders Alembic/SQLAlchemy imports according to Ruff.
2. Removes the unused `Any` import.
3. Keeps the OpenAPI exporter's intentional late import after `sys.path`
   initialization and marks that single line with `# noqa: E402`.

The `E402` exception is intentional because the standalone script must add
the backend root to `sys.path` before importing `app.main`.

## Apply

Extract this ZIP over the project root, then:

```bash
cd ~/projects/sima-budget
make phase0-check
```

No Docker volume cleanup or dependency reinstall is needed for Fix 06.
