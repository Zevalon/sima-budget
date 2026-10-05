# Phase 5C Test Cases - Report Exports

## Automated

1. Phase 5B full regression remains green.
2. CSV endpoint returns 200, CSV content type, attachment filename, and canonical report content.
3. Excel endpoint returns 200, XLSX attachment, and a valid OOXML ZIP signature.
4. PDF endpoint returns 200, PDF attachment, and a valid PDF signature.
5. Unauthorized organization-unit export returns 403.
6. Unit tests validate CSV sections, XLSX workbook parts, and PDF structure.
7. Frontend exports the currently selected unit/month/category filters.

## Browser smoke

1. Login as `budgetadmin`.
2. Select a fiscal year with report data and open Laporan.
3. Confirm CSV, Excel, and PDF buttons are visible.
4. With no filter, export each format and confirm the file downloads and opens.
5. Select one unit, one month, and one category.
6. Export CSV and confirm the exported unit/month/category sections reflect the active filter.
7. Export Excel and confirm sheets Ringkasan, Unit, Bulanan, and Kategori open correctly.
8. Export PDF and confirm the report is readable and the fiscal-year/unit amounts match the UI.
9. Login as a unit-scoped user such as `itpic` and confirm exports only include that permitted scope.
