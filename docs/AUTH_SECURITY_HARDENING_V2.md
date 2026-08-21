# Authentication Security Hardening V2

Implemented on `feature/auth-security-hardening-v2` as the next executable security slice after backend API hardening.

## Scope

1. Refresh-token rotation and session lifecycle (list/revoke/logout-all)
2. Password reset with single-use expiring tokens
3. Email verification with single-use expiring tokens
4. Login lockout and endpoint rate limits
5. Structured audit events
6. Security headers and explicit CORS allow-list
7. Role/permission dependency enforcement
8. Integration tests for the security flows

## Production boundary

The current bootstrap keeps storage in a reference in-memory store so the API can be tested deterministically without infrastructure. Before production launch, replace `SecurityStore` with transactional PostgreSQL repositories and Redis-backed rate limiting/token/session coordination, and provide `BCP_AUTH_SIGNING_KEY` from a secret manager. Do not return verification/reset tokens from production endpoints; deliver them through the configured email provider.

## Security invariants

- Passwords are never stored plaintext; PBKDF2-HMAC-SHA256 is used with a per-password random salt.
- Refresh tokens are opaque, stored only as SHA-256 hashes, rotated on use, and revoked on logout/password reset.
- Access tokens are short-lived and signed with a server-side secret.
- Password-reset and verification tokens are single-use and time-limited.
- Failed logins trigger temporary account lockout.
- Unknown password-reset requests return the same accepted response to reduce account enumeration.
- CORS is allow-list based; credentials are enabled only for configured origins.
- Fine-grained permissions are checked at route boundaries.
- Security events are auditable and should be persisted immutably in production.
