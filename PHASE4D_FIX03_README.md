# SIMA Phase 4D — Fix 03: Stable Fiscal Year Test Mock

## Symptom

`npm run test` fails in:

```text
tests/realization-hardening.test.tsx
```

with:

```text
TypeError: Cannot read properties of undefined (reading 'length')
```

at:

```tsx
{items.length} record
```

## Cause

The test's `useFiscalYear()` mock returned a new `selectedFiscalYear` object on
every React render.

`RealizationsPage` memoizes `reload()` with:

```tsx
useCallback(..., [selectedFiscalYear])
```

so a new fiscal-year object changes `reload`, which causes the effect that
depends on `reload` to execute again.

The previous test fix provided only two `listRealizations()` results. Repeated
reloads eventually exhausted those one-time results and the mock returned
`undefined`, which was assigned to `items`.

## Fix

The fiscal-year object is now created once through `vi.hoisted()` and the same
reference is returned for every render.

The realization list mock also uses:

- one `POSTED` result for the initial load;
- a persistent `REVERSED` result for the post-reversal reload.

The test waits for the post-reversal UI and both reload requests to finish
before teardown.

No production application code, API contract, backend logic, database schema,
or financial rules are changed.

## Apply

```bash
unzip -o SIMA_Phase4D_Fix03_Stable_Fiscal_Year_Test_Mock.zip \
  -d ~/projects/sima-budget

cd ~/projects/sima-budget/apps/frontend
npm run format
npm run test

cd ~/projects/sima-budget
make phase4d-check
```

No database reset, seed reset, migration rollback, Docker-volume deletion, or
dependency reinstall is required.
