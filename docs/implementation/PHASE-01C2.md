# Implementation Phase 1C2 — Administration Management

## Scope

Phase 1C2 adds real administration write operations and permission-aware frontend screens.

Implemented backend capabilities:

- create/update/deactivate users;
- reset user password and revoke active sessions;
- replace user role assignments;
- create/update roles;
- replace role permissions;
- create/update/deactivate organization units;
- prevent hierarchy cycles;
- protect all mutations with CSRF;
- require `ALL` scope for system-wide administration writes;
- audit administration mutations.

Implemented frontend:

- permission-aware Administration menu;
- Administration landing page;
- user management screen;
- role/permission screen;
- organization unit screen;
- route-level permission guards.

## Validation

```bash
chmod +x scripts/check-phase1c2.sh
make phase1c2-check
```

Expected final output:

```text
Administration mutation verification: OK
Phase 1C2 checks passed.
```

## Manual smoke

After automated checks:

1. login as System Administrator;
2. open Administration;
3. create a temporary unit;
4. create a temporary role;
5. create a temporary user;
6. verify menu visibility follows permission;
7. deactivate temporary user/unit when finished.
