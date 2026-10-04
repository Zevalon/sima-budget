# SIMA Phase 2B1 — Fix 05: ESLint require-await

## Symptom

`make phase2b1-check` fails during frontend lint with:

```text
tests/annual-budget.test.tsx
Async arrow function has no 'await' expression
@typescript-eslint/require-await
```

## Cause

The test intentionally uses asynchronous React `act()` so pending effects settle
before jsdom teardown, but its callback had no explicit `await`.

## Fix

Keep asynchronous `act()` and explicitly flush one microtask:

```tsx
await act(async () => {
  render(...);
  await Promise.resolve();
});
```

This satisfies ESLint while preserving the async teardown protection from the
previous fix.

## Apply

```bash
unzip -o SIMA_Phase2B1_Fix05_ESLint_Require_Await.zip \
  -d ~/projects/sima-budget

cd ~/projects/sima-budget/apps/frontend
npm run format
npm run lint
npm run test

cd ~/projects/sima-budget
make phase2b1-check
```

No database reset, migration change, or dependency reinstall is required.
