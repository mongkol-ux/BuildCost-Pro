# BuildCost Pro — Production Release Candidate Validation

## Release Candidate Gate

A release candidate is eligible for production only when every gate below is green:

1. Repository baseline is on `main` and the release candidate branch is based on the current `main`.
2. PostgreSQL 16 starts successfully in CI.
3. Authentication migration applies successfully to a clean database.
4. API imports successfully under production environment settings.
5. Unit and integration tests pass.
6. Python source compilation passes.
7. Security boundary remains enabled: Trusted Hosts, CORS allow-list, security headers and production HSTS.
8. Authentication lifecycle remains covered: register, email verification, login, refresh rotation, session revoke, password reset, lockout and audit logging.
9. No production secrets are committed; `.env.example` contains placeholders only.
10. CI status is green on the exact release candidate commit before merge.

## Current Validation Evidence

- Repository: `mongkol-ux/BuildCost-Pro`
- Default branch: `main`
- Authentication PR #5: merged into `main`.
- Merge commit: `3538c0db1032a7d160b2873ce4ba740aa7fe1e00`.
- RC validation workflow added in this branch: `.github/workflows/release-candidate.yml`.

## Production Blockers

- Real production PostgreSQL credentials and migration execution must be supplied by the deployment environment.
- Real email delivery/provider integration must be configured and verified before enabling email verification and password reset for production traffic.
- CI must execute successfully on the release candidate commit; a previously merged commit had no recorded workflow run, so that historical absence is not treated as a pass.

## Release Decision Rule

`PASS` only when all required gates have current CI evidence. Otherwise the release remains `HOLD` and must not receive production traffic.
