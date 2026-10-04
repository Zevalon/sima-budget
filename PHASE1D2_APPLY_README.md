# SIMA Phase 1D2 — Apply

Start from the latest `main` after Phase 1D1 has been merged:

```bash
cd ~/projects/sima-budget
git switch main
git pull --ff-only
git switch -c feature/phase-1d2-foundation-hardening
```

Extract this package over the repository root, then run:

```bash
chmod +x scripts/check-phase1d2.sh

cd apps/backend
uv run ruff check . --fix
uv run ruff format .

cd ../frontend
npm run format

cd ~/projects/sima-budget
make phase1d2-check
```

No database reset and no new Alembic migration are required.

When the automated gate passes, manually verify:

- application/organization names reflect saved settings after a fresh login;
- Administration remains visible for accounts with only settings/audit view access;
- unauthorized administration routes show an access-denied screen;
- `Cabut Session` logs another user out;
- Audit Log pagination/filter controls work.
