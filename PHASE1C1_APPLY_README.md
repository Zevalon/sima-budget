# SIMA Phase 1C1 — Apply

Recommended Git workflow:

```bash
cd ~/projects/sima-budget
git checkout main
git pull
git checkout -b feature/phase-1c1-rbac-admin-api
```

Apply the patch:

```bash
unzip -o SIMA_Phase1C1_RBAC_Admin_API.zip -d ~/projects/sima-budget
chmod +x ~/projects/sima-budget/scripts/check-phase1c1.sh
```

Normalize backend formatting:

```bash
cd ~/projects/sima-budget/apps/backend
uv run ruff format .
```

Run the gate:

```bash
cd ~/projects/sima-budget
make phase1c1-check
```

No database reset or new migration is required in Phase 1C1.
