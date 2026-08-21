# BuildCost Pro — Production Runtime Smoke Test

## Purpose

This runbook is the final gate between a deployable production image and GO-LIVE. It must be executed against the real HTTPS production URL, never against localhost or CI-only services.

## Preconditions

- `main` contains the approved release commit.
- Production PostgreSQL is reachable from the API runtime.
- Production database migrations have been applied successfully.
- Production JWT/auth signing secret is configured outside Git.
- Production CORS and allowed-host settings match the real frontend/runtime domains.
- Real email delivery is configured and verified.
- TLS/HTTPS is active.

## Smoke sequence

1. `GET /health` returns HTTP 200 and `status=ok`.
2. Register a disposable test account.
3. Verify email using the real delivery path.
4. Login and obtain access + refresh tokens.
5. Refresh once and confirm refresh-token rotation.
6. Reuse the previous refresh token and confirm rejection.
7. List sessions and revoke the test session.
8. Confirm the revoked session cannot authenticate.
9. Request password reset through the real email provider.
10. Complete password reset and confirm active sessions are invalidated.
11. Trigger failed-login threshold and confirm lockout/rate limiting.
12. Confirm audit events exist for registration, verification, login, refresh, revoke, reset and lockout.
13. Confirm security headers and HTTPS behavior.

## PASS criteria

Every step must pass against the same production deployment. Any failure is an immediate HOLD; do not send production traffic.

## Evidence

Record the deployment URL, release commit SHA, migration result, smoke-test timestamp, and PASS/FAIL result. Never record passwords, tokens, API keys, or other secrets.
