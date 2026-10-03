# Phase 1A Manual/Automated Test Case

## P1A-001 — Foundation migration

Precondition:
PostgreSQL development container is healthy.

Steps:
1. Run `make phase1a-check`.

Expected:
- Phase 0 regression gate passes.
- Alembic migration succeeds.
- Foundation bootstrap succeeds twice.
- Verification reports required tables and seed records.
- Final output is `Phase 1A checks passed.`

## P1A-002 — Bootstrap idempotency

Steps:
1. Run `make foundation-bootstrap`.
2. Run it again.
3. Run `make foundation-verify`.

Expected:
No unique constraint failure and no duplicate default roles/permissions/unit types are created.
