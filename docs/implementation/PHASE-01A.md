# Implementation Phase 1A — Identity & Database Foundation

**Status:** IMPLEMENTED — requires workstation validation.

## Scope

Phase 1A establishes persistent identity, organization, RBAC, session, and audit data structures.

Tables:

- organizations
- application_settings
- organization_unit_types
- organization_units
- users
- user_unit_memberships
- roles
- permissions
- role_permissions
- user_role_assignments
- user_sessions
- audit_logs

## Bootstrap

The idempotent foundation bootstrap creates:

- one default organization (`DEFAULT`);
- SIMA application settings;
- eight default organization unit types;
- one root organization unit;
- foundation permission catalog;
- seven default role templates;
- role-permission mappings.

It intentionally does **not** create a default administrator password/user.

First administrator creation is deferred to Phase 1B, when authentication/session behavior is implemented.

## Validation

Run:

```bash
chmod +x scripts/check-phase1a.sh
make phase1a-check
```

Expected final output:

```text
Phase 1A checks passed.
```

## Important

The bootstrap is idempotent and is run twice by the Phase 1A checker to detect duplicate-seed behavior.
