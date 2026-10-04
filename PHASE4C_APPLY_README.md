# SIMA Phase 4C — Realization Aggregates & Monitoring

## Apply

Start from `main` after Phase 4B has been merged.

```bash
cd ~/projects/sima-budget
git switch main
git pull --ff-only
git status
git switch -c feature/phase-4c-realization-monitoring

unzip -o SIMA_Phase4C_Realization_Aggregates_Monitoring.zip \
  -d ~/projects/sima-budget
chmod +x ~/projects/sima-budget/scripts/check-phase4c.sh

cd ~/projects/sima-budget/apps/backend
uv run ruff check . --fix
uv run ruff format .

cd ~/projects/sima-budget/apps/frontend
npm run format

cd ~/projects/sima-budget
make phase4c-check
```

No new Alembic migration is required in Phase 4C. Do not reset PostgreSQL before the first gate.

Expected final output:

```text
Phase 4C realization aggregates and monitoring verification: OK
Phase 4C checks passed.
```
