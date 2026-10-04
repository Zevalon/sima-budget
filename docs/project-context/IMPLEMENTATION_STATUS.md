# SIMA Implementation Status

## Completed

- CP-01 through CP-07 baselines
- Phase 0 — Repository & Tooling
- Phase 1 — Foundation
- Phase 2 — Budget Foundation
  - Phase 2A — Fiscal Year & Budget Master Foundation
  - Phase 2B1 — Annual Budget Core & Submission
  - Phase 2B2 — Annual Budget Approval & Rejection
  - Phase 2C — Unit Allocation
  - Phase 2D — Budget Foundation Hardening & Completion
- Deterministic Development Seed Baseline through Phase 2

## Current

Phase 3A — Budget Plan Core & Versioned Items.

Current scope:

- Budget Plan header bound to Unit Allocation;
- version container and versioned plan items;
- quantity × unit price computed with Decimal;
- unit-scoped access for Unit PIC;
- draft editing with optimistic row-version protection;
- per-plan validation against Unit Allocation;
- Phase 3 seed extension;
- Rencana Anggaran frontend page.

## Next after Phase 3A validation

Phase 3B — Plan Submission & Approval.

Approved versions must become immutable and later commitment logic must preserve:

```text
Committed Approved Plans <= Unit Allocation
```
