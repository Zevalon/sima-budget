# SIMA Phase 4B — Realization Correction, Cancellation & Reversal

## Scope

Phase 4B extends Realization with non-destructive correction workflow:

- cancel DRAFT realization with reason;
- reverse POSTED realization with reason;
- create one linked correction draft from a REVERSED realization;
- correction draft remains editable and must be posted normally;
- cancelled/reversed records stay in history;
- realized aggregate counts POSTED only;
- draft pipeline counts DRAFT only;
- optimistic concurrency applies to cancel/reverse/correction actions;
- actions are unit-scoped and audited.

## Migration

```text
20261004_0008_phase4b_realization_corrections
```

## Gate

```bash
make phase4b-check
```

Expected:

```text
Phase 4B realization correction and reversal verification: OK
Phase 4B checks passed.
```
