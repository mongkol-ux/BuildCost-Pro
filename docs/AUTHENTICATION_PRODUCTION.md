# BuildCost Pro — Production Authentication Infrastructure

## Implemented

- Argon2 password hashing through `pwdlib`
- Short-lived signed access JWTs with issuer, session and token-type claims
- Opaque refresh tokens stored only as SHA-256 hashes
- Refresh-token rotation and server-side session revocation
- Email verification one-time tokens
- Password-reset one-time tokens with expiration and session invalidation
- Failed-login counter and temporary account lockout
- Authentication audit events
- Session listing, single-session revoke and revoke-all
- Security response headers, configured CORS and trusted-host boundary
- PostgreSQL migration for authentication tables

## Security rules

1. Never log passwords or raw refresh/reset/verification tokens.
2. Production must provide a unique `BUILD_COST_JWT_SECRET`; the development secret is rejected in production.
3. Refresh tokens must be rotated on every successful refresh. A revoked token is not reusable.
4. Password reset revokes every active session.
5. Email verification and password reset tokens are stored as hashes and are single-use.
6. Configure exact production hosts and frontend origins; do not use wildcard values.
7. Put the API behind TLS and a trusted reverse proxy in production.

## Required deployment sequence

1. Provision PostgreSQL.
2. Apply `apps/api/migrations/001_authentication.sql` through the project's migration runner.
3. Set all `BUILD_COST_*` environment variables from the deployment secret store.
4. Set `BUILD_COST_ENVIRONMENT=production`.
5. Set exact `BUILD_COST_ALLOWED_HOSTS` and `BUILD_COST_CORS_ORIGINS` values.
6. Run the API test suite and security integration tests in CI before deployment.
7. Connect email delivery for verification/reset workflows without exposing raw tokens in logs.

## API surface

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/verify-email`
- `POST /auth/password-reset/request`
- `POST /auth/password-reset/confirm`
- `GET /auth/sessions`
- `DELETE /auth/sessions/{session_id}`
- `POST /auth/sessions/revoke-all`
