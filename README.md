# SIMA — Sistem Informasi Monitoring Anggaran

SIMA adalah aplikasi web untuk perencanaan, alokasi, persetujuan, realisasi, monitoring, dan pelaporan anggaran tahunan organisasi. Deployment pertama ditujukan untuk kebutuhan internal universitas, tetapi domain aplikasi dibuat generik agar dapat digunakan organisasi lain.

> Status: **Implementation Phase 0 — Repository & Tooling Scaffold**

## Stack

- Frontend: React + TypeScript + Vite
- Backend: FastAPI + Python
- Database: PostgreSQL
- Migration: Alembic
- Local infrastructure: Docker Compose
- Architecture: modular monolith + monorepo

## Quick Start — WSL/Ubuntu

Prerequisites sudah diasumsikan tersedia: Git, Node.js 24 LTS, npm, Python 3.14 melalui `uv`, Docker Desktop + WSL integration.

```bash
cp .env.example .env
cp apps/backend/.env.example apps/backend/.env
cp apps/frontend/.env.example apps/frontend/.env

./scripts/bootstrap-dev.sh
```

Setelah bootstrap:

Terminal 1:

```bash
make backend-dev
```

Terminal 2:

```bash
make frontend-dev
```

Buka:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- API docs (development): `http://localhost:8000/docs`
- Liveness: `http://localhost:8000/health/live`
- Readiness: `http://localhost:8000/health/ready`

## PostgreSQL Saja via Docker

```bash
make dev-db-up
make dev-db-status
```

## Full Docker Stack

Setelah dependency lock files terbentuk dari bootstrap pertama:

```bash
docker compose up --build
```

## Quality Commands

```bash
make lint
make typecheck
make test
```

Backend-only:

```bash
cd apps/backend
uv run pytest
uv run ruff check .
uv run mypy app tests
```

Frontend-only:

```bash
cd apps/frontend
npm run lint
npm run typecheck
npm run test
npm run build
```

## Important: Dependency Locks

Execution workspace yang membuat scaffold ini tidak memiliki akses package registry. Karena itu `uv.lock` dan `package-lock.json` **harus dihasilkan pada development machine Anda yang memiliki internet** melalui `./scripts/bootstrap-dev.sh`, kemudian commit kedua lock file tersebut sebelum mulai feature development.

Direct dependency versions sudah ditentukan di manifest; lock file menjadi sumber pin transitive dependencies.

## Project Documentation

- Context terbaru: `docs/project-context/PROJECT_CONTEXT.md`
- Checkpoint CP-01…CP-05: `docs/checkpoints/`
- ADR: `docs/adr/`
- Installation: `docs/installation/`
- Testing: `docs/testing/`

## Current Implementation Gate

Phase 0 dianggap selesai ketika:

- clean clone dapat di-bootstrap;
- PostgreSQL berjalan;
- FastAPI `/health/live` dan `/health/ready` bekerja;
- frontend shell tampil;
- lint/typecheck/test commands bekerja;
- CI skeleton ada;
- checkpoint project tersimpan di repository;
- tidak ada secret yang di-commit.

Lihat `docs/implementation/PHASE-00.md`.
