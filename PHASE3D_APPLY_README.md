# SIMA Phase 3D — Budget Plan Hardening & Phase 3 Completion

Phase 3D hardens submit/approval workflow identity and adds scoped financial summary cards.

## Apply

Start from merged Phase 3C `main`:

```bash
cd ~/projects/sima-budget
git switch main
git pull --ff-only
git switch -c feature/phase-3d-budget-plan-hardening

unzip -o "/mnt/c/Users/Rafli Apriansyah/Downloads/SIMA_Phase3D_Budget_Plan_Hardening.zip" \
  -d ~/projects/sima-budget

chmod +x ~/projects/sima-budget/scripts/check-phase3d.sh

cd ~/projects/sima-budget/apps/backend
uv run ruff check . --fix
uv run ruff format .

cd ~/projects/sima-budget/apps/frontend
npm run format

cd ~/projects/sima-budget
make phase3d-check
```

## Database

No new migration is introduced in Phase 3D. Do not reset or delete the PostgreSQL volume.

## Seed

The persistent schema and baseline scenarios are unchanged, so no mandatory seed extension is
required. After the gate, you may run the normal development reset before browser smoke:

```bash
make dev-seed-reset CONFIRM=RESET
```

## Expected result

```text
Phase 3D budget plan hardening verification: OK
Phase 3D checks passed.
```
