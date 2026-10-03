# SIMA Phase 0 — Fix 08

## Fix A — Vitest vs Playwright isolation

Vitest previously discovered:

```text
e2e/smoke.spec.ts
```

and attempted to execute a Playwright test.

`vite.config.ts` now restricts Vitest discovery to:

```text
tests/**/*.test.{ts,tsx}
tests/**/*.spec.{ts,tsx}
```

Therefore:

- Vitest owns `tests/`
- Playwright owns `e2e/`

## Fix B — OpenAPI export path

The Phase 0 checker previously used:

```text
../../../docs/api/openapi.json
```

from `apps/backend`, which points outside the repository.

It now correctly uses:

```text
../../docs/api/openapi.json
```

and verifies that `docs/api/openapi.json` was actually created.

## Apply

Extract over the project root:

```bash
unzip -o SIMA_Phase0_Fix08.zip -d ~/projects/sima-budget
chmod +x ~/projects/sima-budget/scripts/check-phase0.sh
```

Then:

```bash
cd ~/projects/sima-budget
make phase0-check
```

No database reset, bootstrap, or dependency reinstall is required.
