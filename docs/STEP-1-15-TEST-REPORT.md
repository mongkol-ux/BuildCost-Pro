# BuildCost Pro — STEP 1–15 Test Report

**Test scope:** STEP 1–15
**Repository:** `mongkol-ux/BuildCost-Pro`
**Branch:** `main`
**Baseline commit:** `72d43e8f0f93685c370be6243b076ca375b1becc`
**Test date:** 2026-08-31
**Method:** GitHub source/config/test/CI inspection + GitHub Actions status inspection

## Executive Result

**STEP 1–15: HOLD — NOT CLEARED FOR STEP 16**

The source, configuration, migrations and test assets are present and structurally aligned with the locked STEP workflow. However, the current commit has a failing Production Operations Health Monitor run. Because the master workflow requires failed gates to block progression, STEP 16 must remain closed until production health is restored and verified.

## STEP Matrix

| STEP | Scope | Source/Test Evidence | Result |
|---:|---|---|---|
| 1 | Requirements / System Baseline | Master workflow and roadmap present | PASS |
| 2 | Core Architecture | API/web structure and deployment artifacts present | PASS |
| 3 | Data Model | PostgreSQL migrations 001/002 present | PASS |
| 4 | API Foundation | FastAPI app, routers, schemas, services and API tests present | PASS |
| 5 | Authentication | Auth models/router/security/service + integration tests present | PASS |
| 6 | Authorization | Role/session claims and protected auth boundary present; deeper RBAC coverage remains limited | WARNING |
| 7 | Database / Persistence | SQL migrations + SQLAlchemy persistence + integration tests present | PASS |
| 8 | Core Business Logic | Calculation and validation tests present | PASS |
| 9 | Frontend Foundation | Next.js/React project and production build workflow present | PASS |
| 10 | Core UI | Web source exists and build workflow exists; runtime UI evidence not executed in this audit | WARNING |
| 11 | Project Module | Project schema/service/router/tests present | PASS |
| 12 | Budget Module | Budget schema/model/service coverage present; reconciliation evidence limited | WARNING |
| 13 | Cost Module | Cost schema/model/service and calculation tests present | PASS |
| 14 | Transaction Module | Transaction model/schema/service and validation tests present | PASS |
| 15 | Dashboard / Summary | Financial summary calculation is tested; UI runtime verification not evidenced | WARNING |

## Source / Configuration Findings

### Positive

- API runtime configuration uses `BUILD_COST_` environment prefix and validates production JWT/cookie settings.
- Production configuration rejects the development JWT secret and insecure cookies.
- Authentication migration creates users, sessions, one-time tokens and audit logs.
- Core migration creates projects, budgets, costs and transactions with constraints and indexes.
- API CI provisions PostgreSQL, applies migrations and runs `pytest -q`.
- Required API test workflow exists for pull requests into `main`.
- Web CI installs Node dependencies and runs the production build.
- Production deployment uses `/health` as the Railway healthcheck.

## Test Suite Findings

Observed API tests include:

- `/health` and HSTS verification
- password hashing and verification
- JWT claim validation
- wrong-secret rejection
- financial summary calculations
- project-code validation
- transaction validation
- end-to-end registration/email verification/login/refresh rotation/session revoke/password reset/lockout/audit events

## CI / Commit Evidence

The current commit has GitHub status entries reporting success for the connected Railway deployments, but the GitHub Actions production-health workflow for the same commit is failing.

Observed failing runs:

- Production Operations Health Monitor, run `33410209274` — failure
- Production Operations Health Monitor, run `33411791388` — failure

Both failures occur in the `Check public production API health` step.

The workflow checks:

1. `/health` response
2. security headers
3. Permissions-Policy
4. HSTS

Because the workflow is a production verification gate, this is a release blocker rather than a cosmetic CI warning.

## Root-Cause Status

**Confirmed:** the production health gate is failing.

**Not yet confirmed from available evidence:** whether the cause is service availability, deployment state, response content, or one of the required security headers. The workflow log endpoint was not available through the current connector surface, so no unsupported root cause is being invented.

## Required Fixes Before STEP 16

### BLOCKER-01 — Production health gate

Restore the public production API so the Production Operations Health Monitor passes all assertions.

Acceptance evidence required:

- HTTP 200 from `/health`
- exact expected JSON body
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: no-referrer`
- exact Permissions-Policy expected by workflow
- HSTS with `max-age=31536000` and `includeSubDomains`

### WARNING-01 — Runtime UI evidence

Run the deployed web application and record evidence for core UI screens before declaring STEP 10/15 fully closed.

### WARNING-02 — RBAC depth

Expand authorization tests for role/resource ownership boundaries before the security-focused later gates.

### WARNING-03 — Budget reconciliation

Add explicit budget-vs-cost-vs-transaction reconciliation tests before the integration baseline.

## Gate Decision

Per the locked workflow, a failed gate blocks progression. Therefore:

```text
STEP 1–15 = HOLD
STEP 16    = CLOSED / NOT STARTED

Required next action:
1. Diagnose production-health failure.
2. Fix production/runtime issue.
3. Re-run Production Operations Health Monitor.
4. Verify API test and web build CI evidence.
5. Re-run the STEP 1–15 gate review.
6. Only then open STEP 16.
```

## Important Test Limitation

A local `pytest`/`npm build` execution could not be performed from the current execution environment because outbound DNS/network access to GitHub is unavailable. Therefore this report does not fabricate local test counts. GitHub repository source and GitHub Actions evidence are used where available.
