# SIMA Phase 2B2 — Annual Budget Approval & Rejection

## Before applying

Phase 2B1 must already be merged into `main` and your local `main` must be clean.

Create:

```bash
git switch main
git pull --ff-only
git switch -c feature/phase-2b2-annual-budget-approval
```

Extract this patch into the repository root.

Then run:

```bash
chmod +x scripts/check-phase2b2.sh

cd apps/backend
uv run ruff check . --fix
uv run ruff format .

cd ../frontend
npm run format

cd ../..
make phase2b2-check
```

No database migration is added by Phase 2B2.

## Expected

```text
Phase 2B2 annual budget approval verification: OK
Phase 2B2 checks passed.
```
