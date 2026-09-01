# STEP 43 — Production Rollback Plan

## Objective
Provide a safe recovery path if the V1.2 release candidate causes a production regression.

## Deployment rollback
1. Stop promotion of the failing release candidate.
2. Identify the last known-good production commit from the release evidence.
3. Roll back the application deployment to that known-good immutable commit/image.
4. Verify `/api/health`, authentication, and core protected routes.
5. Run the production operations health monitor and record evidence.

## Database safety
The application deployment rollback must not assume that database changes can be reversed automatically. Checked-in migrations are forward-applied SQL and are not treated as reversible unless an explicit down/restore procedure has been tested.

For a release containing schema changes:
- Prefer backward-compatible migrations.
- Keep the previous application version compatible during the rollback window.
- If data restoration is required, use the approved database backup/restore procedure rather than ad-hoc destructive SQL.
- After recovery, create a forward-fix release if the schema must remain at the newer version.

## Rollback verification
- [ ] Known-good release identified.
- [ ] Application rollback completed.
- [ ] Public health contract passes.
- [ ] Authentication/protected-route smoke passes.
- [ ] Production operations health passes.
- [ ] Incident/release evidence recorded.

## Approval rule
STEP 43 release approval requires this rollback procedure to be understood and executable. It does not claim that a live production rollback has been performed; that belongs to the production-release/handover stages.
