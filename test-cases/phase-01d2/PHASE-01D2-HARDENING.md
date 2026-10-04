# Phase 1D2 Hardening Test Cases

## SEC-001 — Last administrator continuity

Removing the final active `SYSTEM_ADMIN` + `ALL` assignment must return HTTP 409.

## SEC-002 — Built-in role protection

Replacing permissions on a built-in system role must return HTTP 409.

## SEC-003 — Administrative session revocation

A System Administrator can revoke another user's sessions. The revoked session must return HTTP 401 on `/auth/me`.

## SEC-004 — Organization unit dependency protection

An organization unit used by an active user membership or active scoped role must not be deactivated.

## UX-001 — Permission denial

Direct access to an administration route without its permission shows an explicit access-denied page.

## UX-002 — Configurable authenticated branding

The application shell uses application/organization names returned by the authenticated user response.

## UX-003 — Audit pagination

Audit Log supports previous/next navigation, filter clearing, loading state, and empty state.
