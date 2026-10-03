# SIMA Phase 1B — Apply

Apply over the Phase 1A-complete repository:

```bash
unzip -o SIMA_Phase1B_Authentication_Session.zip -d ~/projects/sima-budget
chmod +x ~/projects/sima-budget/scripts/check-phase1b.sh

cd ~/projects/sima-budget
make phase1b-check
```

No database reset or volume deletion is required.

After the automated gate passes, create the real first administrator:

```bash
make bootstrap-admin
```

Then run backend/frontend and login through:

```text
http://localhost:5173/login
```

Only after the automated + manual login smoke test passes should Phase 1B be committed.
