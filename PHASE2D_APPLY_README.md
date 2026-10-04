# SIMA Phase 2D — Budget Foundation Hardening & Completion

Apply only after Phase 2C has been merged into `main`.

## Main additions

- optimistic concurrency protection for Unit Allocation edits;
- open-year allocation protection on organization-unit eligibility/deactivation;
- real Budget Foundation dashboard summary;
- clearer Unit Allocation empty/locked states;
- frontend Fast Refresh warning cleanup;
- Phase 1D2 verifier cleanup warning fix;
- final Phase 2 hardening verifier and gate.

## Apply

```bash
cd ~/projects/sima-budget
git switch main
git pull --ff-only
git switch -c feature/phase-2d-budget-foundation-hardening

unzip -o "/mnt/c/Users/Rafli Apriansyah/Downloads/SIMA_Phase2D_Budget_Foundation_Hardening.zip" \
  -d ~/projects/sima-budget

chmod +x ~/projects/sima-budget/scripts/check-phase2d.sh

cd ~/projects/sima-budget/apps/backend
uv run ruff check . --fix
uv run ruff format .

cd ~/projects/sima-budget/apps/frontend
npm run format

cd ~/projects/sima-budget
make phase2d-check
```

Expected final markers:

```text
Phase 2D budget foundation hardening verification: OK
Phase 2D checks passed.
```

## Database

No new migration is required.

Do not reset PostgreSQL or remove the Docker volume.

The deterministic Development Seed Baseline remains compatible with Phase 2D.
