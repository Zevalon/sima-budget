# CP-05 — Testing & CI Matrix

| Area | Unit | Integration | API | Component | E2E | Manual |
|---|---:|---:|---:|---:|---:|---:|
| Authentication | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Users/RBAC | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Organization | ✓ | ✓ | ✓ | ✓ | ○ | ✓ |
| Fiscal Year | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Annual Budget | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Allocation | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Budget Plan | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Approval | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Realization | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Reports | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Settings | ✓ | ✓ | ✓ | ✓ | ○ | ✓ |
| Audit | ✓ | ✓ | ✓ | ✓ | ○ | ✓ |

`○` = when materially useful.

## Required Critical E2E Scenarios

1. Login → authorized dashboard.
2. Create Fiscal Year.
3. Create Annual Budget.
4. Submit and approve Annual Budget.
5. Allocate budget to a unit.
6. Unit PIC creates detailed plan.
7. Submit plan.
8. Multi-step approval.
9. Final approval commits budget.
10. Add realization.
11. Verify realization.
12. Dashboard/report totals reflect transaction.
13. Permission-denied user cannot access another unit.
14. Self-approval blocked.
15. Closed fiscal year rejects new transaction.

## Financial Concurrency

Mandatory integration scenarios:
- competing final approvals;
- allocation reduction vs commitments;
- concurrent realization near remaining ceiling;
- plan revision vs new commitments.

## CI Required Checks

Backend:
- `ruff check`
- format check
- mypy
- alembic upgrade on clean PostgreSQL
- pytest

Frontend:
- ESLint
- Prettier
- TypeScript
- Vitest
- production build

Contract:
- OpenAPI generated client freshness

E2E:
- Playwright critical path

Security:
- dependency/security scan
- secret detection where configured
