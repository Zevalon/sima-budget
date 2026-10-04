# Phase 1C2 Administration Test Cases

## ADM-001 — System administration write flow

Expected:
- create unit: 201
- create role: 201
- create user: 201
- user detail: 200
- deactivate user: 204
- deactivate unit: 204

## ADM-002 — Security

All write operations require:
- authenticated session;
- valid CSRF token;
- matching permission;
- `ALL` scope.

## ADM-003 — UI permission-awareness

Users without administration view permissions must not see the Administration menu.
Direct access to protected administration routes redirects to dashboard.
