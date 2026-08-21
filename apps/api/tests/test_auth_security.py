import os
os.environ["BCP_AUTH_SIGNING_KEY"] = "test-signing-key-at-least-32-characters-long"
from fastapi.testclient import TestClient
from src.main import app
from src.security import store

client = TestClient(app)


def setup_function():
    store.users.clear(); store.sessions.clear(); store.refresh_index.clear(); store.one_time_tokens.clear(); store.audit.clear(); store.rate.clear()


def register(email="user@example.com"):
    r = client.post("/auth/register", json={"email":email,"password":"StrongPassword!123"})
    assert r.status_code == 201
    return r.json()


def login(email="user@example.com", password="StrongPassword!123"):
    return client.post("/auth/login", json={"email":email,"password":password})


def test_register_hashes_password_and_issues_verification_token():
    data = register(); user = next(iter(store.users.values()))
    assert data["verification_token"] and user.password_hash.startswith("pbkdf2_sha256$")
    assert user.password_hash != "StrongPassword!123"


def test_login_returns_access_and_refresh_tokens():
    register(); r = login(); assert r.status_code == 200
    body = r.json(); assert body["access_token"] and body["refresh_token"] and body["session_id"]


def test_refresh_rotates_and_invalidates_old_token():
    register(); first = login().json(); second = client.post("/auth/refresh", json={"refresh_token":first["refresh_token"]})
    assert second.status_code == 200
    assert client.post("/auth/refresh", json={"refresh_token":first["refresh_token"]}).status_code == 401


def test_logout_revokes_current_session():
    register(); auth = login().json(); h={"Authorization":f"Bearer {auth['access_token']}"}
    assert client.post("/auth/logout", headers=h).status_code == 200
    assert client.get("/auth/me", headers=h).status_code == 401


def test_password_reset_revokes_sessions():
    register(); auth = login().json(); token = client.post("/auth/password-reset/request", json={"email":"user@example.com"}).json()["reset_token"]
    assert client.post("/auth/password-reset/confirm", json={"token":token,"password":"NewStrongPassword!456"}).status_code == 200
    assert client.get("/auth/me", headers={"Authorization":f"Bearer {auth['access_token']}"}).status_code == 401
    assert login(password="NewStrongPassword!456").status_code == 200


def test_email_verification_is_one_time():
    register(); auth=login().json(); h={"Authorization":f"Bearer {auth['access_token']}"}
    token=client.post("/auth/verify-email/request",headers=h).json()["verification_token"]
    assert client.post("/auth/verify-email/confirm",json={"token":token}).status_code==200
    assert client.post("/auth/verify-email/confirm",json={"token":token}).status_code==400


def test_lockout_after_five_failures():
    register()
    for _ in range(5): assert login(password="wrong").status_code == 401
    assert login().status_code == 423


def test_sessions_can_be_listed_and_revoked():
    register(); auth=login().json(); h={"Authorization":f"Bearer {auth['access_token']}"}
    sessions=client.get("/auth/sessions",headers=h).json(); assert len(sessions)==1
    sid=sessions[0]["id"]; assert client.delete(f"/auth/sessions/{sid}",headers=h).status_code==200


def test_security_headers_present():
    r=client.get("/health"); assert r.headers["x-content-type-options"]=="nosniff"; assert r.headers["x-frame-options"]=="DENY"; assert "frame-ancestors" in r.headers["content-security-policy"]


def test_invalid_access_token_is_rejected():
    assert client.get("/auth/me",headers={"Authorization":"Bearer invalid"}).status_code==401


def test_unknown_password_reset_does_not_disclose_account():
    r=client.post("/auth/password-reset/request",json={"email":"missing@example.com"}); assert r.status_code==200 and r.json()=={"status":"accepted"}


def test_user_cannot_read_admin_audit_log():
    register(); auth=login().json(); h={"Authorization":f"Bearer {auth['access_token']}"}
    assert client.get("/admin/audit-log",headers=h).status_code==403


def test_admin_permission_allows_audit_log():
    data=register(); user=store.users[data["user_id"]]; user.role="admin"; auth=login().json(); h={"Authorization":f"Bearer {auth['access_token']}"}
    assert client.get("/admin/audit-log",headers=h).status_code==200
