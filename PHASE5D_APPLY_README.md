# SIMA Phase 5D — Apply Instructions

Start from `main` after Phase 5C is merged.

```bash
cd ~/projects/sima-budget
git switch main
git pull --ff-only
git status
git switch -c feature/phase-5d-reporting-hardening
```

Extract:

```bash
unzip -o SIMA_Phase5D_Reporting_Hardening.zip -d ~/projects/sima-budget
```

Then:

```bash
chmod +x ~/projects/sima-budget/scripts/check-phase5d.sh

cd ~/projects/sima-budget/apps/backend
uv run ruff check . --fix
uv run ruff format .

cd ~/projects/sima-budget/apps/frontend
npm run format

cd ~/projects/sima-budget
make phase5d-check
```

Expected final lines:

```text
Phase 5D reporting hardening verification: OK

Phase 5D checks passed.
```

No database migration, destructive reset, or new dependency is required.
