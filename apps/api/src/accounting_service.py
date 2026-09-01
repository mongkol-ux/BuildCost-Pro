from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .core_models import Project, Transaction
from .accounting_models import FinancialPeriod, Payment, Retention, Reconciliation


ZERO = Decimal("0.00")


def _project(db: Session, project_id: str, user_id: str, role: str) -> Project:
    stmt = select(Project).where(Project.id == project_id)
    if role != "admin":
        stmt = stmt.where(Project.owner_user_id == user_id)
    value = db.scalar(stmt)
    if not value:
        raise HTTPException(status_code=404, detail="project not found")
    return value


def _period(db: Session, project_id: str, period_id: str) -> FinancialPeriod:
    value = db.scalar(select(FinancialPeriod).where(FinancialPeriod.id == period_id, FinancialPeriod.project_id == project_id))
    if not value:
        raise HTTPException(status_code=404, detail="financial period not found")
    return value


def create_period(db: Session, project_id: str, user_id: str, role: str, period_code: str, start_date: date, end_date: date) -> FinancialPeriod:
    _project(db, project_id, user_id, role)
    item = FinancialPeriod(project_id=project_id, period_code=period_code, start_date=start_date, end_date=end_date)
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="financial period code already exists")
    db.refresh(item)
    return item


def list_periods(db: Session, project_id: str, user_id: str, role: str) -> list[FinancialPeriod]:
    _project(db, project_id, user_id, role)
    return list(db.scalars(select(FinancialPeriod).where(FinancialPeriod.project_id == project_id).order_by(FinancialPeriod.start_date.desc())).all())


def close_period(db: Session, project_id: str, period_id: str, user_id: str, role: str) -> FinancialPeriod:
    _project(db, project_id, user_id, role)
    item = _period(db, project_id, period_id)
    if item.status == "CLOSED":
        return item
    item.status = "CLOSED"
    item.closed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(item)
    return item


def create_payment(db: Session, project_id: str, user_id: str, role: str, data: dict) -> Payment:
    _project(db, project_id, user_id, role)
    if data.get("transaction_id"):
        tx = db.scalar(select(Transaction).where(Transaction.id == data["transaction_id"], Transaction.project_id == project_id))
        if not tx:
            raise HTTPException(status_code=404, detail="transaction not found")
    item = Payment(project_id=project_id, **data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_payments(db: Session, project_id: str, user_id: str, role: str) -> list[Payment]:
    _project(db, project_id, user_id, role)
    return list(db.scalars(select(Payment).where(Payment.project_id == project_id).order_by(Payment.payment_date.desc(), Payment.created_at.desc())).all())


def create_retention(db: Session, project_id: str, user_id: str, role: str, data: dict) -> Retention:
    _project(db, project_id, user_id, role)
    if data.get("transaction_id"):
        tx = db.scalar(select(Transaction).where(Transaction.id == data["transaction_id"], Transaction.project_id == project_id))
        if not tx:
            raise HTTPException(status_code=404, detail="transaction not found")
        if tx.retention_amount < data["amount"]:
            raise HTTPException(status_code=422, detail="retention exceeds transaction retention amount")
    item = Retention(project_id=project_id, **data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_retentions(db: Session, project_id: str, user_id: str, role: str) -> list[Retention]:
    _project(db, project_id, user_id, role)
    return list(db.scalars(select(Retention).where(Retention.project_id == project_id).order_by(Retention.created_at.desc())).all())


def reconcile(db: Session, project_id: str, user_id: str, role: str, period_id: str, expected_total: Decimal) -> Reconciliation:
    _project(db, project_id, user_id, role)
    period = _period(db, project_id, period_id)
    actual = db.scalar(select(func.coalesce(func.sum(Transaction.amount), 0)).where(Transaction.project_id == project_id, Transaction.financial_period_id == period.id)) or ZERO
    actual = Decimal(str(actual)).quantize(Decimal("0.01"))
    expected_total = expected_total.quantize(Decimal("0.01"))
    difference = (actual - expected_total).quantize(Decimal("0.01"))
    item = Reconciliation(project_id=project_id, financial_period_id=period.id, expected_total=expected_total, actual_total=actual, difference=difference, status="MATCHED" if difference == ZERO else "MISMATCH")
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
