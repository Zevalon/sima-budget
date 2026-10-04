# SIMA Phase 2B1 — Fix 04: Stable Fiscal Year Test Mock

## Symptom

After Fix 03, Vitest reports:

```text
Test timed out in 5000ms
```

for `tests/annual-budget.test.tsx`.

## Cause

The test mock returned a new `selectedFiscalYear` object every time
`useFiscalYear()` was called:

```tsx
useFiscalYear: () => ({
  selectedFiscalYear: { ... },
})
```

`AnnualBudgetsPage` has an effect that depends on the selected fiscal-year
object:

```tsx
useEffect(..., [selectedFiscalYear])
```

The unstable mock therefore made the dependency appear changed after every
state update and render, repeatedly re-running the effect.

The real application provider does not have this problem because
`selectedFiscalYear` is memoized.

## Fix

The test now creates one stable mock context and one stable selected fiscal
year inside the Vitest mock factory, and returns those same objects on every
render.

The authentication mock is also made stable for consistency.

## Apply

```bash
unzip -o SIMA_Phase2B1_Fix04_Stable_Fiscal_Year_Test_Mock.zip \
  -d ~/projects/sima-budget

cd ~/projects/sima-budget/apps/frontend
npm run format
npm run test

cd ~/projects/sima-budget
make phase2b1-check
```

No database reset, migration change, or dependency reinstall is required.
