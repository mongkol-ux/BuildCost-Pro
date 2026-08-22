"""Application service for projects and financial aggregates."""
from decimal import Decimal
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .core_models import Budget, Cost, Project, Transaction


def _project_or_404(db: Session, project_id: str, user_id: str, role: str) -> Project:
    stmt = select(Project).where(Project.id == project_id)
    if role != "admin":
        stmt = stmt.where(Project.owner_user_id == user_id)
    project = db.scalar(stmt)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    return project


def create_project(db: Session, user_id: str, code: str, name: str, description: str | None) -> Project:
    project = Project(owner_user_id=user_id, code=code, name=name, description=description)
    db.add(project)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="project code already exists")
    db.refresh(project)
    return project


def list_projects(db: Session, user_id: str, role: str) -> list[Project]:
    stmt = select(Project).order_by(Project.created_at.desc())
    if role != "admin":
        stmt = stmt.where(Project.owner_user_id == user_id)
    return list(db.scalars(stmt).all())


def get_project(db: Session, project_id: str, user_id: str, role: str) -> Project:
    return _project_or_404(db, project_id, user_id, role)


def update_project(db: Session, project_id: str, user_id: str, role: str, data: dict) -> Project:
    project = _project_or_404(db, project_id, user_id, role)
    for key, value in data.items():
        if value is not None:
            setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project


def create_budget(db: Session, project_id: str, user_id: str, role: str, name: str, amount: Decimal) -> Budget:
    _project_or_404(db, project_id, user_id, role)
    budget = Budget(project_id=project_id, name=name, amount=amount)
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


def list_budgets(db: Session, project_id: str, user_id: str, role: str) -> list[Budget]:
    _project_or_404(db, project_id, user_id, role)
    return list(db.scalars(select(Budget).where(Budget.project_id == project_id).order_by(Budget.created_at.desc())).all())


def create_cost(db: Session, project_id: str, user_id: str, role: str, data: dict) -> Cost:
    _project_or_404(db, project_id, user_id, role)
    total = (data["quantity"] * data["unit_cost"]).quantize(Decimal("0.01"))
    cost = Cost(project_id=project_id, total=total, **data)
    db.add(cost)
    db.commit()
    db.refresh(cost)
    return cost


def list_costs(db: Session, project_id: str, user_id: str, role: str) -> list[Cost]:
    _project_or_404(db, project_id, user_id, role)
    return list(db.scalars(select(Cost).where(Cost.project_id == project_id).order_by(Cost.occurred_at.desc())).all())


def create_transaction(db: Session, project_id: str, user_id: str, role: str, data: dict) -> Transaction:
    _project_or_404(db, project_id, user_id, role)
    item = Transaction(project_id=project_id, **data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_transactions(db: Session, project_id: str, user_id: str, role: str) -> list[Transaction]:
    _project_or_404(db, project_id, user_id, role)
    return list(db.scalars(select(Transaction).where(Transaction.project_id == project_id).order_by(Transaction.occurred_at.desc())).all())


def project_summary(db: Session, project_id: str, user_id: str, role: str) -> dict:
    _project_or_404(db, project_id, user_id, role)
    budget_total = db.scalar(select(func.coalesce(func.sum(Budget.amount), 0)).where(Budget.project_id == project_id)) or Decimal("0")
    cost_total = db.scalar(select(func.coalesce(func.sum(Cost.total), 0)).where(Cost.project_id == project_id)) or Decimal("0")
    def tx_total(tx_type: str) -> Decimal:
        return db.scalar(select(func.coalesce(func.sum(Transaction.amount), 0)).where(Transaction.project_id == project_id, Transaction.type == tx_type)) or Decimal("0")
    income = tx_total("INCOME")
    expense = tx_total("EXPENSE")
    adjustment = tx_total("ADJUSTMENT")
    return {
        "project_id": project_id,
        "budget_total": budget_total,
        "cost_total": cost_total,
        "income_total": income,
        "expense_total": expense,
        "adjustment_total": adjustment,
        "balance": income - expense + adjustment,
        "budget_remaining": budget_total - cost_total,
    }
