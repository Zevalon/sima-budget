# SIMA Phase 2C — Development Seed Baseline

This patch adds a deterministic local development seed for every table implemented through Phase 2C.

## Why

Manual smoke-test data had started to affect regression checks and made UI states depend on whatever had been created previously. From this point forward, development data is disposable and reproducible.

## First application (destructive)

```bash
cd ~/projects/sima-budget
make dev-seed-reset CONFIRM=RESET
```

This deletes **all current application rows** in the local development database, preserves the schema/Alembic migration state, recreates foundation data, and inserts the seed baseline.

The command refuses to run unless:

- `APP_ENV=development`;
- the database host is local;
- the database name is an approved SIMA development name;
- `CONFIRM=RESET` is supplied.

## Later refresh

```bash
make dev-seed
```

Future phases that introduce new tables must extend `apps/backend/scripts/seed_dev.py`. Use `make dev-seed` for normal refreshes and only use the destructive reset when a clean baseline is desired.

## Seed credentials

Default local development password for all seed accounts:

```text
SimaDev-2026!
```

It can be overridden with `DEV_SEED_PASSWORD`.

Main accounts:

```text
sysadmin
budgetadmin
management
auditor
viewer
itpic
itapprover
ftipic
ftiapprover
```

## Primary Phase 2C scenario

```text
FY2026          PLANNING
Annual Budget   APPROVED / Rp 600.000.000.000,00
Allocated       Rp 300.000.000.000,00
Remaining       Rp 300.000.000.000,00
```

Several active `can_receive_budget=true` units intentionally remain unallocated so the Alokasi Unit create form is immediately testable.
