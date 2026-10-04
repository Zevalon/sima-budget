# SIMA Phase 3B — Budget Plan Submission & Approval

Phase 3B extends the Phase 3A Budget Plan core with submission, scoped unit approval,
rejection, immutable rejected-version history, revision to a new version, resubmission,
and approval history.

## Main flow

```text
DRAFT
  -> PENDING_APPROVAL
       -> APPROVED
       -> REJECTED
            -> revise -> DRAFT (new version)
```

The exact submitted `BudgetPlanVersion` is stored on every approval record.

## Authority

- Unit PIC: view/create/update/submit/revise within assigned scope.
- Unit Approver: view/approve/reject within assigned scope.
- Budget Administrator/System Administrator: read-only for Budget Plans by default.
- Self approval follows `allow_self_approval` and remains disabled by default.

## Apply

```bash
unzip -o SIMA_Phase3B_Budget_Plan_Approval.zip -d ~/projects/sima-budget
chmod +x ~/projects/sima-budget/scripts/check-phase3b.sh

cd ~/projects/sima-budget/apps/backend
uv run ruff check . --fix
uv run ruff format .

cd ~/projects/sima-budget/apps/frontend
npm run format

cd ~/projects/sima-budget
make phase3b-check
```

Do not reset the PostgreSQL volume. Alembic migration `20261004_0006` is applied by
the checker.

After the gate passes, refresh the cumulative development baseline with:

```bash
make dev-seed-reset CONFIRM=RESET
```
