# Implementation Phase 0 — Repository & Tooling Scaffold

## Goal

Membuat repository runnable sebelum implementasi domain finansial dimulai.

## Deliverables

- [x] Monorepo directory structure
- [x] FastAPI skeleton
- [x] Liveness/readiness endpoints
- [x] PostgreSQL Compose service
- [x] Alembic skeleton
- [x] React + TypeScript + Vite shell
- [x] Responsive application shell placeholder
- [x] Backend/frontend tests skeleton
- [x] CI workflows
- [x] Security baseline docs
- [x] Test-case/log structure
- [x] CP-01 through CP-05 copied into repository
- [ ] `uv.lock` generated on connected development machine
- [ ] `package-lock.json` generated on connected development machine
- [ ] Full bootstrap verified on user's WSL + Docker environment

## Exit Criteria

Setelah dua lock file dihasilkan dan `make phase0-check` sukses pada development machine, Phase 0 dapat ditutup dan Phase 1 dimulai.

## Next

Phase 1:
- application settings;
- auth/session/CSRF;
- users;
- roles/permissions/scopes;
- organization units;
- audit infrastructure;
- real permission-aware app shell.
