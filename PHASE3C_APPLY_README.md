# SIMA Phase 3C — Commitment & Available Budget Controls

Phase 3C makes APPROVED Budget Plans consume Unit Allocation capacity.

Core rule:

```text
Unit Allocation - Committed Approved Plans = Available
```

DRAFT and PENDING_APPROVAL plans remain a separate Draft Pipeline and do not reduce official Available budget.

Key controls:

- approval locks the Unit Allocation row;
- concurrent approvals cannot jointly exceed Unit Allocation;
- reducing an allocation below existing committed plans is rejected;
- Budget Plan context exposes Allocated / Committed / Pipeline / Available;
- Unit Allocation overview and Dashboard expose commitment metrics;
- development seed includes an APPROVED Budget Plan commitment scenario.

No new database migration is required.

Apply and validate:

```bash
chmod +x scripts/check-phase3c.sh
cd apps/backend
uv run ruff check . --fix
uv run ruff format .
cd ../frontend
npm run format
cd ../..
make phase3c-check
```
