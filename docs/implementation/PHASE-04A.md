# Phase 4A — Realization Core

Phase 4A introduces manual budget realization against APPROVED Budget Plans.

## Lifecycle

```text
DRAFT → POSTED
```

`REVERSED` and `CANCELLED` are reserved in the schema for the controlled correction workflow in Phase 4B.

## Core Rules

- realization can only reference an APPROVED Budget Plan;
- realization stores the exact approved plan version;
- entry/posting is only allowed while Fiscal Year is ACTIVE;
- one approved plan may have many realization records;
- only POSTED realizations reduce remaining realizable amount;
- DRAFT realization is informational pipeline only;
- total POSTED realization must never exceed approved plan total;
- posting locks the parent Budget Plan before checking the aggregate;
- POSTED records are immutable in Phase 4A;
- no hard delete endpoint is provided;
- draft updates use optimistic concurrency.

## Formula

```text
Approved Plan
- Posted Realization
= Remaining To Realize
```

## Permissions

- `realizations.view`
- `realizations.create`
- `realizations.update`
- `realizations.post`

Unit PIC receives scoped mutation rights. Other standard roles receive read access only.
