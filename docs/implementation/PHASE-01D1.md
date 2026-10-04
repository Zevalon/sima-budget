# Implementation Phase 1D1 — Audit Log & Application Settings

Phase 1D1 exposes two existing foundation capabilities as operational features.

## Application Settings

API:

```text
GET   /api/v1/settings
PATCH /api/v1/settings
```

Rules:
- read requires `settings.view`;
- update requires `settings.update` with `ALL` scope;
- update requires valid CSRF;
- update is audited.

## Audit Log

API:

```text
GET /api/v1/audit
```

Supported filters:
- `action`
- `entity_type`
- `limit`
- `offset`

Access requires `audit.view`.

## UI

Administration now contains:
- Pengaturan Aplikasi
- Audit Log

Both are permission-aware.

## Gate

```bash
make phase1d1-check
```

Expected final output:

```text
Foundation administration verification: OK
Phase 1D1 checks passed.
```
