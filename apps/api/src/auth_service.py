"""Authentication service with refresh-token rotation and lockout."""
from datetime import datetime, timedelta, timezone
import json
from sqlalchemy import select
from sqlalchemy.orm import Session
from .auth_models import AuditLog, AuthSession, OneTimeToken, User
from .auth_security import create_access_token, hash_password, random_token, token_hash, verify_password
from .config import get_settings


def _now() -> datetime:
    return datetime.now(timezone.utc)


def audit(db: Session, event: str, user_id: str | None, ip: str | None, ua: str | None, **meta) -> None:
    db.add(AuditLog(user_id=user_id, event=event, ip_address=ip, user_agent=ua, metadata_json=json.dumps(meta, separators=(",", ":"))))


def register(db: Session, email: str, password: str, ip: str | None, ua: str | None) -> User:
    normalized = email.strip().lower()
    if db.scalar(select(User).where(User.email == normalized)):
        raise ValueError("email already registered")
    user = User(email=normalized, password_hash=hash_password(password))
    db.add(user)
    db.flush()
    raw = random_token()
    settings = get_settings()
    db.add(OneTimeToken(user_id=user.id, purpose="email_verification", token_hash=token_hash(raw), expires_at=_now() + timedelta(minutes=settings.verification_token_minutes)))
    audit(db, "auth.registered", user.id, ip, ua)
    db.commit()
    return user


def _new_session(db: Session, user: User, ip: str | None, ua: str | None) -> tuple[str, str]:
    settings = get_settings()
    raw = random_token()
    session = AuthSession(user_id=user.id, refresh_token_hash=token_hash(raw), user_agent=ua, ip_address=ip, expires_at=_now() + timedelta(days=settings.refresh_token_days))
    db.add(session)
    db.flush()
    access = create_access_token(user.id, session.id, user.role)
    return access, raw


def login(db: Session, email: str, password: str, ip: str | None, ua: str | None) -> tuple[str, str, int]:
    settings = get_settings()
    user = db.scalar(select(User).where(User.email == email.strip().lower()))
    if not user:
        audit(db, "auth.login_failed", None, ip, ua, reason="invalid_credentials")
        db.commit()
        raise ValueError("invalid credentials")
    if user.locked_until and user.locked_until > _now():
        audit(db, "auth.login_blocked", user.id, ip, ua)
        db.commit()
        raise PermissionError("account temporarily locked")
    if not verify_password(password, user.password_hash):
        user.failed_login_count += 1
        if user.failed_login_count >= settings.login_max_attempts:
            user.locked_until = _now() + timedelta(minutes=settings.login_lock_minutes)
            user.failed_login_count = 0
        audit(db, "auth.login_failed", user.id, ip, ua, reason="invalid_credentials")
        db.commit()
        raise ValueError("invalid credentials")
    if not user.email_verified_at:
        audit(db, "auth.login_blocked", user.id, ip, ua, reason="email_not_verified")
        db.commit()
        raise PermissionError("email verification required")
    user.failed_login_count = 0
    user.locked_until = None
    access, refresh = _new_session(db, user, ip, ua)
    audit(db, "auth.login_succeeded", user.id, ip, ua)
    db.commit()
    return access, refresh, settings.access_token_minutes * 60


def rotate_refresh(db: Session, refresh: str, ip: str | None, ua: str | None) -> tuple[str, str, int]:
    settings = get_settings()
    session = db.scalar(select(AuthSession).where(AuthSession.refresh_token_hash == token_hash(refresh)).with_for_update())
    if not session or session.revoked_at or session.expires_at <= _now():
        raise PermissionError("invalid refresh token")
    user = db.get(User, session.user_id)
    if not user or not user.is_active:
        raise PermissionError("invalid session")
    session.revoked_at = _now()
    access, replacement = _new_session(db, user, ip, ua)
    audit(db, "auth.refresh_rotated", user.id, ip, ua, replaced_session=session.id)
    db.commit()
    return access, replacement, settings.access_token_minutes * 60


def revoke_session(db: Session, session_id: str, user_id: str) -> None:
    session = db.scalar(select(AuthSession).where(AuthSession.id == session_id, AuthSession.user_id == user_id))
    if session and not session.revoked_at:
        session.revoked_at = _now()
        audit(db, "auth.session_revoked", user_id, None, None, session_id=session_id)
        db.commit()


def revoke_all_sessions(db: Session, user_id: str) -> None:
    sessions = db.scalars(select(AuthSession).where(AuthSession.user_id == user_id, AuthSession.revoked_at.is_(None))).all()
    now = _now()
    for session in sessions:
        session.revoked_at = now
    audit(db, "auth.sessions_revoked_all", user_id, None, None, count=len(sessions))
    db.commit()


def consume_one_time_token(db: Session, raw: str, purpose: str) -> User:
    item = db.scalar(select(OneTimeToken).where(OneTimeToken.token_hash == token_hash(raw), OneTimeToken.purpose == purpose).with_for_update())
    if not item or item.consumed_at or item.expires_at <= _now():
        raise ValueError("invalid or expired token")
    item.consumed_at = _now()
    user = db.get(User, item.user_id)
    if not user:
        raise ValueError("invalid token")
    return user


def verify_email(db: Session, raw: str) -> None:
    user = consume_one_time_token(db, raw, "email_verification")
    user.email_verified_at = _now()
    audit(db, "auth.email_verified", user.id, None, None)
    db.commit()


def request_password_reset(db: Session, email: str) -> str | None:
    user = db.scalar(select(User).where(User.email == email.strip().lower()))
    if not user:
        return None
    raw = random_token()
    settings = get_settings()
    db.add(OneTimeToken(user_id=user.id, purpose="password_reset", token_hash=token_hash(raw), expires_at=_now() + timedelta(minutes=settings.reset_token_minutes)))
    audit(db, "auth.password_reset_requested", user.id, None, None)
    db.commit()
    return raw


def reset_password(db: Session, raw: str, new_password: str) -> None:
    user = consume_one_time_token(db, raw, "password_reset")
    user.password_hash = hash_password(new_password)
    user.failed_login_count = 0
    user.locked_until = None
    revoke_all_sessions(db, user.id)
    audit(db, "auth.password_reset_completed", user.id, None, None)
    db.commit()
