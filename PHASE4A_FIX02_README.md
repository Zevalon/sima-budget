# SIMA Phase 4A — Fix 02: React Hook Dependency Warning

## Symptom

Frontend lint reports:

```text
React Hook useEffect has a missing dependency: 'reload'
react-hooks/exhaustive-deps
```

## Fix

`reload()` is wrapped with `useCallback()` and the effect depends on `reload`.

No Realization business logic or API behavior changes.

## Apply

```bash
unzip -o SIMA_Phase4A_Fix02_Frontend_Hook_Warning.zip \
  -d ~/projects/sima-budget

cd ~/projects/sima-budget/apps/frontend
npm run format
npm run lint

cd ~/projects/sima-budget
make phase4a-check
```

No database or seed reset is required for this fix.
