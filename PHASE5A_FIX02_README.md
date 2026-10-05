# SIMA Phase 5A — Fix 02: Duplicate Report Value Test

## Symptom

`make phase5a-check` fails in:

```text
tests/reports.test.tsx
```

with:

```text
Found multiple elements with the text: Rp 30.000.000.000,00
```

## Cause

The value represents `Committed` and is intentionally rendered in two places:

1. canonical financial summary card;
2. unit summary table.

The test used `getByText()`, which requires exactly one matching element.

## Fix

The assertion now uses `getAllByText()` and verifies that the committed value
appears at least twice.

No application UI, reporting calculation, API, backend logic, database,
migration, seed, or financial rule is changed.

## Apply

```bash
unzip -o SIMA_Phase5A_Fix02_Report_Test_Duplicate_Value.zip   -d ~/projects/sima-budget

cd ~/projects/sima-budget/apps/frontend
npm run format
npm run test

cd ~/projects/sima-budget
make phase5a-check
```
