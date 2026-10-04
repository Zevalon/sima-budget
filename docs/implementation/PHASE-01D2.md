# Implementation Phase 1D2 — Foundation Hardening

Phase 1D2 is the final implementation slice of Phase 1 before budget-domain work begins.

## Security hardening

- preserves at least one active `SYSTEM_ADMIN` with `ALL` scope;
- prevents built-in system roles from being deactivated;
- prevents manual permission replacement on built-in system roles;
- adds administrative session revocation;
- password reset and user deactivation revoke sessions instead of silently deleting them;
- organization units cannot be deactivated while referenced by active users or active role scopes;
- permission-denied frontend routes display an explicit access-denied state.

## UX hardening

- Administration navigation now also recognizes settings/audit-only permissions;
- authenticated application shell uses configurable application and organization display names;
- user list exposes `Cabut Session` when permitted;
- user and audit tables have explicit empty states;
- Audit Log supports pagination and clearing filters.

## Validation

```bash
make phase1d2-check
```

Expected final output:

```text
Foundation hardening verification: OK
Phase 1D2 checks passed.
```

After this gate and browser smoke testing are green, Phase 1 is ready for its final checkpoint.
