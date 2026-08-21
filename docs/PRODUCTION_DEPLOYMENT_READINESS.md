# BuildCost Pro V1.0 — Production Deployment Readiness & Final API Production Gate

## Gate objective

This gate is the final release boundary before BuildCost Pro API is allowed to run against production traffic.

A green CI run is necessary but not sufficient. Production launch requires both automated checks and the operational dependencies listed below.

## Current baseline

- Authentication flow: Register → Verify Email → Login → Refresh Rotation → Session Revoke → Password Reset → Lockout → Audit Log.
- Security headers and CORS are implemented.
- Integration tests cover the authentication/security contract.
- The current security store is deterministic in-memory and is therefore **not production storage**.
- Refresh/session state, rate limits, one-time tokens and audit events must be moved to durable/shared infrastructure before launch.

## Mandatory production blockers

The deployment MUST remain blocked until all items below are true:

1. PostgreSQL is configured as the authoritative application/security database.
2. Redis (or an equivalent shared atomic store) is configured for rate limiting and distributed session/token coordination where required.
3. A real transactional email provider is configured for verification and password-reset delivery.
4. `BCP_AUTH_SIGNING_KEY` is supplied by a production secret manager, is unique to the environment, and is never committed to source control.
5. CORS contains only approved production origins; wildcard origins are forbidden when credentials are enabled.
6. HTTPS/TLS terminates correctly and HSTS is enabled for production traffic.
7. Database migrations run successfully against a production-like PostgreSQL instance before release.
8. Backups, restore verification and rollback procedures have been tested.
9. Observability is enabled: structured logs, metrics, health checks and alerting for authentication failures, lockouts, 5xx errors and dependency failures.
10. Secrets, credentials and tokens are excluded from logs and telemetry.
11. A production smoke test validates the complete authentication lifecycle against real infrastructure.
12. No unresolved critical/high security finding remains in the release candidate.

## Final API production gate

### Automated gate

- Python dependency installation succeeds.
- Unit/integration tests pass.
- Authentication lifecycle tests pass.
- Refresh token rotation rejects reuse of the previous token.
- Session revocation invalidates access tokens immediately.
- Password reset invalidates existing sessions.
- Lockout and rate-limit boundaries are enforced.
- Security headers are present.
- Permission boundaries return 403 for unauthorized roles.
- Account enumeration is not disclosed by password-reset requests.
- Production configuration validation passes.

### Deployment gate

- [ ] Production PostgreSQL reachable and migration version verified.
- [ ] Shared Redis/rate-limit infrastructure reachable.
- [ ] Production email provider reachable and test message delivered.
- [ ] Production secret manager configured.
- [ ] Approved CORS origins configured.
- [ ] TLS/HSTS verified.
- [ ] Backup and restore test completed.
- [ ] Monitoring/alerts verified.
- [ ] Production authentication smoke test completed.
- [ ] Rollback tested.

## Release decision

**GO** only when every mandatory blocker and deployment checkbox is satisfied.

**NO-GO** if any mandatory dependency is missing, if the service falls back to in-memory security state, if secrets are embedded in configuration/source, or if the end-to-end production smoke test fails.

## Recommended deployment sequence

1. Build immutable API artifact.
2. Run the CI production gate.
3. Apply/verify database migrations in staging.
4. Deploy to staging with production-like PostgreSQL/Redis/email services.
5. Run the complete authentication smoke test.
6. Verify telemetry, alerts, backup and rollback.
7. Promote the exact tested artifact to production.
8. Run post-deploy health and authentication smoke checks.
9. Keep rollback available until the release observation window closes.
