# PROJECT CONTEXT - SIMA through Phase 5C

SIMA is an annual budget planning and monitoring application built with React + TypeScript,
FastAPI, PostgreSQL, SQLAlchemy, Alembic, and Docker.

## Completed milestones

- Phase 0 - Repository & Tooling
- Phase 1 - Foundation
- Phase 2 - Budget Foundation
- Phase 3 - Budget Plan
- Phase 4 - Realization
- CP-09 - Phase 4 Realization Complete
- Phase 5A - Reporting Foundation
- Phase 5B - Reports UI & Filters

## Current work - Phase 5C

Phase 5C adds CSV, Excel, and PDF download formats on top of the canonical reporting model.

The export endpoint reuses the same organization-unit scope guard as the JSON report endpoint.

The frontend sends the active Unit, Month, and Category filters to the export endpoint. Unit filtering recalculates the canonical server report. Month and category filtering only limit their breakdown sections and do not rewrite fiscal-year totals.

## Export architecture

```text
Canonical reporting service/query layer
        |
        +--> JSON API
        +--> Reports UI + filters
        +--> CSV export
        +--> Excel (.xlsx) export
        +--> PDF export
```

No new database tables or columns are introduced in Phase 5C.

## Next

Phase 5D - Reporting Hardening & Phase 5 Completion.
