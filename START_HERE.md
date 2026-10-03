# START HERE — SIMA Phase 0

Source code di folder ini adalah implementasi awal berdasarkan CP-01 sampai CP-05.

## 1. Pindahkan ke WSL

Simpan project di filesystem Linux, misalnya:

```bash
~/projects/sima-budget
```

## 2. Bootstrap

```bash
cd ~/projects/sima-budget
cp .env.example .env
cp apps/backend/.env.example apps/backend/.env
cp apps/frontend/.env.example apps/frontend/.env
./scripts/bootstrap-dev.sh
```

Bootstrap pertama membutuhkan internet untuk mengunduh dependency dan menghasilkan:

```text
apps/backend/uv.lock
apps/frontend/package-lock.json
```

Kedua lock file tersebut harus di-commit ke Git.

## 3. Jalankan aplikasi

Terminal 1:

```bash
make backend-dev
```

Terminal 2:

```bash
make frontend-dev
```

## 4. Buka

```text
http://localhost:5173
http://localhost:8000/docs
http://localhost:8000/health/live
http://localhost:8000/health/ready
```

## 5. Verifikasi

```bash
make phase0-check
```

Jika semua PASS, Phase 0 selesai dan development dapat lanjut ke Phase 1 — Foundation.

## GitHub

Jika private repository Anda masih kosong, copy seluruh isi folder ini ke working tree repository yang sudah Anda clone, lalu:

```bash
git add .
git commit -m "chore: scaffold SIMA application"
git push origin main
```

Pastikan `.env` tidak ikut masuk ke commit.
