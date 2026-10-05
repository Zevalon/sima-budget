# PROJECT CONTEXT — SIMA through Phase 5B

SIMA is an annual budget planning and monitoring application built with React + TypeScript,
FastAPI, PostgreSQL, SQLAlchemy, Alembic, and Docker.

## Completed milestones

- Phase 0 — Repository & Tooling
- Phase 1 — Foundation
- Phase 2 — Budget Foundation
- Phase 3 — Budget Plan
- Phase 4 — Realization
- CP-09 — Phase 4 Realization Complete
- Phase 5A — Reporting Foundation & Financial Summary API

## Current work — Phase 5B

Phase 5B turns the canonical reporting read model into an operational report UI.

The server accepts an optional `organization_unit_id` report filter. The requested unit must be
inside the user's existing `reports.view` scope. A unit outside that scope is rejected.

The report screen now provides:

- report section navigation;
- organization-unit filter;
- month filter;
- category filter;
- expanded unit financial table;
- monthly realization bar visualization;
- category commitment / plan-pipeline breakdown.

## Reporting semantics

Canonical formulas remain server-owned:

```text
Available             = Allocated - Committed
Remaining to Realize  = Committed - Realized
Utilization           = Realized / Committed * 100
```

The organization-unit filter recalculates the canonical report for the selected permitted unit.

The month filter limits only the monthly visualization; cumulative fiscal-year totals remain
cumulative.

The category filter limits the category plan breakdown only. Category-level Realized is not shown
because Realization is not item/category attributed in the current domain model.

## Reporting architecture

```text
Canonical reporting service/query layer
        |
        +--> JSON API
        +--> Reports UI + filters
        +--> future CSV / Excel / PDF
```

## Next

After Phase 5B validation and merge:

1. Phase 5C — CSV / Excel / PDF Export
2. Phase 5D — Reporting Hardening & Completion
