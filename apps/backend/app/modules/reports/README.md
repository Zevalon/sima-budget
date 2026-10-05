# Reports Module

Phase 5A introduces the canonical, scope-aware reporting read model.

Current endpoint:

```text
GET /api/v1/reports/financial-summary?fiscal_year_id={id}
```

The module derives report totals from transactional tables and does not persist duplicate aggregate totals.

Later Phase 5 work must reuse this reporting layer for report UI and CSV/Excel/PDF exports.
