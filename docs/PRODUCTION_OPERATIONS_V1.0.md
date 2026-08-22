# BuildCost Pro V1.0 — Production Operations & Post-Go-Live

## Purpose

This runbook defines the operational baseline after V1.0 Go-Live. It is the operational source of truth for health checks, release verification, incident response, rollback, and routine maintenance.

## Production surface

- API runtime: Railway
- Public API health endpoint: `https://buildcost-pro-production.up.railway.app/health`
- Database: PostgreSQL
- Source of truth: `main` branch after release gates pass

## 1. Daily production checks

- Confirm `/health` returns HTTP 200.
- Confirm the health contract is exactly:
  - `status=ok`
  - `service=buildcost-pro-api`
  - `version=1.0.0`
- Confirm HTTPS security headers remain present.
- Confirm no unexpected production deployment is active.
- Review recent Railway deployment/runtime logs for startup, migration, database, and authentication errors.

## 2. Release checks

A release is PASS only when all of the following are green on the exact release commit:

1. API unit/integration tests.
2. Production database migrations.
3. Python compilation.
4. Production container build.
5. Public `/health` smoke test.
6. Production security-header/HSTS assertions.
7. Production configuration invariants.

Do not promote a release when any required gate is red or when the exact release commit cannot be identified.

## 3. Incident severity

### SEV-1 — production unavailable or data integrity risk

- Stop further releases immediately.
- Confirm the failing deployment and database health.
- Roll back to the last known-good production commit/deployment.
- Preserve logs and timestamps before destructive changes.
- Verify `/health` and a read-only business API after rollback.

### SEV-2 — major feature degraded

- Identify affected endpoint and deployment.
- Check application and database logs.
- Prefer a targeted rollback if the fault was introduced by the latest release.
- Re-run production smoke validation after recovery.

### SEV-3 — minor defect

- Record the issue.
- Reproduce outside production when possible.
- Fix through the normal PR/CI/release process.

## 4. Rollback procedure

1. Identify the current production commit/deployment.
2. Identify the last known-good release commit/deployment.
3. Roll back the Railway service to the known-good deployment.
4. Wait for runtime readiness.
5. Validate `/health` and security headers.
6. Validate one protected read-only API operation.
7. Record the incident and root cause before re-attempting release.

Database migrations must be backward-compatible with the rollback target. Never assume an application rollback can safely reverse a destructive schema migration.

## 5. Database safety

- Production migrations are applied by the application startup/release process.
- Schema changes must be committed together with application compatibility changes.
- Prefer additive migrations first; defer destructive cleanup until old application versions are no longer needed.
- Backups and restore capability are operational prerequisites for production data.

## 6. Security operations

Production must keep:

- non-default JWT secret with at least 32 characters;
- secure authentication cookies;
- HTTPS/HSTS;
- trusted-host validation;
- explicit CORS origins;
- public API documentation disabled in production;
- container process running as non-root.

Secrets must never be committed to Git.

## 7. Post-release observation

For each release, observe the first production window for:

- startup/restart loops;
- migration failures;
- authentication failures;
- database connection failures;
- elevated HTTP 4xx/5xx responses;
- unexpected latency or resource usage.

A release is operationally accepted only after the automated gates and the post-release observation checks pass.

## 8. Operational evidence

Keep the following evidence with each production release:

- release commit SHA;
- PR number and merge SHA;
- CI gate result;
- production deployment identifier;
- smoke-test result;
- incident/rollback record if applicable.

## Current V1.0 baseline

The public health contract is implemented in `apps/api/src/main.py`, and the release-candidate workflow contains the production runtime smoke and security-header gate. STEP 21 extends that baseline with an explicit operational runbook and repeatable post-Go-Live monitoring expectations.
