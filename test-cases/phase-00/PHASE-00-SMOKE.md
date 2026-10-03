# PHASE-00-SMOKE

## TEST ID
PHASE-00-001

## Scenario
Fresh development scaffold can be bootstrapped and started.

## Preconditions
- WSL development prerequisites installed.
- Docker Desktop running.
- Internet available for first dependency install.

## Steps
1. Copy `.env.example` files.
2. Run `./scripts/bootstrap-dev.sh`.
3. Run `make backend-dev`.
4. Run `make frontend-dev`.
5. Open frontend.
6. Request `/health/live`.
7. Request `/health/ready` with PostgreSQL running.
8. Run `make phase0-check`.

## Expected
- Dependency lock files generated.
- PostgreSQL healthy.
- Frontend dashboard scaffold renders.
- Liveness returns 200.
- Readiness returns 200.
- Local checks pass.

## Actual Result
To be completed on the target development device.

## Status
NOT EXECUTED ON TARGET DEVICE
