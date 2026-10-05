# SIMA Phase 5A — Apply Instructions

## Branch

```bash
git switch main
git pull --ff-only
git switch -c feature/phase-5a-reporting-foundation
```

## Apply patch

Extract the Phase 5A ZIP into the repository root.

Then:

```bash
chmod +x scripts/check-phase5a.sh

cd apps/backend
uv run ruff check . --fix
uv run ruff format .

cd ../frontend
npm run format

cd ../..
make phase5a-check
```

Expected final lines:

```text
Phase 5A reporting foundation verification: OK
Phase 5A checks passed.
```

## Database

Phase 5A has no new Alembic migration. Do not reset PostgreSQL or delete Docker volumes before the first gate.

For browser smoke testing after the gate, refreshing the deterministic development seed is recommended:

```bash
make dev-seed-reset CONFIRM=RESET
```

Then login with a seeded user and open **Laporan** for FY2025.
