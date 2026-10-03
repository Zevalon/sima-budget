# SIMA Phase 1B — Fix 04: E2E CI

## Problem

After Phase 1B, `/app/dashboard` is a protected route.

The original Phase 0 Playwright smoke test assumed the dashboard was directly
accessible to an anonymous browser session, so the GitHub Actions
`E2E CI / frontend-smoke` job can fail after authentication is introduced.

## Correct Phase 1B expectation

For an anonymous user:

```text
/app/dashboard
    ↓
/login
```

The smoke test now stubs `/api/v1/auth/me` as HTTP 401 and verifies the login UI.
This keeps the frontend smoke job deterministic and does not require the E2E
workflow to run PostgreSQL + FastAPI.

The actual login/session/CSRF flow remains covered by `make phase1b-check`.

## Apply

Apply this patch on the Phase 1B branch:

```bash
git switch feature/phase-1b-authentication

unzip -o SIMA_Phase1B_Fix04_E2E_CI.zip -d ~/projects/sima-budget

cd ~/projects/sima-budget/apps/frontend
npm run format
npx playwright test e2e/smoke.spec.ts
```

Then commit and push:

```bash
cd ~/projects/sima-budget
git add .
git commit -m "test(e2e): update smoke test for protected routes"
git push
```

GitHub will automatically rerun the existing pull-request checks.
