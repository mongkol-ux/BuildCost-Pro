# BuildCost Pro — STEP 45 V1.2 Production Handover

**Status:** IN PROGRESS

## Purpose

Close the V1.2 release only when its production evidence, operational ownership, backup/restore readiness, and release record are complete. This handover does not add product scope and must not bypass a failed release gate.

## Confirmed release evidence

| Check | Evidence | Status |
|---|---|---|
| STEP 44 production release gate | Approved production release gate for the current V1.2 baseline | PASS |
| API production container smoke | PostgreSQL-backed container migration/startup and `/health` contract in the STEP 44 gate | PASS |
| Authentication and protected routes | STEP 44 API boundary tests | PASS |
| Web production health and security | STEP 44 public `/api/health` and security-header assertions | PASS |
| Operational baseline | `docs/PRODUCTION_OPERATIONS_V1.0.md` | DOCUMENTED |
| Rollback policy | `docs/STEP-43-RELEASE-CANDIDATE-ROLLBACK.md` | DOCUMENTED |

## Required closure checklist

- [x] Resolve release-blocking CI/production gate failures.
- [x] Record the approved release commit and successful production gate.
- [x] Reconcile the execution tracker with STEP 44 evidence.
- [ ] Confirm the PostgreSQL backup owner, schedule, retention policy, and backup location in the production platform.
- [ ] Perform and record a non-production restore drill from a production-compatible backup. The record must include backup identifier, restore target, start/end times, result, and verifier.
- [ ] Verify the restored database with migration/schema checks and a protected read-only API request.
- [ ] Confirm the on-call/operational owner and incident escalation route.
- [ ] Create an immutable V1.2 release tag after every item above is complete.
- [ ] Declare STEP 45 `DONE — V1.2 PRODUCTION READY` only after the checklist has dated evidence.

## Automated STEP 45 gate

`.github/workflows/step45-production-ready.yml` validates the handover evidence framework, required release/rollback/operations documents, and prevents the automation from falsely declaring STEP 45 complete while dated backup/restore, operational-owner, and immutable-tag evidence remains missing.

## Backup and restore procedure

1. Before a release, verify that the production PostgreSQL platform reports a current successful backup and record its identifier and timestamp.
2. Restore that backup into an isolated, non-production PostgreSQL instance; never rehearse a restore over the live database.
3. Run the checked-in migration chain against the restored copy. It must finish without errors and expose the required schema tables.
4. Start the release API against the restored copy using production-safe configuration, then verify `/health` and one authenticated, read-only route.
5. Record the evidence in the release record. If any check fails, stop release closure and use the STEP 43 rollback policy; do not attempt destructive recovery on the live database.

## Closure rule

The successful STEP 44 run establishes deployability, but it is not evidence of a completed restore drill or release tag. Until those remaining controls are verified, STEP 45 remains **IN PROGRESS**.
