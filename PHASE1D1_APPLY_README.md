# SIMA Phase 1D1 — Apply

Start from the latest `main` after Phase 1C2:

```bash
cd ~/projects/sima-budget
git switch main
git pull --ff-only
git switch -c feature/phase-1d1-audit-settings
```

Extract this package over the repository root, then:

```bash
chmod +x scripts/check-phase1d1.sh

cd apps/backend
uv run ruff check . --fix
uv run ruff format .

cd ../frontend
npm run format

cd ~/projects/sima-budget
make phase1d1-check
```

No database reset and no new Alembic migration are required.
