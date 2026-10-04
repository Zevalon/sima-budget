# SIMA Implementation Status

## Completed

- Phase 0 — Repository & Tooling
- Phase 1 — Foundation
- Phase 2 — Budget Foundation
- Phase 3 — Budget Plan
- Phase 4A — Realization Core
- Phase 4B — Realization Correction, Cancellation & Reversal

## Current

### Phase 4C — Realization Aggregates & Monitoring

Implementation adds:

- cross-domain execution aggregates from Annual Budget → Allocation → Commitment → Realization;
- Realized and Realization Draft Pipeline on Unit Allocation summaries;
- Remaining to Realize = Committed - Realized;
- utilization percentage per approved plan and per scoped realization context;
- monitoring UI on Dashboard, Unit Allocation, and Realization pages;
- explicit concurrent posting verification;
- invariant validation: `Realized <= Committed <= Allocated`.

## Next after Phase 4C validation

Phase 4D — Realization Hardening & Phase 4 Completion.
