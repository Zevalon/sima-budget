# SIMA Phase 1C2 — Apply

Start from updated main after Phase 1C1 merge:

```bash
cd ~/projects/sima-budget
git switch main
git pull --ff-only
git switch -c feature/phase-1c2-administration
```

Apply the ZIP over the repository root, then:

```bash
chmod +x scripts/check-phase1c2.sh

cd apps/backend
uv run ruff format .

cd ../frontend
npm run format

cd ~/projects/sima-budget
make phase1c2-check
```

No database reset or new Alembic migration is required.

If the automated gate passes, run the application and manually test Administration.
