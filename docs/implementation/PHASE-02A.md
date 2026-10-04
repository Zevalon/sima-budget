# Implementation Phase 2A — Fiscal Year & Budget Master Foundation

## Goal

Introduce the first operational budget-domain foundation after Phase 1.

## Fiscal Year

Lifecycle:

```text
DRAFT → PLANNING → ACTIVE → CLOSED → ARCHIVED
                         ↑
                         └── controlled reopen from CLOSED
```

Rules:

- Fiscal Year code is unique per organization.
- `start_date < end_date`.
- only one `ACTIVE` Fiscal Year may exist per organization;
- `CLOSED → ACTIVE` is only available through the controlled reopen operation;
- reopen requires a dedicated permission and a reason;
- `ARCHIVED` is immutable through normal lifecycle endpoints;
- create, update, transition, and reopen operations are audited.

API:

```text
GET   /api/v1/fiscal-years
POST  /api/v1/fiscal-years
PATCH /api/v1/fiscal-years/{id}
POST  /api/v1/fiscal-years/{id}/transition
POST  /api/v1/fiscal-years/{id}/reopen
```

## Master Data

Budget Category:

```text
GET   /api/v1/master-data/budget-categories
POST  /api/v1/master-data/budget-categories
PATCH /api/v1/master-data/budget-categories/{id}
POST  /api/v1/master-data/budget-categories/{id}/deactivate
```

Unit of Measure:

```text
GET   /api/v1/master-data/units-of-measure
POST  /api/v1/master-data/units-of-measure
PATCH /api/v1/master-data/units-of-measure/{id}
POST  /api/v1/master-data/units-of-measure/{id}/deactivate
```

Master data uses deactivate rather than destructive delete.

## Permissions

```text
fiscal_years.view
fiscal_years.create
fiscal_years.update
fiscal_years.transition
fiscal_years.reopen
budget_categories.view
budget_categories.manage
units_of_measure.view
units_of_measure.manage
```

`BUDGET_ADMIN` receives all Phase 2A permissions.

`SYSTEM_ADMIN` receives only Phase 2A read permissions, preserving the rule that technical system administration does not automatically grant budget authority.

## UI

Master Data navigation now exposes:

- Tahun Anggaran
- Kategori Anggaran
- Satuan

The top-bar Fiscal Year selector is now backed by real Fiscal Year data.

## Gate

```bash
make phase2a-check
```

Expected final output:

```text
Phase 2A budget foundation verification: OK
Phase 2A checks passed.
```
