"""Password, token and JWT primitives. Tokens are never stored in plaintext."""
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import secrets
import jwt
from pwdlib import PasswordHash
from .config import get_settings

_passwords = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return _passwords.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _passwords.verify(password, password_hash)


def random_token() -> str:
    return secrets.token_urlsafe(48)


def token_hash(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


def create_access_token(user_id: str, session_id: str, role: str) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "sid": session_id,
        "role": role,
        "iss": settings.jwt_issuer,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_minutes),
        "type": "access",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_access_token(token: str) -> dict:
    settings = get_settings()
    payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"], issuer=settings.jwt_issuer)
    if payload.get("type") != "access" or not payload.get("sid"):
        raise jwt.InvalidTokenError("invalid access token")
    return payload
