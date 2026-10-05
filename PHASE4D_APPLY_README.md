# SIMA Phase 4D — Realization Hardening & Phase 4 Completion

Phase 4D hardens realization mutations so every state-changing request is tied to the exact browser snapshot being acted on.

## Main hardening

Mutation requests now carry:

```text
expected_row_version
expected_status
expected_plan_version_id
```

The backend rejects the request with `409 Conflict` if any of the three no longer matches.

This applies to:

- draft update;
- posting;
- cancellation;
- reversal;
- correction creation.

Creating a correction also increments the source realization's `row_version`, so the source record itself reflects that its workflow relationship changed.

## Apply

```bash
unzip -o SIMA_Phase4D_Realization_Hardening.zip \
  -d ~/projects/sima-budget

chmod +x ~/projects/sima-budget/scripts/check-phase4d.sh

cd ~/projects/sima-budget/apps/backend
uv run ruff check . --fix
uv run ruff format .

cd ~/projects/sima-budget/apps/frontend
npm run format

cd ~/projects/sima-budget
make phase4d-check
```

No database migration is required for Phase 4D.
