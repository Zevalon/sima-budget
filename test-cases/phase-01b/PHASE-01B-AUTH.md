# Phase 1B Authentication Test Cases

## AUTH-001 — Valid login

Expected:
- HTTP 200
- HttpOnly session cookie issued
- `/auth/me` succeeds
- response includes CSRF token

## AUTH-002 — Invalid password

Expected:
- HTTP 401
- no authenticated session
- failed attempt recorded
- audit event created

## AUTH-003 — Logout without CSRF

Expected:
- HTTP 403
- session remains authenticated

## AUTH-004 — Valid logout

Expected:
- HTTP 204
- server session revoked
- subsequent `/auth/me` returns HTTP 401

## AUTH-005 — Protected frontend

Expected:
- anonymous user opening `/app/dashboard` is redirected to `/login`
- authenticated user can access dashboard

## Automated gate

```bash
make phase1b-check
```
