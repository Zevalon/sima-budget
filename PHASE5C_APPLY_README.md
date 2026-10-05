# SIMA Phase 5C - Apply Instructions

Start from `main` after Phase 5B has been merged.

```bash
cd ~/projects/sima-budget
git switch main
git pull --ff-only
git status
git switch -c feature/phase-5c-report-exports
```

Extract the patch into the repository root:

```bash
unzip -o SIMA_Phase5C_Report_Exports.zip -d ~/projects/sima-budget
```

Then:

```bash
chmod +x ~/projects/sima-budget/scripts/check-phase5c.sh

cd ~/projects/sima-budget/apps/backend
uv run ruff check . --fix
uv run ruff format .

cd ~/projects/sima-budget/apps/frontend
npm run format

cd ~/projects/sima-budget
make phase5c-check
```

Expected final lines:

```text
Phase 5C report export verification: OK

Phase 5C checks passed.
```

No database migration, destructive reset, or new Python package is required.
