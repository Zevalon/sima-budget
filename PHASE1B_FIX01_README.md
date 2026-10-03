# SIMA Phase 1B — Fix 01

Fixes the first Phase 1B Ruff gate:

- organize imports in `app/core/security.py`;
- remove unused `UUID` import in `app/modules/auth/service.py`;
- wrap the long foundation bootstrap error message in `scripts/bootstrap_admin.py`.

Apply over the repository root and rerun:

```bash
cd ~/projects/sima-budget
make phase1b-check
```

No database reset, migration rollback, dependency reinstall, or Docker volume deletion is required.
