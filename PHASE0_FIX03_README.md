# SIMA Phase 0 — Fix 03

## Symptom

`make phase0-check` passes backend tests but fails at:

```text
[3/6] Database migration and readiness
psycopg.OperationalError:
connection to server at "127.0.0.1", port 5432 failed: Connection refused
```

## Cause

The Phase 0 checker assumed PostgreSQL had already been started by bootstrap.

After Docker/Desktop/WSL restart, the development PostgreSQL container may not be running yet.

## Fix

`check-phase0.sh` now:

1. verifies Docker engine is active;
2. starts the PostgreSQL development service;
3. waits up to 60 seconds for `pg_isready`;
4. runs Alembic only after PostgreSQL is ready;
5. performs the application-level database ping.

## Manual immediate fix

```bash
cd ~/projects/sima-budget
make dev-db-up
make dev-db-status
make phase0-check
```

If Docker is not active, start Docker Desktop first.

## Diagnostics

```bash
docker compose -f compose.dev.yml ps
docker compose -f compose.dev.yml logs postgres
```
