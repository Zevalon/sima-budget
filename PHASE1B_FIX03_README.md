# SIMA Phase 1B — Fix 03

Fixes the frontend ESLint errors reported by `make phase1b-check`.

Changes:

- move `useAuth` and auth context types out of `AuthProvider.tsx` so React Fast Refresh
  sees a component-only module;
- make the form submit handler synchronous and explicitly launch the async login task
  with `void`;
- explicitly ignore the optional Promise returned by React Router navigation;
- add a typed `VITE_API_BASE_URL` declaration for `import.meta.env`;
- update imports in `ProtectedRoute` and `AppShell`.

Apply over the repository root, then run:

```bash
cd ~/projects/sima-budget/apps/frontend
npm run format

cd ~/projects/sima-budget
make phase1b-check
```

No database reset, migration rollback, dependency reinstall, or Docker volume deletion is required.
