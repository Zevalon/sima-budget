# SIMA Phase 4B — Fix 01: Vitest Hoisted Mock Fixture

## Symptom

`make phase4b-check` fails in:

```text
tests/realization-workflow.test.tsx
```

with:

```text
ReferenceError: Cannot access 'base' before initialization
```

Vitest also reports that `vi.mock()` factories are hoisted.

## Cause

`vi.mock()` is hoisted to the top of the module. The mock factory referenced a
top-level `const base`, but that constant had not been initialized when the
hoisted factory executed.

## Fix

Move the `base` realization fixture inside the `vi.mock()` factory itself.

This keeps every value used by the hoisted factory self-contained and removes
the temporal-dead-zone error.

No production frontend code, backend code, API contract, migration, or business
logic is changed.

## Apply

```bash
unzip -o SIMA_Phase4B_Fix01_Vitest_Hoisted_Mock.zip \
  -d ~/projects/sima-budget

cd ~/projects/sima-budget/apps/frontend
npm run format
npm run test

cd ~/projects/sima-budget
make phase4b-check
```

No database reset, seed reset, migration rollback, or dependency reinstall is
required.
