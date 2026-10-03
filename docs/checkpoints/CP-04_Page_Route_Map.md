# CP-04 — Page & Route Map

## Public

| Route | Page |
|---|---|
| `/login` | Login |
| `/forgot-password` | Forgot Password (when enabled) |
| `/reset-password` | Reset Password (when enabled) |

## Application

| Route | Page | Typical Access |
|---|---|---|
| `/app/dashboard` | Role-aware Dashboard | Authenticated |

## Budget

| Route | Page |
|---|---|
| `/app/budgets/fiscal-years` | Fiscal Years |
| `/app/budgets/fiscal-years/:id` | Fiscal Year Detail |
| `/app/budgets/annual` | Annual Budget |
| `/app/budgets/annual/:id` | Annual Budget Detail |
| `/app/budgets/allocations` | Unit Allocations |
| `/app/budgets/revisions` | Budget Revisions |
| `/app/budgets/transfers` | Budget Transfers (feature flag) |

## Plans

| Route | Page |
|---|---|
| `/app/plans` | Budget Plan List |
| `/app/plans/new` | Create Budget Plan |
| `/app/plans/:id` | Plan Detail |
| `/app/plans/:id/edit` | Edit Draft |
| `/app/plans/:id/revisions/new` | Request Plan Revision |
| `/app/plans/:id/revisions/:revisionId` | Revision Detail |

## Realizations

| Route | Page |
|---|---|
| `/app/realizations` | Realization List |
| `/app/realizations/new` | Create Realization |
| `/app/realizations/:id` | Realization Detail |
| `/app/realizations/:id/edit` | Edit Draft Realization |

## Approval

| Route | Page |
|---|---|
| `/app/approvals/inbox` | Approval Inbox |
| `/app/approvals/submissions` | My Submissions |
| `/app/approvals/history` | Approval History |
| `/app/approvals/:instanceId` | Approval Detail |

## Reports

| Route | Page |
|---|---|
| `/app/reports` | Report Center |
| `/app/reports/annual-summary` | Annual Budget Summary |
| `/app/reports/allocations` | Unit Allocation |
| `/app/reports/plans` | Budget Plans |
| `/app/reports/plan-items` | Plan Detail Items |
| `/app/reports/realizations` | Realizations |
| `/app/reports/budget-vs-realization` | Budget vs Realization |
| `/app/reports/remaining-budget` | Remaining Budget |
| `/app/reports/utilization` | Unit Utilization |
| `/app/reports/categories` | Category Report |
| `/app/reports/monthly` | Monthly Realization |
| `/app/reports/approvals` | Approval Report |
| `/app/reports/revisions` | Revision History |

## Master Data

| Route | Page |
|---|---|
| `/app/master/organization-units` | Organization Units |
| `/app/master/unit-types` | Unit Types |
| `/app/master/budget-categories` | Budget Categories |
| `/app/master/units-of-measure` | Units of Measure |
| `/app/master/account-references` | Account References (optional) |
| `/app/master/document-numbering` | Document Numbering |

## Administration

| Route | Page |
|---|---|
| `/app/admin/users` | Users |
| `/app/admin/users/:id` | User Detail |
| `/app/admin/roles` | Roles |
| `/app/admin/roles/:id` | Role Detail |
| `/app/admin/permissions` | Permission Catalog |
| `/app/admin/workflows` | Approval Workflows |
| `/app/admin/workflows/:id` | Workflow Detail |
| `/app/admin/settings` | Application Settings |
| `/app/admin/audit` | Audit Log |
| `/app/admin/system` | System Information |

## Profile

| Route | Page |
|---|---|
| `/app/profile` | User Profile |
| `/app/profile/security` | Password / Security |
| `/app/notifications` | Notification Center |

## Route Design Rules

1. URL uses plural nouns for resource collections.
2. IDs are opaque identifiers and not sequential business numbers.
3. Document numbers are displayed in UI but not required as route identifiers.
4. Frontend route guards are convenience only; backend is authority.
5. Fiscal Year is normally a global UI context, not repeated in every path.
6. Deep links must remain valid when permission allows access.
7. Feature-flag-disabled routes return not-found/feature-unavailable rather than empty screens.
