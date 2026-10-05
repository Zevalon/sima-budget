# SIMA Phase 5B — Apply Instructions

Start from `main` after Phase 5A has been merged.

```bash
cd ~/projects/sima-budget
git switch main
git pull --ff-only
git status
git switch -c feature/phase-5b-reports-ui-filters
```

Extract the patch into the repository root:

```bash
unzip -o SIMA_Phase5B_Reports_UI_Filters.zip -d ~/projects/sima-budget
```

Then:

```bash
chmod +x ~/projects/sima-budget/scripts/check-phase5b.sh

cd ~/projects/sima-budget/apps/backend
uv run ruff check . --fix
uv run ruff format .

cd ~/projects/sima-budget/apps/frontend
npm run format

cd ~/projects/sima-budget
make phase5b-check
```

Expected final lines:

```text
Phase 5B report filter verification: OK

Phase 5B checks passed.
```

No database migration or destructive database reset is required before the automated gate.
