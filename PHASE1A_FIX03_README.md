# SIMA Phase 1A — Fix 03

## Symptom

Phase 0 regression passes, migration succeeds, but Phase 1A bootstrap fails:

```text
ModuleNotFoundError: No module named 'app'
```

## Cause

The bootstrap script was executed by file path:

```bash
python scripts/bootstrap_foundation.py
```

When Python runs a file this way, `scripts/` becomes the effective script import location,
so the sibling `app/` package is not importable as expected.

## Fix

Run the scripts as modules from `apps/backend`:

```bash
python -m scripts.bootstrap_foundation
python -m scripts.verify_foundation
```

This keeps the backend project root on Python's import path.

The patch updates:

- `scripts/check-phase1a.sh`
- `Makefile`

## Apply

Extract over the repository root:

```bash
unzip -o SIMA_Phase1A_Fix03.zip -d ~/projects/sima-budget
chmod +x ~/projects/sima-budget/scripts/check-phase1a.sh
```

Then rerun:

```bash
cd ~/projects/sima-budget
make phase1a-check
```

No migration rollback, database reset, dependency reinstall, or Docker volume deletion is required.
