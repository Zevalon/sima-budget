# SIMA Phase 2C — Unit Allocation

This patch must be applied after Phase 2B2 has been merged into `main`.

## Main additions

- `unit_allocations` PostgreSQL table;
- Decimal / NUMERIC allocation values;
- approved Annual Budget prerequisite;
- PLANNING-only allocation mutation;
- eligible organization-unit validation;
- total allocation <= Annual Budget invariant;
- PostgreSQL row locking for concurrency-safe aggregate validation;
- allocation create/update audit trail;
- allocation permission model;
- Alokasi Unit frontend page;
- Phase 2C regression and concurrency verifier.

## Apply

```bash
cd ~/projects/sima-budget
git switch main
git pull --ff-only
git switch -c feature/phase-2c-unit-allocation

unzip -o "/mnt/c/Users/Rafli Apriansyah/Downloads/SIMA_Phase2C_Unit_Allocation.zip" \
  -d ~/projects/sima-budget

chmod +x ~/projects/sima-budget/scripts/check-phase2c.sh

cd ~/projects/sima-budget/apps/backend
uv run ruff check . --fix
uv run ruff format .

cd ~/projects/sima-budget/apps/frontend
npm run format

cd ~/projects/sima-budget
make phase2c-check
```

Expected final markers:

```text
Phase 2C unit allocation verification: OK
Phase 2C checks passed.
```

## Database

This phase adds migration:

```text
20261004_0004_phase2c_unit_allocations
```

The gate runs `alembic upgrade head` automatically.

Do not delete the PostgreSQL volume.
