from apps.api.src.auth import hash_password
from apps.api.src.models import User, UserRole


def test_cost_budget_transaction_flow(client, db):
    user = User(email="owner@example.com", full_name="Owner", password_hash=hash_password("StrongPassword123!"), role=UserRole.MANAGER)
    db.add(user); db.commit(); db.refresh(user)
    token = client.post("/api/v1/auth/login", data={"username": user.email, "password": "StrongPassword123!"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    project = client.post("/api/v1/projects", headers=headers, json={"name": "Flow Project", "code": "FLOW-001"}).json()
    project_id = project["id"]

    cost = client.post("/api/v1/costs", headers=headers, json={"project_id": project_id, "category": "Materials", "description": "Concrete", "amount": "12500.00"})
    budget = client.post("/api/v1/budgets", headers=headers, json={"project_id": project_id, "name": "Main Budget", "description": "Budget", "amount": "50000.00"})
    transaction = client.post("/api/v1/transactions", headers=headers, json={"project_id": project_id, "reference": "TX-001", "description": "Supplier payment", "amount": "12500.00"})

    assert cost.status_code == 201
    assert budget.status_code == 201
    assert transaction.status_code == 201
    assert len(client.get(f"/api/v1/costs?project_id={project_id}", headers=headers).json()) == 1
