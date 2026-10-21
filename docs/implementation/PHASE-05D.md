# Phase 5D — Reporting Hardening & Phase 5 Completion

## Goal

Close the Monitoring & Reporting phase with historical-reporting safety, export hardening, and
final regression coverage.

## Historical reporting

Organization-unit deactivation must not erase historical financial visibility.

Reporting scope resolution therefore keeps inactive organizational units available when they are
still part of the caller's authorized scope. Existing allocations, approved commitments, and
realizations remain visible after a unit becomes inactive.

This is a reporting/history rule only. Deactivation rules for new operational transactions remain
unchanged.

## Export hardening

Financial report responses and downloads now use:

```text
Cache-Control: private, no-store
Pragma: no-cache
X-Content-Type-Options: nosniff
```

CSV text originating from configurable/master data is protected against spreadsheet-formula
injection.

CSV, Excel, and PDF outputs also include the active Unit, Month, and Category filter context so a
downloaded report can be interpreted independently from the browser session.

An unknown category filter is rejected instead of producing a misleading empty-category export.

## PDF hardening

Long report lines are wrapped instead of silently truncated. This preserves report text while
keeping the simple PDF generator dependency-free.

## UI stylesheet cleanup

The Phase 5C report stylesheet is normalized to remove duplicated declarations inside responsive
media queries.

## Completion gate

```bash
make phase5d-check
```

The gate runs the complete regression chain through Phase 5C and then verifies:

- historical inactive-unit reporting;
- canonical amount relationships;
- report anti-cache/security headers;
- filtered export metadata;
- invalid category rejection;
- CSV/PDF exporter hardening.

After browser smoke testing and CI/merge, create **CP-10 — Phase 5 Monitoring & Reporting
Complete** before starting Phase 6.
