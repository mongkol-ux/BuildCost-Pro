import pytest
import jwt
from src.auth_security import create_access_token, decode_access_token, hash_password, token_hash, verify_password


def test_password_hash_round_trip():
    hashed = hash_password("StrongPassword123!")
    assert hashed != "StrongPassword123!"
    assert verify_password("StrongPassword123!", hashed)
    assert not verify_password("WrongPassword123!", hashed)


def test_token_hash_is_deterministic_and_not_plaintext():
    raw = "refresh-token-value"
    assert token_hash(raw) == token_hash(raw)
    assert token_hash(raw) != raw


def test_access_token_contains_session_and_user_claims():
    token = create_access_token("user-1", "session-1", "user")
    payload = decode_access_token(token)
    assert payload["sub"] == "user-1"
    assert payload["sid"] == "session-1"
    assert payload["type"] == "access"


def test_wrong_secret_rejected(monkeypatch):
    token = create_access_token("user-1", "session-1", "user")
    monkeypatch.setenv("BUILD_COST_JWT_SECRET", "another-secret-that-is-long-enough-123456")
    from src.config import get_settings
    get_settings.cache_clear()
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token)
