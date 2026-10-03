# Development Installation

## Prerequisites

- Windows 11 recommended
- WSL 2 + Ubuntu
- Node.js 24 LTS via NVM
- Python 3.14 managed through uv
- Docker Desktop with WSL integration
- Git

## First Run

```bash
git clone <repository>
cd sima-budget
cp .env.example .env
cp apps/backend/.env.example apps/backend/.env
cp apps/frontend/.env.example apps/frontend/.env
./scripts/bootstrap-dev.sh
```

Bootstrap generates dependency lock files. Review them and commit them before feature work.

## Development

```bash
make backend-dev
make frontend-dev
```

PostgreSQL:

```bash
make dev-db-status
```

## Verification

```bash
make phase0-check
```
