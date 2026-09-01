"""Read-only reporting aggregates for STEP 37."""
from decimal import Decimal
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from fastapi import HTTPException
from .core_models import Project, Budget, Cost, Transaction, BOQRevision, BOQItem
from .procurement_models import ProcurementRequest, PurchaseOrder
from .reporting_schemas import ReportingDashboard, ReportKPI, CategoryReportRow


def _project(db: Session, project_id: str, user_id: str, role: str) -> Project:
    stmt = select(Project).where(Project.id == project_id)
    if role != "admin":
        stmt = stmt.where(Project.owner_user_id == user_id)
    project = db.scalar(stmt)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    return project


def _sum(db: Session, column, *conditions) -> Decimal:
    value = db.scalar(select(func.coalesce(func.sum(column), 0)).where(*conditions))
    return value or Decimal("0")


def dashboard(db: Session, project_id: str, user_id: str, role: str) -> ReportingDashboard:
    _project(db, project_id, user_id, role)
    budget = _sum(db, Budget.amount, Budget.project_id == project_id)
    actual = _sum(db, Cost.total, Cost.project_id == project_id)
    commitment = _sum(
        db, PurchaseOrder.total,
        PurchaseOrder.status.in_(["DRAFT", "ORDERED", "PARTIALLY_RECEIVED"]),
        PurchaseOrder.request_id.in_(select(ProcurementRequest.id).where(ProcurementRequest.project_id == project_id)),
    )
    income = _sum(db, Transaction.amount, Transaction.project_id == project_id, Transaction.type == "INCOME")
    expense = _sum(db, Transaction.amount, Transaction.project_id == project_id, Transaction.type == "EXPENSE")
    variance = budget - actual
    variance_percent = (variance / budget * Decimal("100")).quantize(Decimal("0.01")) if budget else None

    rows = db.execute(
        select(Cost.category, func.coalesce(func.sum(Cost.total), 0))
        .where(Cost.project_id == project_id)
        .group_by(Cost.category)
        .order_by(Cost.category)
    ).all()
    categories = [CategoryReportRow(category=str(category), amount=amount or Decimal("0")) for category, amount in rows]

    boq_revisions = select(BOQRevision.id).where(BOQRevision.project_id == project_id)
    boq_total = _sum(db, BOQItem.total, BOQItem.revision_id.in_(boq_revisions))
    boq_items = db.scalar(select(func.count(BOQItem.id)).where(BOQItem.revision_id.in_(boq_revisions))) or 0

    kpi = ReportKPI(
        budget=budget,
        actual=actual,
        commitment=commitment,
        variance=variance,
        variance_percent=variance_percent,
        income=income,
        expense=expense,
        balance=income - expense,
    )
    return ReportingDashboard(
        project_id=project_id,
        kpi=kpi,
        cost_by_category=categories,
        boq_total=boq_total,
        boq_items=int(boq_items),
        procurement_commitment=commitment,
        accounting_expense=expense,
        accounting_income=income,
    )
