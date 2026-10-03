# CP-05 — Final Repository Structure

```text
sima-budget/
├── apps/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   ├── dependencies/
│   │   │   │   └── v1/
│   │   │   ├── core/
│   │   │   │   ├── config.py
│   │   │   │   ├── database.py
│   │   │   │   ├── logging.py
│   │   │   │   ├── security.py
│   │   │   │   └── errors.py
│   │   │   ├── modules/
│   │   │   │   ├── auth/
│   │   │   │   ├── users/
│   │   │   │   ├── roles/
│   │   │   │   ├── organizations/
│   │   │   │   ├── fiscal_years/
│   │   │   │   ├── annual_budgets/
│   │   │   │   ├── allocations/
│   │   │   │   ├── budget_categories/
│   │   │   │   ├── budget_plans/
│   │   │   │   ├── approvals/
│   │   │   │   ├── realizations/
│   │   │   │   ├── reports/
│   │   │   │   ├── notifications/
│   │   │   │   ├── audit/
│   │   │   │   └── settings/
│   │   │   ├── shared/
│   │   │   │   ├── db/
│   │   │   │   ├── files/
│   │   │   │   ├── pagination/
│   │   │   │   ├── permissions/
│   │   │   │   └── types/
│   │   │   └── main.py
│   │   ├── alembic/
│   │   ├── tests/
│   │   │   ├── unit/
│   │   │   ├── integration/
│   │   │   └── api/
│   │   ├── scripts/
│   │   ├── pyproject.toml
│   │   ├── alembic.ini
│   │   └── .env.example
│   │
│   └── frontend/
│       ├── src/
│       │   ├── app/
│       │   ├── components/
│       │   │   ├── ui/
│       │   │   └── shared/
│       │   ├── features/
│       │   │   ├── auth/
│       │   │   ├── users/
│       │   │   ├── organization/
│       │   │   ├── budgets/
│       │   │   ├── plans/
│       │   │   ├── approvals/
│       │   │   ├── realizations/
│       │   │   ├── reports/
│       │   │   ├── notifications/
│       │   │   └── settings/
│       │   ├── layouts/
│       │   ├── lib/
│       │   │   ├── api/
│       │   │   ├── auth/
│       │   │   ├── formatting/
│       │   │   └── validation/
│       │   ├── routes/
│       │   ├── styles/
│       │   └── types/
│       ├── tests/
│       ├── e2e/
│       ├── public/
│       ├── package.json
│       └── .env.example
│
├── docs/
│   ├── project-context/
│   ├── checkpoints/
│   ├── architecture/
│   ├── adr/
│   ├── database/
│   ├── api/
│   ├── installation/
│   ├── deployment/
│   ├── testing/
│   ├── security/
│   └── user-guide/
├── test-cases/
├── logs/testing/
├── scripts/
├── docker/
├── .github/
├── compose.yml
├── compose.dev.yml
├── Makefile
├── README.md
├── CONTRIBUTING.md
├── SECURITY.md
├── CHANGELOG.md
└── .gitignore
```

## Repository Rules

- Repository contains source, migrations, docs, tests, examples.
- Repository never contains real secrets.
- Uploaded runtime files are excluded.
- Runtime logs are excluded.
- Python virtualenv and `node_modules` are excluded.
- Database volumes/dumps are excluded unless sanitized fixture explicitly intended for tests.
- Generated frontend OpenAPI client may be committed or CI-generated, but one consistent policy must be chosen at scaffold. Baseline recommendation: commit generated type/client code and verify freshness in CI.
