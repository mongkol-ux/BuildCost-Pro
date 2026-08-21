from apps.api.src.auth import hash_password
from apps.api.src.models import User, UserRole


def test_manager_can_create_project(client, db):
    user = User(email="manager@example.com", full_name="Manager", password_hash=hash_password("StrongPassword123!"), role=UserRole.MANAGER)
    db.add(user); db.commit(); db.refresh(user)
    token_response = client.post("/api/v1/auth/login", data={"username": user.email, "password": "StrongPassword123!"})
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]
    response = client.post("/api/v1/projects", headers={"Authorization": f"Bearer {token}"}, json={"name": "Demo Project", "code": "DEMO-001", "description": "Integration test"})
    assert response.status_code == 201
    assert response.json()["code"] == "DEMO-001"


def test_duplicate_project_code_returns_conflict(client, db):
    user = User(email="manager2@example.com", full_name="Manager", password_hash=hash_password("StrongPassword123!"), role=UserRole.MANAGER)
    db.add(user); db.commit(); db.refresh(user)
    token = client.post("/api/v1/auth/login", data={"username": user.email, "password": "StrongPassword123!"}).json()["access_token"]
    payload = {"name": "Demo", "code": "DUP-001"}
    assert client.post("/api/v1/projects", headers={"Authorization": f"Bearer {token}"}, json=payload).status_code == 201
    response = client.post("/api/v1/projects", headers={"Authorization": f"Bearer {token}"}, json=payload)
    assert response.status_code == 409
