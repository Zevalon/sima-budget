# Phase 4D — Realization Hardening & Phase 4 Completion

## Goal

Close the Realization phase with explicit workflow identity checks, final scope validation, and cross-domain aggregate consistency.

## Workflow identity

Every mutable realization action now identifies the exact snapshot the browser is acting on:

```text
row_version + status + plan_version_id
```

If any value is stale, the server returns `409 Conflict` and the user must reload before retrying.

Protected actions:

- update DRAFT;
- post DRAFT;
- cancel DRAFT;
- reverse POSTED;
- create correction from REVERSED.

## Correction source hardening

Creating a correction increments the source realization `row_version`. This means the source workflow record changes when a correction relationship is created, preventing an old tab from continuing with the pre-correction snapshot.

## Final invariants

```text
Realized <= Committed <= Allocated

Plan Realized <= Approved Plan

POSTED     -> Realized
DRAFT      -> Realization Draft Pipeline
REVERSED   -> historical, not Realized
CANCELLED  -> historical, not Draft Pipeline
```

## Scope

A user with realization permissions still receives only records and aggregates within the organizational-unit scope granted by RBAC.

## Completion gate

```bash
make phase4d-check
```

The gate runs the complete regression chain through Phase 4C before the Phase 4D verifier.

After browser smoke testing and CI/merge, create **CP-09 — Phase 4 Realization Complete**.
