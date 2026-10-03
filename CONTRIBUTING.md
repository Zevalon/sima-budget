# Contributing

## Branches

Gunakan:

- `feature/*`
- `fix/*`
- `chore/*`
- `docs/*`

Perubahan normal masuk ke `main` melalui Pull Request.

## Commit Convention

Gunakan Conventional Commits:

```text
feat(plans): add budget item validation
fix(approval): prevent self approval
docs: update development setup
```

## Before Opening a Pull Request

```bash
make lint
make typecheck
make test
```

Untuk perubahan finansial, pastikan test business rule, transaction boundary, audit, permission, dan concurrency yang relevan ikut diperbarui.

## Architectural Changes

Perubahan terhadap business rule atau architecture baseline tidak boleh dilakukan diam-diam. Update checkpoint/ADR yang relevan.
