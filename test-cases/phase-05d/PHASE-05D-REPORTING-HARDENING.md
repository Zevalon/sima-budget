# Phase 5D Test Cases — Reporting Hardening

## Automated

1. Full Phase 5C regression remains green.
2. Financial summary response has `private, no-store` cache policy.
3. Export response has `private, no-store`, `no-cache`, and `nosniff` headers.
4. Deactivating a unit with historical finance records does not remove it from the report.
5. The same inactive unit can still be selected when it remains inside the caller's report scope.
6. `Available = Allocated - Committed`.
7. `Remaining to Realize = Committed - Realized`.
8. Export contains active filter context.
9. Unknown category export filter is rejected with `404`.
10. CSV configurable text is protected against spreadsheet-formula injection.
11. PDF long text is wrapped rather than silently truncated.

## Browser smoke

1. Login as `budgetadmin` and open Laporan for a fiscal year with data.
2. Confirm report cards, unit table, monthly breakdown, category breakdown, and filters still work.
3. Export CSV / Excel / PDF without filters and open each file.
4. Apply Unit + Month + Category filters and export again.
5. Confirm each downloaded file states the active filter context.
6. Confirm downloaded values match the active browser report.
7. Confirm browser console/network has no report errors.
8. If an inactive historical unit exists in development data, confirm its historical report can
   still be viewed by an authorized user.
9. Login as a scoped user and confirm no out-of-scope unit can be viewed or exported.
