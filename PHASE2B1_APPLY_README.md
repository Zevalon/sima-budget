# SIMA Phase 2B1 — Annual Budget Core & Submission

Phase 2B is intentionally split into two implementation slices:

- Phase 2B1 — Annual Budget core + submission workflow
- Phase 2B2 — management approval / rejection + self-approval policy

Phase 2B1 introduces the annual organization-wide budget while keeping approval
execution out of scope until the next slice.

## Main additions

- `annual_budgets` table using PostgreSQL `NUMERIC(20,2)` / Python `Decimal`
- one annual budget per fiscal year
- DRAFT editing
- submission to `PENDING_APPROVAL`
- immutable-after-submission behavior until an approval decision exists
- approval-submission history foundation
- audit events
- permission-aware Annual Budget UI
- System Administrator read-only separation
- Budget Administrator create/update/submit authority

## Apply

```bash
cd ~/projects/sima-budget
git switch main
git pull --ff-only
git switch -c feature/phase-2b1-annual-budget-core

unzip -o "/mnt/c/Users/Rafli Apriansyah/Downloads/SIMA_Phase2B1_Annual_Budget_Core.zip" \
  -d ~/projects/sima-budget

chmod +x ~/projects/sima-budget/scripts/check-phase2b1.sh

cd ~/projects/sima-budget/apps/backend
uv run ruff check . --fix
uv run ruff format .

cd ~/projects/sima-budget/apps/frontend
npm run format

cd ~/projects/sima-budget
make phase2b1-check
```

No database reset is required. A new Alembic migration is included and the gate
runs `alembic upgrade head`.

Expected final output:

```text
Phase 2B1 annual budget core verification: OK
Phase 2B1 checks passed.
```
