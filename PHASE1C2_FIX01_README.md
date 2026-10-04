# SIMA Phase 1C2 — Fix 01

Fixes the frontend lint failures reported by `make phase1c2-check`.

Changes:

- adds typed FormData helpers;
- avoids unsafe `String(FormDataEntryValue)` conversion;
- avoids direct state-changing reload calls from `useEffect`;
- fixes test mocks that used unnecessary `async`;
- applies the same loading pattern to Users, Roles, and Organization Units pages.

Apply over the repository root, then:

```bash
cd ~/projects/sima-budget/apps/frontend
npm run format

cd ~/projects/sima-budget
make phase1c2-check
```

No database reset, Alembic rollback, or dependency reinstall is required.
