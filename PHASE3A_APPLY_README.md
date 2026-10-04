# SIMA Phase 3A — Budget Plan Core & Versioned Items

Phase 3A introduces unit-scoped draft Budget Plans on top of Unit Allocation.

## Scope

- `BudgetPlan` header tied to Fiscal Year, Unit Allocation, and Organization Unit.
- `BudgetPlanVersion` snapshot container.
- `BudgetPlanItem` detail rows.
- quantity × unit price calculated on the backend using Decimal.
- draft total may not exceed the source Unit Allocation.
- `UNIT_PIC` receives scoped view/create/update permissions.
- Budget Admin/System Admin receive read access only.
- `OWN_UNIT` and `OWN_UNIT_AND_CHILDREN` are enforced by the backend.
- optimistic row-version protection for draft edits.
- development seed extended with FY2026 draft plans.
- frontend Rencana Anggaran page enabled.

## Important Phase Boundary

Phase 3A does **not** commit budget and does not provide plan approval yet.

Draft plans do not consume official committed allocation. Phase 3B/3C will add
submission, approval, immutable approved versions, and aggregate commitment
controls.

## Apply

Start from the latest merged `main`:

```bash
cd ~/projects/sima-budget
git switch main
git pull --ff-only
git switch -c feature/phase-3a-budget-plan-core

unzip -o "/mnt/c/Users/Rafli Apriansyah/Downloads/SIMA_Phase3A_Budget_Plan_Core.zip" \
  -d ~/projects/sima-budget

chmod +x ~/projects/sima-budget/scripts/check-phase3a.sh

cd ~/projects/sima-budget/apps/backend
uv run ruff check . --fix
uv run ruff format .

cd ~/projects/sima-budget/apps/frontend
npm run format

cd ~/projects/sima-budget
make phase3a-check
```

## Expected gate

```text
Phase 3A budget plan core verification: OK

Phase 3A checks passed.
```

## Seed

Phase 3A extends the cumulative development seed. After the gate passes, reset
the local development dataset when you are ready to smoke-test the new page:

```bash
make dev-seed-reset CONFIRM=RESET
```

All existing seeded development accounts continue to use `DEV_SEED_PASSWORD`.
