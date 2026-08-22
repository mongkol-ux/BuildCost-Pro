from decimal import Decimal
from uuid import uuid4

from src.auth_models import User
from src.auth_router import SessionLocal
from src.core_service import create_budget, create_cost, create_project, create_transaction, project_summary


def test_core_business_persistence_and_summary():
    db = SessionLocal()
    user = User(email=f"core-test-{uuid4()}@example.invalid", password_hash="test", role="user")
    db.add(user)
    db.commit()
    db.refresh(user)
    project = None
    try:
        project = create_project(db, user.id, f"TEST-{uuid4().hex[:10]}", "Integration Project", None)
        create_budget(db, project.id, user.id, user.role, "Main Budget", Decimal("10000.00"))
        create_cost(db, project.id, user.id, user.role, {"category": "materials", "quantity": Decimal("2.0000"), "unit_cost": Decimal("125.00")})
        create_transaction(db, project.id, user.id, user.role, {"type": "INCOME", "amount": Decimal("1000.00")})
        create_transaction(db, project.id, user.id, user.role, {"type": "EXPENSE", "amount": Decimal("150.00")})
        summary = project_summary(db, project.id, user.id, user.role)
        assert summary["budget_total"] == Decimal("10000.00")
        assert summary["cost_total"] == Decimal("250.00")
        assert summary["balance"] == Decimal("850.00")
        assert summary["budget_remaining"] == Decimal("9750.00")
    finally:
        if project is not None:
            db.delete(project)
            db.commit()
        db.delete(user)
        db.commit()
        db.close()
