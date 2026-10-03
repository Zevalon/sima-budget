# SIMA — CP-03 API Endpoint Map

Dokumen ringkas untuk navigasi endpoint baseline. Detail dan business rule authoritative tetap berada pada `CP-03_Application_Architecture_API_Baseline.md`.

## Authentication
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `POST /api/v1/auth/logout-all`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/change-password`

## Users & RBAC
- `/api/v1/users`
- `/api/v1/roles`
- `/api/v1/permissions`
- `/api/v1/user-role-assignments`

## Organization
- `/api/v1/organization-unit-types`
- `/api/v1/organization-units`
- `/api/v1/organization-units/tree`

## Fiscal Year
- `/api/v1/fiscal-years`
- command: `start-planning`, `activate`, `close`, `reopen`, `archive`

## Annual Budget
- `/api/v1/fiscal-years/{fy_id}/annual-budget`
- `/api/v1/annual-budgets/{id}/submit`
- `/api/v1/annual-budgets/{id}/revisions`

## Allocation
- `/api/v1/fiscal-years/{fy_id}/allocations`
- `/api/v1/allocations/{id}/summary`
- `/api/v1/allocations/{id}/adjustments`
- `/api/v1/fiscal-years/{fy_id}/transfers`

## Budget Plan
- `/api/v1/budget-plans`
- `/api/v1/budget-plans/{id}/versions`
- `/api/v1/budget-plans/{id}/items`
- command: `submit`, `cancel`, `revisions`

## Approval
- `/api/v1/approvals/inbox`
- `/api/v1/approval-instances/{id}`
- `/api/v1/approval-step-instances/{id}/approve`
- `/api/v1/approval-step-instances/{id}/reject`
- `/api/v1/approval-step-instances/{id}/request-revision`
- `/api/v1/approval-workflows`

## Realization
- `/api/v1/realizations`
- `/api/v1/budget-plans/{plan_id}/realizations`
- command: `submit`, `verify`, `reject`, `cancel`, `reverse`

## Files
- `/api/v1/files`
- `/api/v1/files/{id}/download`

## Dashboard & Reports
- `/api/v1/dashboard/*`
- `/api/v1/reports/*`
- `/api/v1/reports/{report_code}/export`

## Notifications / Audit / Settings
- `/api/v1/notifications`
- `/api/v1/audit-logs`
- `/api/v1/settings/application`
- `/api/v1/settings/security`
- `/api/v1/settings/document-numbering`
