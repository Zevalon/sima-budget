# PROJECT CONTEXT — SIMA through Phase 5A

SIMA is an annual budget planning and monitoring application built with React + TypeScript,
FastAPI, PostgreSQL, SQLAlchemy, Alembic, and Docker.

## Completed milestones

- Phase 0 — Repository & Tooling
- Phase 1 — Foundation
- Phase 2 — Budget Foundation
- Phase 3 — Budget Plan
- Phase 4 — Realization
- CP-09 — Phase 4 Realization Complete

## Current work — Phase 5A

Phase 5A introduces the canonical reporting read model.

The reporting layer is scope-aware and derives financial totals from existing transactional tables.
It does not store duplicate report totals.

Canonical formulas:

```text
Available             = Allocated - Committed
Remaining to Realize  = Committed - Realized
Utilization           = Realized / Committed * 100
```

Status contribution rules:

```text
Committed                  <- APPROVED Budget Plan current version
Plan Draft Pipeline         <- DRAFT + PENDING_APPROVAL Budget Plan current version
Realized                    <- POSTED Realization
Realization Draft Pipeline  <- DRAFT Realization
```

Realization is still plan-level, so category-level realized spending cannot be calculated faithfully.
Phase 5A therefore exposes category plan commitment/pipeline only and does not invent category realized values.

## Reporting architecture rule

```text
Canonical reporting service/query layer
        |
        +--> JSON API
        +--> Reports UI
        +--> future CSV / Excel / PDF
```

Future reporting and export work must reuse this layer rather than duplicate formulas.

## Next

After Phase 5A validation and merge:

1. Phase 5B — Reports UI & Filters
2. Phase 5C — Export
3. Phase 5D — Reporting Hardening & Completion
