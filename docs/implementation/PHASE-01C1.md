# Implementation Phase 1C1 — RBAC Evaluation & Administration API

## Purpose

Phase 1C1 turns the RBAC data model from Phase 1A into enforceable authorization behavior.

## Implemented

- permission evaluation from active role assignments;
- role validity window handling;
- data scope foundation:
  - OWN
  - OWN_UNIT
  - OWN_UNIT_AND_CHILDREN
  - ALL
- unit hierarchy access evaluation;
- reusable FastAPI permission dependency;
- read-only administration endpoints.

## API

```text
GET /api/v1/admin/users
GET /api/v1/admin/roles
GET /api/v1/admin/permissions
GET /api/v1/admin/organization-units
```

Permissions:

```text
/admin/users               -> users.view
/admin/roles               -> roles.view
/admin/permissions         -> permissions.view
/admin/organization-units  -> organization_units.view
```

## Validation

```bash
chmod +x scripts/check-phase1c1.sh
make phase1c1-check
```

The validation creates temporary System Administrator and Viewer accounts.

Expected behavior:

- System Administrator can access all four administration read endpoints.
- Viewer cannot access `/admin/users`.
- Viewer can access `/admin/organization-units`.

Expected final line:

```text
Administration authorization verification: OK
Phase 1C1 checks passed.
```

## Next

Phase 1C2 adds administration write operations and frontend management screens.
