# SIMA Authentication Baseline

## Session

SIMA uses an opaque random browser session token.

The raw token:
- exists only in the browser HttpOnly cookie;
- is never stored in the database.

The database stores an HMAC-SHA256 hash of the token.

## CSRF

Authenticated mutation requests require `X-CSRF-Token`.

The CSRF token is derived using a separate CSRF secret and the active raw session token.

## Passwords

Passwords use Argon2id through `argon2-cffi`.

The first administrator has no source-controlled default password.

## Lockout

Default:
- 5 failed attempts
- 15-minute temporary lock

Values are configurable with environment settings.

## Audit

Authentication events:
- LOGIN_FAILED
- LOGIN_SUCCESS
- LOGOUT
- ADMIN_BOOTSTRAP_CREATED
- ADMIN_BOOTSTRAP_UPDATED
