# Development Seed Baseline — Acceptance Cases

1. `make dev-seed-reset CONFIRM=RESET` rejects non-development/non-local databases.
2. Reset preserves the Alembic schema version while deleting application rows.
3. Foundation bootstrap is recreated after reset.
4. All standard roles and permissions are available.
5. Seed users can authenticate with the documented development password.
6. Exactly one ACTIVE and one PLANNING fiscal year exist in the baseline.
7. FY2026 has an APPROVED Annual Budget of Rp 600B.
8. FY2026 has Rp 300B allocated and Rp 300B remaining.
9. At least one eligible budget-receiving unit remains unallocated so the Unit Allocation create form is testable.
10. A revoked/expired session sample exists; no active fake session is seeded.
11. Seed audit marker `DEV_SEED_APPLIED` exists.
12. Future phase seed additions extend the same seed baseline.
