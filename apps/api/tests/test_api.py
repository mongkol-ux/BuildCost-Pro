def register_and_login(client, email="user@example.com", password="StrongPassword123!"):
    r = client.post("/api/v1/auth/register", json={"email": email, "full_name": "Test User", "password": password})
    assert r.status_code == 201
    r = client.post("/api/v1/auth/login", data={"username": email, "password": password})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_registration_login_and_me(client):
    token = register_and_login(client)
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"


def test_validation_error_shape(client):
    response = client.post("/api/v1/auth/register", json={"email": "bad", "full_name": "x", "password": "short"})
    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "VALIDATION_ERROR"
    assert "details" in body


def test_protected_project_requires_authentication(client):
    response = client.get("/api/v1/projects")
    assert response.status_code == 401


def test_invalid_token_is_rejected(client):
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_TOKEN"
