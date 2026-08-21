import os

os.environ.setdefault("BUILD_COST_JWT_SECRET", "integration-test-secret-0123456789-abcdefgh")
os.environ.setdefault("BUILD_COST_ALLOWED_HOSTS", "testserver,localhost")

from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from src import auth_router
from src.auth_models import AuditLog, AuthSession, OneTimeToken, User
from src.auth_security import random_token, token_hash
from src.main import app

client = TestClient(app)


def db():
    return auth_router.SessionLocal()


def replace_latest_one_time_token(user_id: str, purpose: str) -> str:
    with db() as session:
        item = session.scalar(
            select(OneTimeToken).where(
                OneTimeToken.user_id == user_id,
                OneTimeToken.purpose == purpose,
                OneTimeToken.consumed_at.is_(None),
            ).order_by(OneTimeToken.created_at.desc())
        )
        assert item is not None
        raw = random_token()
        item.token_hash = token_hash(raw)
        session.commit()
        return raw


def test_authentication_security_gate_end_to_end():
    # The CI job runs against PostgreSQL and applies the same migration used by deployment.
    with db() as session:
        session.execute(delete(AuditLog))
        session.execute(delete(AuthSession))
        session.execute(delete(OneTimeToken))
        session.execute(delete(User))
        session.commit()

    email = "integration@example.com"
    password = "StrongPassword123!"
    new_password = "NewStrongPassword456!"

    registered = client.post("/auth/register", json={"email": email, "password": password})
    assert registered.status_code == 201
    user_id = registered.json()["id"]

    verification_raw = replace_latest_one_time_token(user_id, "email_verification")
    assert client.post("/auth/verify-email", json={"token": verification_raw}).status_code == 200
    assert client.post("/auth/verify-email", json={"token": verification_raw}).status_code == 400

    login = client.post("/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200
    first_tokens = login.json()
    first_refresh = first_tokens["refresh_token"]

    rotated = client.post("/auth/refresh", json={"refresh_token": first_refresh})
    assert rotated.status_code == 200
    second_tokens = rotated.json()
    assert second_tokens["refresh_token"] != first_refresh
    assert client.post("/auth/refresh", json={"refresh_token": first_refresh}).status_code == 401

    auth = {"Authorization": f"Bearer {second_tokens['access_token']}"}
    sessions = client.get("/auth/sessions", headers=auth)
    assert sessions.status_code == 200
    assert sessions.json()
    session_id = sessions.json()[0]["id"]

    assert client.delete(f"/auth/sessions/{session_id}", headers=auth).status_code == 204
    assert client.get("/auth/sessions", headers=auth).status_code == 401

    # Password reset invalidates all existing sessions.
    login_again = client.post("/auth/login", json={"email": email, "password": password})
    assert login_again.status_code == 200
    reset_request = client.post("/auth/password-reset/request", json={"email": email})
    assert reset_request.status_code == 200
    reset_raw = replace_latest_one_time_token(user_id, "password_reset")

    assert client.post(
        "/auth/password-reset/confirm",
        json={"token": reset_raw, "new_password": new_password},
    ).status_code == 200
    assert client.post(
        "/auth/password-reset/confirm",
        json={"token": reset_raw, "new_password": password},
    ).status_code == 400

    assert client.post("/auth/login", json={"email": email, "password": password}).status_code == 401
    assert client.post("/auth/login", json={"email": email, "password": new_password}).status_code == 200

    # Lockout: five failed attempts, then a valid login is blocked.
    locked_email = "lockout@example.com"
    locked = client.post("/auth/register", json={"email": locked_email, "password": password})
    assert locked.status_code == 201
    locked_id = locked.json()["id"]
    locked_verification = replace_latest_one_time_token(locked_id, "email_verification")
    assert client.post("/auth/verify-email", json={"token": locked_verification}).status_code == 200

    for _ in range(5):
        assert client.post(
            "/auth/login",
            json={"email": locked_email, "password": "WrongPassword123!"},
        ).status_code == 401
    assert client.post("/auth/login", json={"email": locked_email, "password": password}).status_code == 423

    with db() as session:
        events = set(session.scalars(select(AuditLog.event)).all())
        expected = {
            "auth.registered",
            "auth.email_verified",
            "auth.login_succeeded",
            "auth.refresh_rotated",
            "auth.session_revoked",
            "auth.password_reset_requested",
            "auth.password_reset_completed",
            "auth.login_blocked",
        }
        assert expected.issubset(events)
