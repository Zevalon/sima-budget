# SIMA Phase 4A — Realization Core

## Apply

```bash
cd ~/projects/sima-budget
git switch main
git pull --ff-only
git switch -c feature/phase-4a-realization-core

unzip -o SIMA_Phase4A_Realization_Core.zip -d ~/projects/sima-budget
chmod +x scripts/check-phase4a.sh

cd apps/backend
uv run ruff check . --fix
uv run ruff format .

cd ../frontend
npm run format

cd ~/projects/sima-budget
make phase4a-check
```

## Migration

```text
20261004_0007_phase4a_realizations
```

Do not reset PostgreSQL before the first gate run.
