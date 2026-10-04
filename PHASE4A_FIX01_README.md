# SIMA Phase 4A — Fix 01: HTTPX Client Lifecycle

## Symptom

`make phase4a-check` reaches the Phase 4A verifier and fails with:

```text
RuntimeError: Cannot open a client instance more than once.
```

The failure occurs at:

```python
async with client:
```

## Cause

`login_client()` creates an `httpx.AsyncClient` and immediately performs the
login request. Performing that request already opens the client.

The verifier then tries to enter the same client again with:

```python
async with client:
```

Recent HTTPX versions reject this second open.

## Fix

Keep using the already-open client returned by `login_client()` and manage its
cleanup explicitly:

```python
client, headers = await login_client()
try:
    ...
finally:
    await client.aclose()
```

The same correction is applied to the final context verification client.

No Realization business logic, API behavior, schema, or database migration is
changed.

## Apply

```bash
unzip -o SIMA_Phase4A_Fix01_HTTPX_Client_Lifecycle.zip \
  -d ~/projects/sima-budget

cd ~/projects/sima-budget/apps/backend
uv run ruff format .
uv run ruff check . --fix

cd ~/projects/sima-budget
make phase4a-check
```

No database reset, seed reset, migration rollback, Docker-volume deletion, or
dependency reinstall is required.
