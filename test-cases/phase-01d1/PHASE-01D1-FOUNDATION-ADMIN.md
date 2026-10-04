# Phase 1D1 Test Cases

## FD1-001 Settings read
System Administrator receives 200 from `/api/v1/settings`.

## FD1-002 Settings CSRF
PATCH without CSRF returns 403.

## FD1-003 Settings update
PATCH with valid session, CSRF, permission, and ALL scope returns 200.

## FD1-004 Audit visibility
The settings update creates an `APPLICATION_SETTINGS_UPDATED` audit event.

## FD1-005 Permission-aware UI
Settings and Audit cards are only visible when matching view permissions exist.
