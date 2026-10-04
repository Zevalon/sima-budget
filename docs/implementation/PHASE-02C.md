# Phase 2C — Unit Allocation

## Status

Pending local validation.

## Scope

Phase 2C introduces organization-unit allocation against an approved Annual Budget.

Implemented rules:

- one allocation per Annual Budget + organization unit;
- only active units with `can_receive_budget=true` may receive allocation;
- allocation writes require an Annual Budget in `APPROVED` status;
- allocation writes are allowed only while the Fiscal Year is `PLANNING`;
- total allocations may never exceed the approved Annual Budget;
- monetary values use PostgreSQL `NUMERIC(20,2)` / Python `Decimal`;
- create/update operations lock the Annual Budget row before aggregate validation;
- this row lock serializes competing writes for the same Annual Budget and prevents concurrent over-allocation;
- allocation updates increment `version` and are audited;
- organization-wide allocation endpoints require `ALL` scope.

## Permissions

- `unit_allocations.view`
- `unit_allocations.create`
- `unit_allocations.update`

Role defaults:

- System Administrator: view only;
- Budget Administrator: view/create/update;
- Management Approver: view only;
- Auditor: view only;
- Unit PIC: no organization-wide allocation permission yet.

Unit-scoped allocation visibility is intentionally deferred until the Budget Plan phase, so the current organization-wide endpoint cannot leak other units' financial allocation data to unit-scoped users.

## API

```text
GET   /api/v1/unit-allocations/overview?fiscal_year_id=<uuid>
POST  /api/v1/unit-allocations
PATCH /api/v1/unit-allocations/{allocation_id}
```

## Concurrency Invariant

Every allocation mutation acquires a PostgreSQL row lock on the parent Annual Budget before calculating the current aggregate allocation.

Two concurrent requests that would independently fit but jointly exceed the Annual Budget cannot both commit successfully.

The Phase 2C verifier exercises this with two concurrent `600.00` allocations against a `1000.00` Annual Budget and requires exactly one request to succeed.

## UI

A new **Alokasi Unit** page provides:

- approved Annual Budget summary;
- allocated total;
- remaining amount;
- eligible unit selector;
- create allocation form;
- allocation update forms during PLANNING;
- read-only state when mutation conditions are not met.

## Explicitly Deferred

- inter-unit transfer workflow;
- unit-scoped self-service allocation views;
- allocation decrease guards against committed Budget Plans;
- Budget Plan creation and commitment;
- allocation reporting beyond the operational summary.
