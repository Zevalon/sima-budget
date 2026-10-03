# SIMA Phase 1A Patch

Apply this patch over the current Phase 0-complete repository.

```bash
unzip -o SIMA_Phase1A_Identity_Database_Foundation.zip -d ~/projects/sima-budget
chmod +x ~/projects/sima-budget/scripts/check-phase1a.sh
cd ~/projects/sima-budget
make phase1a-check
```

Do not delete the current PostgreSQL volume. Alembic will migrate the existing development database forward.

If the check passes:

```bash
git add .
git commit -m "feat(foundation): add identity and RBAC data model"
git push
```

Do not create the Phase 1 milestone tag yet; Phase 1A is only the first subphase of Phase 1.
