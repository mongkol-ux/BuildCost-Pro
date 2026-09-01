from decimal import Decimal
from uuid import uuid4

from src.auth_models import User
from src.auth_router import SessionLocal
from src.core_service import create_budget, create_cost, create_project, create_transaction, project_summary
from src.integration_service import build_project_integration_summary


def test_step42_financial_reconciliation_and_integration_invariants():
    db = SessionLocal()
    user = User(email=f"step42-{uuid4()}@example.invalid", password_hash="test", role="user")
    db.add(user)
    db.commit()
    db.refresh(user)
    project = None
    try:
        project = create_project(db, user.id, f"QA-{uuid4().hex[:10]}", "STEP 42 UAT", None)
        create_budget(db, project.id, user.id, user.role, "QA Budget", Decimal("20000.00"))
        create_cost(
            db,
            project.id,
            user.id,
            user.role,
            {"category": "materials", "quantity": Decimal("4"), "unit_cost": Decimal("250")},
        )
        create_transaction(db, project.id, user.id, user.role, {"type": "INCOME", "amount": Decimal("5000")})
        create_transaction(db, project.id, user.id, user.role, {"type": "EXPENSE", "amount": Decimal("1000")})

        summary = project_summary(db, project.id, user.id, user.role)
        integration = build_project_integration_summary(db, project.id)

        assert summary["budget_total"] == Decimal("20000")
        assert summary["cost_total"] == Decimal("1000")
        assert summary["balance"] == Decimal("4000")
        assert summary["budget_remaining"] == Decimal("19000")
        assert integration["project_id"] == project.id
        assert integration["budget_total"] == Decimal("20000")
        assert integration["cost_total"] == Decimal("1000")
        assert integration["accounting_expense_total"] == Decimal("1000")
    finally:
        if project is not None:
            db.delete(project)
            db.commit()
        db.delete(user)
        db.commit()
        db.close()


def test_step42_authentication_boundary_is_enforced():
    db = SessionLocal()
    user = User(email=f"step42-auth-{uuid4()}@example.invalid", password_hash="test", role="user")
    db.add(user)
    db.commit()
    db.refresh(user)
    project = None
    other_user = User(email=f"step42-other-{uuid4()}@example.invalid", password_hash="test", role="user")
    db.add(other_user)
    db.commit()
    db.refresh(other_user)
    try:
        project = create_project(db, user.id, f"AUTH-{uuid4().hex[:10]}", "Permission Boundary", None)
        from src.core_service import get_project

        assert get_project(db, project.id, user.id, user.role).id == project.id
        try:
            get_project(db, project.id, other_user.id, other_user.role)
        except Exception:
            pass
        else:
            raise AssertionError("cross-user project access was not rejected")
    finally:
        if project is not None:
            db.delete(project)
            db.commit()
        db.delete(other_user)
        db.delete(user)
        db.commit()
        db.close()
