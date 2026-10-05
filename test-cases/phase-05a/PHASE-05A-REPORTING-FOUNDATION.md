# Phase 5A Test Cases

1. A role with `reports.view` can request the financial summary for an existing fiscal year.
2. A user without `reports.view` is rejected.
3. OWN_UNIT report totals only include that unit.
4. OWN_UNIT_AND_CHILDREN includes descendants but excludes unrelated branches.
5. ALL scope can aggregate the complete organization.
6. APPROVED current plan versions count as Committed.
7. DRAFT/PENDING_APPROVAL current plan versions count only in Plan Draft Pipeline.
8. POSTED realizations count as Realized.
9. DRAFT realizations count only in Realization Draft Pipeline.
10. REVERSED/CANCELLED realizations do not count in effective totals.
11. Remaining to Realize equals Committed minus Realized.
12. Monthly realization returns 12 stable month buckets.
13. Category plan summaries never fabricate category-level realization amounts.
14. Reports page follows the global fiscal-year selector.
