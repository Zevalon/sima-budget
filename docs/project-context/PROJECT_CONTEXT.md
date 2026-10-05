# PROJECT CONTEXT — SIMA through Phase 5D

SIMA is an annual budget planning and monitoring application using React + TypeScript, FastAPI,
PostgreSQL, SQLAlchemy, Alembic, and Docker.

## Completed implementation before this phase

- Phase 0 — Repository & Tooling
- Phase 1 — Foundation
- Phase 2 — Budget Foundation
- Phase 3 — Budget Plan
- Phase 4 — Realization
- CP-09 — Phase 4 Realization Complete
- Phase 5A — Canonical Reporting Foundation
- Phase 5B — Reports UI & Scoped Filters
- Phase 5C — CSV / Excel / PDF Export

## Phase 5D

Phase 5D closes Monitoring & Reporting.

Historical reports retain inactive organization units when those units remain inside the caller's
authorized report scope. Deactivating a unit therefore does not erase historical allocation,
commitment, or realization visibility.

Financial report JSON and export downloads are marked private/no-store and use `nosniff`.

CSV protects configurable/master-data text against spreadsheet formula injection. Export files
contain active Unit, Month, and Category filter metadata. PDF output wraps long lines rather than
silently truncating them.

Canonical financial semantics remain server-owned:

```text
Available             = Allocated - Committed
Remaining to Realize  = Committed - Realized
Utilization           = Realized / Committed * 100
```

Reversed and cancelled realization records remain historical and do not inflate canonical realized
or draft-pipeline totals.

## Completion

After `make phase5d-check`, browser smoke testing, GitHub CI, and merge to `main`, create:

```text
CP-10 — Phase 5 Monitoring & Reporting Complete
```

Then continue to Phase 6 according to the implementation roadmap.
