# SIMA Phase 0 — Fix 05 (PostgreSQL 18 volume layout)

## Root cause

PostgreSQL official Docker image 18+ changed its storage layout.

For PostgreSQL 18:

```text
PGDATA=/var/lib/postgresql/18/docker
```

The persistent Docker volume must be mounted at:

```text
/var/lib/postgresql
```

The previous SIMA scaffold incorrectly used the pre-18 mount:

```text
/var/lib/postgresql/data
```

PostgreSQL 18 detects that as an old/unused database layout and exits.

## Important one-time cleanup

Phase 0 contains no valuable DB data yet, so remove the old development
container and volume after applying this patch:

```bash
cd ~/projects/sima-budget

docker compose --env-file .env -f compose.dev.yml down -v --remove-orphans
```

Then confirm no old SIMA PostgreSQL volume remains:

```bash
docker volume ls --format '{{.Name}}' | grep -E 'sima.*postgres' || true
```

If an old SIMA development PostgreSQL volume is still listed, remove ONLY
that SIMA development volume by its exact name:

```bash
docker volume rm <EXACT_SIMA_POSTGRES_VOLUME_NAME>
```

Then recreate:

```bash
docker compose --env-file .env -f compose.dev.yml up -d postgres
docker compose --env-file .env -f compose.dev.yml ps
```

Expected status:

```text
Up ... (healthy)
```

Finally:

```bash
make phase0-check
```

## Safety note

Do not use `down -v` or delete PostgreSQL volumes casually once the project
contains important data.
