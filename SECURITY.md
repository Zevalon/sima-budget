# Security Policy

## Do Not Commit

- `.env`
- password
- session token
- secret key
- database production dump
- private certificate
- production attachment

## Reporting

Untuk repository private, laporkan temuan keamanan melalui jalur internal tim pengembang/organisasi, bukan issue publik.

## Baseline

- opaque server-side session
- HttpOnly cookie
- CSRF protection untuk unsafe request
- Argon2id password hashing
- RBAC + scope
- backend-side authorization
- upload validation
- audit trail
- production HTTPS

Lihat `docs/security/SECURITY_BASELINE.md`.
