# Phase 1C1 RBAC Test Cases

## RBAC-001 — System Administrator read access

Expected:
- users: 200
- roles: 200
- permissions: 200
- organization units: 200

## RBAC-002 — Viewer restriction

Expected:
- users: 403
- organization units: 200

## RBAC-003 — Existing authentication regression

Expected:
Phase 1B gate remains green before RBAC-specific verification begins.

## Gate

```bash
make phase1c1-check
```
