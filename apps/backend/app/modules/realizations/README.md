# Realizations Module

Implemented in Phase 4A and extended in Phase 4B.

Owns manual budget-realization records against exact APPROVED Budget Plan versions.

Current workflow:

```text
DRAFT -> POSTED -> REVERSED
  \-> CANCELLED

REVERSED -> correction DRAFT -> POSTED
```

The module provides scoped access, optimistic concurrency, cumulative realization limits,
non-destructive cancellation/reversal, correction linkage, and audit events.
