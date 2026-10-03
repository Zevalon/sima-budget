# Security Baseline

Core V1 controls:

- opaque server-side sessions;
- HttpOnly cookie;
- Secure cookie production flag;
- SameSite baseline;
- CSRF for unsafe methods;
- Argon2id passwords;
- RBAC + data scope;
- backend authorization;
- self-approval prevention;
- restrictive CORS;
- upload allowlist and limit;
- no secrets in repository;
- critical audit events;
- HTTPS production edge;
- session revocation;
- concurrency testing for financial operations.

The implementation must not weaken this baseline without documented review.
