# STEP 24 — V1.0 Post-Release Governance & Operational Baseline

## Objective

Establish the controlled operating baseline after V1.0 release closure without reopening the V1.0 release gate.

## Scope

- Preserve `main` as the V1.0 production source of truth.
- Keep production health and security verification automated.
- Separate historical deployment failures from current production evidence.
- Require evidence before any future production change is promoted.
- Keep release evidence immutable and auditable.

## Current repository baseline

- Repository: `mongkol-ux/BuildCost-Pro`
- Default branch: `main`
- Release line: V1.0
- Production URL: `https://buildcost-pro-production.up.railway.app`
- Production RC workflow: `.github/workflows/release-candidate.yml`
- Production operations monitor: `.github/workflows/production-ops-health.yml`

## Operational controls

### 1. Production health gate

The production RC workflow must validate the public `/health` contract and, on `main`, the required security headers and HSTS before a production release is accepted.

### 2. Scheduled production monitoring

The production operations workflow is the recurring runtime guard. A monitoring failure is an operational incident signal and must not be silently treated as a release pass.

### 3. Change control

Any post-V1.0 code change must enter through the normal Git workflow and pass applicable CI before promotion to `main`. Direct production changes outside the repository-controlled release path are not part of the approved baseline.

### 4. Evidence integrity

Release evidence must identify the exact commit, workflow result, production verification result, and release decision. Historical failures remain historical evidence and must not be overwritten or reclassified.

### 5. Rollback readiness

If a production change fails its health/security contract, stop promotion and restore the last known-good production commit through the controlled deployment path. Do not bypass the verification gate to force a release.

## V1.0 boundary

STEP 24 does not introduce a new V1.0 feature scope. It establishes the post-release operating discipline required to keep the accepted V1.0 baseline stable.

## Acceptance criteria

- [x] Post-release governance scope documented.
- [x] Production verification contract remains defined in the repository.
- [x] Production monitoring remains part of the repository baseline.
- [x] Historical deployment evidence is explicitly distinguished from current runtime evidence.
- [x] Future changes are required to pass controlled CI/release verification.
- [x] Rollback principle is documented.

## STEP 24 decision

**STATUS: COMPLETE — POST-RELEASE GOVERNANCE BASELINE ESTABLISHED**

V1.0 remains the controlled production baseline. Future work proceeds as a new change/release cycle and must not silently mutate the accepted V1.0 evidence.
