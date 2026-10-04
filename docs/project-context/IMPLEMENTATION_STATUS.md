# SIMA Implementation Status

## Completed

- Phase 0 — Repository & Tooling
- Phase 1 — Foundation
- Phase 2 — Budget Foundation
- Phase 3A — Budget Plan Core & Versioned Items
- Phase 3B — Budget Plan Submission & Approval
- Phase 3C — Commitment & Available Budget Controls

## Current

### Phase 3D — Budget Plan Hardening & Phase 3 Completion

Implementation adds:

- optimistic/stale protection on submit;
- exact approval identity using row version + submission number + plan version;
- protection against stale approval tabs acting on a later resubmission;
- scoped Allocation / Committed / Draft Pipeline / Available summary;
- clearer plan creation empty states;
- final Phase 3 regression gate.

## Next after Phase 3D validation

Create CP-08 — Phase 3 Budget Plan Complete, then begin Phase 4 / next roadmap domain.


## Phase 4A — Realization Core

Status: implementation in validation. Adds scoped realization DRAFT → POSTED against exact APPROVED Budget Plan versions, strict cumulative realization ceiling, optimistic concurrency, audit trail, and cumulative development seed extension.
