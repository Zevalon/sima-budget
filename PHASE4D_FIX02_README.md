# SIMA Phase 4D — Fix 02: Await Realization Reload in Vitest

## Symptom

`make phase4d-check` passes all frontend test assertions but Vitest reports an
unhandled error after the test:

```text
ReferenceError: window is not defined
```

The error originates from React's scheduler after
`realization-hardening.test.tsx` has already finished.

## Cause

The test waited only until `reverseRealization()` was called.

The real component continues after that call:

1. updates the success state;
2. awaits `reload()`;
3. fetches context and realization data again;
4. updates React state.

The test could finish and jsdom could be torn down while steps 2-4 were still
running.

## Fix

The test now:

- controls both initial and post-reversal API responses;
- returns `POSTED` on the first load;
- returns `REVERSED` on the reload;
- waits until the `REVERSED` state and reversal reason are rendered;
- verifies both reload API calls completed.

This synchronizes the test with the actual asynchronous component lifecycle.

No production code, backend code, database schema, API contract, or business
rules are changed.

## Apply

```bash
unzip -o SIMA_Phase4D_Fix02_Await_Realization_Reload.zip \
  -d ~/projects/sima-budget

cd ~/projects/sima-budget/apps/frontend
npm run format
npm run test

cd ~/projects/sima-budget
make phase4d-check
```

No database reset, seed reset, migration rollback, or dependency reinstall is
required.
