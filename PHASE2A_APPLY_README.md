# SIMA Phase 2A — Fiscal Year & Budget Master Foundation

Phase 2A begins the budget domain after completion of CP-06 / Phase 1.

## Included

- Fiscal Year model and lifecycle
- controlled Fiscal Year reopen
- one ACTIVE Fiscal Year per organization
- Budget Category master
- Unit of Measure master
- Phase 2A permissions and Budget Administrator grants
- permission-aware Master Data UI
- global Fiscal Year selector foundation
- migration, tests, audit, and regression gate

## Apply

Start from the latest merged Phase 1 `main`:

```bash
cd ~/projects/sima-budget
git switch main
git pull --ff-only
git switch -c feature/phase-2a-fiscal-year-master
```

Extract this package over the repository root, then:

```bash
chmod +x scripts/check-phase2a.sh

cd apps/backend
uv run ruff check . --fix
uv run ruff format .

cd ../frontend
npm run format

cd ~/projects/sima-budget
make phase2a-check
```

## Important

This phase adds a real Alembic migration. Do not delete the PostgreSQL volume.

The bootstrap is intentionally rerun so existing system roles receive the newly introduced Phase 2A permissions according to the approved role template.

`SYSTEM_ADMIN` receives Phase 2A read permissions only. Financial/master-data mutation authority is assigned to `BUDGET_ADMIN`, preserving the separation between technical administration and budget authority.
