# CP-05 — Implementation Roadmap

## Phase 0 — Repository & Tooling
Deliver:
- monorepo scaffold
- React/TypeScript/Vite
- FastAPI
- PostgreSQL Compose
- config/env handling
- health checks
- lint/typecheck/test commands
- CI skeleton
- docs skeleton

Gate:
fresh clone can start application.

## Phase 1 — Foundation
Deliver:
- application shell
- settings
- auth
- sessions/CSRF
- users
- roles/permissions/scopes
- organizational units
- audit infrastructure

Gate:
user can login and authorization works.

## Phase 2 — Budget Foundation
Deliver:
- fiscal year lifecycle
- categories/UOM
- annual budget
- approval for annual budget
- allocations

Gate:
annual budget can be safely allocated.

## Phase 3 — Plans
Deliver:
- plan header
- version model
- items
- attachments
- calculations
- draft/submit
- plan detail UI

Gate:
unit can submit valid plan.

## Phase 4 — Approval
Deliver:
- workflow templates/steps
- approval inbox
- actions
- comments
- self-approval rule
- final approval transaction
- revision request

Gate:
plan approval safely commits funds.

## Phase 5 — Realization
Deliver:
- draft/submitted/verified flow
- attachments
- limits
- execution status
- corrections policy foundation

Gate:
realization reconciles to plan.

## Phase 6 — Monitoring & Reports
Deliver:
- role dashboards
- reports
- filters
- export
- warnings

Gate:
financial totals reconcile.

## Phase 7 — Completion
Deliver:
- notifications
- revision workflows
- allocation revision
- branding/settings
- audit views
- user documentation

Gate:
V1 feature complete.

## Phase 8 — Hardening
Deliver:
- regression
- E2E
- concurrency
- security review
- performance review
- staging
- backup/restore test
- UAT
- release docs

Gate:
V1 Release Candidate.
