# Implementation Phase 1B — Authentication & Session

## Scope

Implemented:

- first administrator bootstrap command;
- login with username or email;
- Argon2 password verification;
- failed-login counter and temporary account lock;
- opaque random server-side session;
- session cookie using HttpOnly + SameSite=Lax;
- production Secure cookie flag;
- session token stored only as HMAC hash;
- CSRF token derived from the authenticated session;
- current-user endpoint;
- logout + server-side session revocation;
- authentication audit events;
- protected frontend routes;
- login page;
- authenticated application shell.

## API

```text
POST /api/v1/auth/login
GET  /api/v1/auth/me
POST /api/v1/auth/logout
```

## First administrator

After Phase 1B checks pass:

```bash
make bootstrap-admin
```

No default password is committed to Git.

## Validation

```bash
chmod +x scripts/check-phase1b.sh
make phase1b-check
```

Expected:

```text
Authentication verification: OK (...)
Phase 1B checks passed.
```
