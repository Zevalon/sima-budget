# Phase 5B — Reports UI & Filters

## Objective

Turn the Phase 5A canonical reporting read model into an operational report screen without duplicating financial formulas in the frontend.

## Included

- report section navigation;
- organization-unit filter;
- month filter for the monthly realization breakdown;
- category filter for the category plan breakdown;
- server-side organization-unit filtering with RBAC scope validation;
- expanded unit table;
- monthly realization bar visualization;
- category commitment and draft-pipeline table;
- loading, empty, error, and active-filter states;
- stale report-response protection when filters change quickly.

## Unit filter semantics

`organization_unit_id` is an optional query parameter on:

```text
GET /api/v1/reports/financial-summary
```

The server first computes the user's permitted report scope and then validates the requested unit against that scope.

A unit outside the effective scope returns `403 Forbidden`.

When a unit filter is active:

- canonical totals are recalculated for that unit;
- monthly realization is recalculated for that unit;
- category commitment/pipeline is recalculated for that unit;
- `scope_budget_amount` becomes the unit allocation.

## Month filter semantics

The month filter only limits the monthly breakdown displayed by the UI.

It does not rewrite cumulative fiscal-year totals.

## Category filter semantics

The category filter limits the category commitment/pipeline breakdown.

Realized per category is intentionally not shown because Realization is currently stored at Budget Plan level rather than Budget Plan Item/category level.

## No financial formulas duplicated

The frontend formats and filters canonical values returned by the reporting API. It does not independently recalculate committed, realized, available, remaining, or utilization.

## No migration

Phase 5B adds no database table or column.
