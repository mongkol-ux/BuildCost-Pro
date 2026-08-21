import os

os.environ.setdefault("BUILD_COST_JWT_SECRET", "integration-test-secret-0123456789-abcdefgh")
os.environ.setdefault("BUILD_COST_ALLOWED_HOSTS", "testserver,localhost")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.auth_models import Base, AuditLog, OneTimeToken, AuthSession, User
from src.auth_router import app if False else router
from src import auth_router
from src.main import app


TEST_DB = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=TEST_DB, expire_on_commit=False)
Base.metadata.create_all(TEST_DB)
auth_router.SessionLocal = TestingSessionLocal
client = TestClient(app)


def db():
    return TestingSessionLocal()


def token_for(user_id: str, purpose: str) -> str:
    with db() as session:
        row = session.scalar(
            select(OneTimeToken).where(
                OneTimeToken.user_id == user_id,
                OneTimeToken.purpose == purpose,
                OneTimeToken.consumed_at.is_(None),
            ).order_by(OneTimeToken.created_at.desc())
        )
        assert row is not None
        from src.auth_security import token_hash
        # Raw one-time tokens are deliberately never stored. For integration testing,
        # use the service return value for password reset and the generated verification
        # token is retrieved by reproducing the deterministic test fixture below.
        return row.token_hash


def test_authentication_security_gate_end_to_end():
    email = "integration@example.com"
    password = "StrongPassword123!"
    new_password = "NewStrongPassword456!"

    registered = client.post("/auth/register", json={"email": email, "password": password})
    assert registered.status_code == 201
    user_id = registered.json()["id"]

    # Verify-email is intentionally one-time-token based. Exercise the service boundary
    # directly to obtain the raw token without exposing it through a production API.
    from src.auth_service import register as service_register, verify_email, request_password_reset
    from src.auth_security import random_token, token_hash
    from datetime import datetime, timedelta, timezone

    with db() as session:
        user = session.get(User, user_id)
        verification_raw = random_token()
        item = session.scalar(
            select(OneTimeToken).where(
                OneTimeToken.user_id == user_id,
                OneTimeToken.purpose == "email_verification",
            ).order_by(OneTimeToken.created_at.desc())
        )
        assert item is not None
        item.token_hash = token_hash(verification_raw)
        session.commit()

    verified = client.post("/auth/verify-email", json={"token": verification_raw})
    assert verified.status_code == 200
    assert verified.json() == {"verified": True}
    assert client.post("/auth/verify-email", json={"token": verification_raw}).status_code == 400

    login = client.post("/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200
    first_tokens = login.json()
    first_access = first_tokens["access_token"]
    first_refresh = first_tokens["refresh_token"]

    rotated = client.post("/auth/refresh", json={"refresh_token": first_refresh})
    assert rotated.status_code == 200
    second_tokens = rotated.json()
    assert second_tokens["refresh_token"] != first_refresh
    assert client.post("/auth/refresh", json={"refresh_token": first_refresh}).status_code == 401

    sessions = client.get("/auth/sessions", headers={"Authorization": f"Bearer {second_tokens['access_token']}"})
    assert sessions.status_code == 200
    assert sessions.json()
    session_id = sessions.json()[0]["id"]

    revoked = client.delete(
        f"/auth/sessions/{session_id}",
        headers={"Authorization": f"Bearer {second_tokens['access_token']}"},
    )
    assert revoked.status_code == 204
    assert client.get(
        "/auth/sessions",
        headers={"Authorization": f"Bearer {second_tokens['access_token']}"},
    ).status_code == 401

    # Create a fresh session for password-reset invalidation testing.
    login_again = client.post("/auth/login", json={"email": email, "password": password})
    assert login_again.status_code == 200
    reset_request = client.post("/auth/password-reset/request", json={"email": email})
    assert reset_request.status_code == 200

    with db() as session:
        item = session.scalar(
            select(OneTimeToken).where(
                OneTimeToken.user_id == user_id,
                OneTimeToken.purpose == "password_reset",
                OneTimeToken.consumed_at.is_(None),
            ).order_by(OneTimeToken.created_at.desc())
        )
        assert item is not None
        reset_raw = random_token()
        item.token_hash = token_hash(reset_raw)
        session.commit()

    reset = client.post(
        "/auth/password-reset/confirm",
        json={"token": reset_raw, "new_password": new_password},
    )
    assert reset.status_code == 200
    assert client.post(
        "/auth/password-reset/confirm",
        json={"token": reset_raw, "new_password": password},
    ).status_code == 400

    assert client.post("/auth/login", json={"email": email, "password": password}).status_code == 401
    fresh_login = client.post("/auth/login", json={"email": email, "password": new_password})
    assert fresh_login.status_code == 200

    # Lockout: five failed attempts, then the account is blocked.
    locked_email = "lockout@example.com"
    locked = client.post("/auth/register", json={"email": locked_email, "password": password})
    assert locked.status_code == 201
    locked_id = locked.json()["id"]
    with db() as session:
        verification = session.scalar(
            select(OneTimeToken).where(
                OneTimeToken.user_id == locked_id,
                OneTimeToken.purpose == "email_verification",
            ).order_by(OneTimeToken.created_at.desc())
        )
        raw = random_token()
        verification.token_hash = token_hash(raw)
        session.commit()
    assert client.post("/auth/verify-email", json={"token": raw}).status_code == 200

    for _ in range(5):
        assert client.post("/auth/login", json={"email": locked_email, "password": "WrongPassword123!"}).status_code == 401
    assert client.post("/auth/login", json={"email": locked_email, "password": password}).status_code == 423

    with db() as session:
        events = session.scalars(select(AuditLog.event)).all()
        assert "auth.registered" in events
        assert "auth.email_verified" in events
        assert "auth.login_succeeded" in events
        assert "auth.refresh_rotated" in events
        assert "auth.session_revoked" in events
        assert "auth.password_reset_requested" in events
        assert "auth.password_reset_completed" in events
        assert "auth.login_blocked" in events
