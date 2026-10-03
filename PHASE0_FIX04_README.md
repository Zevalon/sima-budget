# SIMA Phase 0 — Fix 04

## Symptom

PostgreSQL container continuously restarts and logs:

```text
Database is uninitialized and superuser password is not specified.
You must specify POSTGRES_PASSWORD ...
```

## Cause

The development PostgreSQL container was created without a usable
`POSTGRES_PASSWORD` environment value.

## Fix

This patch:

1. explicitly loads the root `.env` through Compose `env_file`;
2. fails fast if `POSTGRES_PASSWORD` is not set;
3. uses the root `.env` explicitly with `docker compose --env-file .env`;
4. makes the healthcheck read POSTGRES values inside the container;
5. makes Phase 0 print PostgreSQL logs immediately if the container exits/restarts.

## One-time cleanup required

Because the current development database never initialized correctly,
remove its container and development volume before recreating it.

```bash
cd ~/projects/sima-budget

docker compose --env-file .env -f compose.dev.yml down -v --remove-orphans

docker compose --env-file .env -f compose.dev.yml up -d postgres

docker compose --env-file .env -f compose.dev.yml ps
```

Wait until PostgreSQL reports `healthy`, then:

```bash
make phase0-check
```

This cleanup is safe only because Phase 0 contains no valuable database data yet.
Do not use `down -v` casually once real development data matters.
