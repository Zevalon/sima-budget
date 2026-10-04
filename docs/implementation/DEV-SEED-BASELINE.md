# Development Seed Baseline

SIMA uses a deterministic development seed so local smoke testing does not depend on manually created data.

## Commands

Non-destructive refresh of the seed-managed records:

```bash
make dev-seed
```

Destructive reset of all application data followed by a fresh seed:

```bash
make dev-seed-reset CONFIRM=RESET
```

Verification only:

```bash
make dev-seed-verify
```

The reset command is intentionally guarded. It only runs with `APP_ENV=development`, a local PostgreSQL host, an approved development database name, and `CONFIRM=RESET`.

## Seed accounts

All seed accounts use `DEV_SEED_PASSWORD` (default development value: `SimaDev-2026!`).

| Username | Role | Scope |
| --- | --- | --- |
| sysadmin | System Administrator | ALL |
| budgetadmin | Budget Administrator | ALL |
| management | Management Approver | ALL |
| auditor | Auditor | ALL |
| viewer | Viewer | ALL |
| itpic | Unit PIC | OWN_UNIT / IT |
| itapprover | Unit Approver | OWN_UNIT / IT |
| ftipic | Unit PIC | OWN_UNIT_AND_CHILDREN / FTI |
| ftiapprover | Unit Approver | OWN_UNIT_AND_CHILDREN / FTI |

## Organization data

The seed creates realistic organization units including Finance, HR, IT, FTI, FEB, Informatics study program, LPPM, and Library. Budget-receiving units are marked `can_receive_budget=true`; operational units are also prepared with `can_create_budget_plan=true` for Phase 3.

## Fiscal/budget scenarios

- FY2024 — CLOSED, approved historical Annual Budget.
- FY2025 — ACTIVE, approved Annual Budget with historical allocation data.
- FY2026 — PLANNING, approved Annual Budget Rp 600B, with Rp 300B allocated and Rp 300B remaining. This is the primary Phase 2C/Phase 3 development scenario.
- FY2027 — DRAFT, intentionally without an Annual Budget.

Approval history includes approved and rejected/resubmitted examples.

## Seed coverage

The baseline seeds all persistent tables implemented through Phase 2C. `user_sessions` is a runtime/security table; it is cleared on reset and only one expired/revoked sample session is inserted. No usable authenticated session token is seeded.

Tables introduced in future phases must extend the same `scripts/seed_dev.py` baseline instead of creating unrelated seed scripts.
