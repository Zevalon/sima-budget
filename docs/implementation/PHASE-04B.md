# Phase 4B — Realization Correction, Cancellation & Reversal

Status: implementation / validation.

## Business rules

- No hard delete for financial realization records.
- DRAFT may be cancelled with a reason.
- POSTED may be reversed with a reason.
- REVERSED is excluded from realized totals.
- CANCELLED is excluded from draft pipeline.
- A REVERSED record may create one linked correction DRAFT.
- Correction DRAFT is reviewed/edited and then posted through the standard posting flow.
- Cancel/reverse/correction actions require the current row version.
- Financial actions are allowed only while Fiscal Year is ACTIVE.
- Scope enforcement remains authoritative in the backend.

## Financial effect

```text
POSTED    -> counts as Realized
DRAFT     -> counts as Draft Pipeline
REVERSED  -> historical only, does not count as Realized
CANCELLED -> historical only, does not count as Draft Pipeline
```
