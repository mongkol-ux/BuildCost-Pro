"""Authentication and security hardening primitives for BuildCost Pro.

The service is intentionally dependency-light for the bootstrap. Storage and
email delivery are behind interfaces so the same contracts can be backed by
PostgreSQL/Redis/SMTP in production without changing API semantics.
"""
from __future__ import annotations

import hashlib, hmac, secrets, time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Callable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

PBKDF2_ITERATIONS = 310_000
ACCESS_TTL_SECONDS = 900
REFRESH_TTL_SECONDS = 60 * 60 * 24 * 30
RESET_TTL_SECONDS = 30 * 60
VERIFY_TTL_SECONDS = 24 * 60 * 60
LOCKOUT_SECONDS = 15 * 60
MAX_FAILED_LOGINS = 5


def now() -> datetime:
    return datetime.now(timezone.utc)


def _hash_secret(value: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac("sha256", value.encode(), salt, PBKDF2_ITERATIONS).hex()


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${_hash_secret(password, salt)}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algo, iterations, salt_hex, digest = encoded.split("$")
        if algo != "pbkdf2_sha256" or int(iterations) != PBKDF2_ITERATIONS:
            return False
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), int(iterations)).hex()
        return hmac.compare_digest(actual, digest)
    except (ValueError, TypeError):
        return False


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


@dataclass
class User:
    id: str
    email: str
    password_hash: str
    role: str = "user"
    email_verified: bool = False
    failed_logins: int = 0
    locked_until: datetime | None = None
    created_at: datetime = field(default_factory=now)


@dataclass
class Session:
    id: str
    user_id: str
    refresh_hash: str
    created_at: datetime
    expires_at: datetime
    revoked_at: datetime | None = None
    ip: str | None = None
    user_agent: str | None = None


class SecurityStore:
    """Reference store. Replace this implementation with transactional DB/Redis storage."""
    def __init__(self) -> None:
        self.users: dict[str, User] = {}
        self.sessions: dict[str, Session] = {}
        self.refresh_index: dict[str, str] = {}
        self.one_time_tokens: dict[str, tuple[str, str, datetime]] = {}
        self.audit: list[dict] = []
        self.rate: dict[str, list[float]] = {}

    def audit_event(self, event: str, user_id: str | None, request: Request, **meta) -> None:
        self.audit.append({"event": event, "user_id": user_id, "ip": request.client.host if request.client else None,
                           "at": now().isoformat(), "metadata": meta})

    def rate_limit(self, key: str, limit: int, window: int) -> None:
        current = time.time(); hits = [x for x in self.rate.get(key, []) if current - x < window]
        if len(hits) >= limit:
            raise HTTPException(status_code=429, detail="Too many requests")
        hits.append(current); self.rate[key] = hits


store = SecurityStore()

PERMISSIONS = {
    "user": {"profile:read", "session:read", "session:revoke"},
    "manager": {"profile:read", "session:read", "session:revoke", "project:read", "project:write"},
    "admin": {"*"},
}


def issue_access_token(user: User, session_id: str) -> str:
    # Opaque signed token: payload is intentionally tiny; validate through HMAC.
    exp = int(time.time()) + ACCESS_TTL_SECONDS
    body = f"{user.id}.{session_id}.{exp}"
    sig = hmac.new(_signing_key(), body.encode(), hashlib.sha256).hexdigest()
    return f"{body}.{sig}"


def _signing_key() -> bytes:
    # Must be overridden by a secret manager in production.
    import os
    key = os.getenv("BCP_AUTH_SIGNING_KEY")
    if not key or len(key) < 32:
        raise RuntimeError("BCP_AUTH_SIGNING_KEY must be set to at least 32 characters")
    return key.encode()


def parse_access_token(token: str) -> tuple[User, Session]:
    try:
        uid, sid, exp_s, sig = token.split(".")
        body = f"{uid}.{sid}.{exp_s}"
        expected = hmac.new(_signing_key(), body.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected) or int(exp_s) < int(time.time()):
            raise ValueError
    except (ValueError, RuntimeError):
        raise HTTPException(status_code=401, detail="Invalid or expired access token")
    user = store.users.get(uid); session = store.sessions.get(sid)
    if not user or not session or session.revoked_at or session.expires_at <= now() or session.user_id != uid:
        raise HTTPException(status_code=401, detail="Session is invalid")
    return user, session

bearer = HTTPBearer(auto_error=False)


def current_identity(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> tuple[User, Session]:
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    return parse_access_token(credentials.credentials)


def require_permission(permission: str) -> Callable:
    def dependency(identity: tuple[User, Session] = Depends(current_identity)) -> tuple[User, Session]:
        user, session = identity
        perms = PERMISSIONS.get(user.role, set())
        if "*" not in perms and permission not in perms:
            raise HTTPException(status_code=403, detail="Insufficient permission")
        return user, session
    return dependency


def new_session(user: User, request: Request) -> tuple[Session, str, str]:
    raw = secrets.token_urlsafe(48)
    sid = secrets.token_urlsafe(18)
    session = Session(sid, user.id, token_hash(raw), now(), now() + timedelta(seconds=REFRESH_TTL_SECONDS),
                      ip=request.client.host if request.client else None,
                      user_agent=request.headers.get("user-agent"))
    store.sessions[sid] = session; store.refresh_index[session.refresh_hash] = sid
    return session, raw, issue_access_token(user, sid)


def rotate_refresh(raw: str, request: Request) -> tuple[User, Session, str, str]:
    sid = store.refresh_index.get(token_hash(raw)); old = store.sessions.get(sid) if sid else None
    if not old or old.revoked_at or old.expires_at <= now():
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user = store.users.get(old.user_id)
    if not user: raise HTTPException(status_code=401, detail="Invalid refresh token")
    old.revoked_at = now()
    return (lambda s: (user, s[0], s[1], s[2]))(new_session(user, request))
