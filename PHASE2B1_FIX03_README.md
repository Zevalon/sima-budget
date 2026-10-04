# SIMA Phase 2B1 — Fix 03: Annual Budget Async Test Teardown

## Symptom

Vitest reports:

```text
Test Files  6 passed
Tests       6 passed
Errors      1 error

ReferenceError: window is not defined
```

and says the error originated from `tests/annual-budget.test.tsx` after the
test environment was torn down.

## Cause

`AnnualBudgetsPage` starts an asynchronous `useEffect()` during mount.

The previous test used `findByText("Buat Anggaran Tahunan")`, but that text is
already rendered immediately before the asynchronous budget-loading effect has
finished.

As a result, the test can end while React still has pending scheduled work.
Vitest then tears down jsdom, so a later React scheduler callback sees that
`window` no longer exists.

## Fix

Mount the component inside asynchronous React `act()`:

```tsx
await act(async () => {
  render(...);
});
```

This allows the mocked async effect to settle before assertions and before the
test environment is destroyed.

## Apply

```bash
unzip -o SIMA_Phase2B1_Fix03_Async_Test_Teardown.zip \
  -d ~/projects/sima-budget

cd ~/projects/sima-budget/apps/frontend
npm run format
npm run test

cd ~/projects/sima-budget
make phase2b1-check
```

No database reset, migration change, or dependency reinstall is required.
