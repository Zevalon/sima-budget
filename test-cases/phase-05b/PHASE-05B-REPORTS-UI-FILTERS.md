# Phase 5B Test Cases — Reports UI & Filters

## Automated

1. Phase 5A full regression remains green.
2. Valid organization-unit filter returns `200`.
3. Filtered response identifies `organization_unit_filter_id`.
4. Unit filter options remain available after a filter is applied.
5. Unit outside the caller's report scope returns `403`.
6. Frontend unit filter requests the server-filtered canonical summary.
7. Month filter limits only the monthly breakdown.
8. Category filter limits only the category breakdown.
9. Reset restores the full scoped report.

## Browser smoke

1. Login as `budgetadmin` or another role with broad report scope.
2. Select FY2025 and open Laporan.
3. Confirm all-scope summary loads.
4. Select one organization unit and confirm cards/table/month/category data change.
5. Select a month and confirm only that month is shown in the monthly visualization.
6. Select a category and confirm only that category is shown.
7. Reset filters and confirm the full scoped report returns.
8. Login as a unit-scoped user such as `itpic`.
9. Confirm unit options do not expose units outside the user's scope.
10. Confirm direct API attempts to filter an unauthorized unit are rejected.
