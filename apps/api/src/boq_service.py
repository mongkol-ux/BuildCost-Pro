"""BOQ and estimating services for STEP 32."""
from decimal import Decimal, ROUND_HALF_UP
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .core_models import BOQItem, BOQRevision, Budget
from .core_service import _project_or_404

CENT = Decimal("0.01")


def calculate_item_total(quantity: Decimal, unit_rate: Decimal) -> Decimal:
    return (quantity * unit_rate).quantize(CENT, rounding=ROUND_HALF_UP)


def create_revision(db: Session, project_id: str, user_id: str, role: str, name: str, budget_id: str | None):
    _project_or_404(db, project_id, user_id, role)
    if budget_id:
        budget = db.scalar(select(Budget).where(Budget.id == budget_id, Budget.project_id == project_id))
        if not budget:
            raise HTTPException(status_code=404, detail="budget not found")
    latest = db.scalar(select(func.max(BOQRevision.revision_no)).where(BOQRevision.project_id == project_id)) or 0
    revision = BOQRevision(project_id=project_id, budget_id=budget_id, revision_no=latest + 1, name=name)
    db.add(revision)
    db.commit()
    db.refresh(revision)
    return revision


def list_revisions(db: Session, project_id: str, user_id: str, role: str):
    _project_or_404(db, project_id, user_id, role)
    return list(db.scalars(select(BOQRevision).where(BOQRevision.project_id == project_id).order_by(BOQRevision.revision_no.desc())).all())


def create_item(db: Session, revision_id: str, user_id: str, role: str, data: dict):
    revision = db.scalar(select(BOQRevision).where(BOQRevision.id == revision_id))
    if not revision:
        raise HTTPException(status_code=404, detail="BOQ revision not found")
    _project_or_404(db, revision.project_id, user_id, role)
    total = calculate_item_total(data["quantity"], data["unit_rate"])
    item = BOQItem(revision_id=revision_id, total=total, **data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_items(db: Session, revision_id: str, user_id: str, role: str):
    revision = db.scalar(select(BOQRevision).where(BOQRevision.id == revision_id))
    if not revision:
        raise HTTPException(status_code=404, detail="BOQ revision not found")
    _project_or_404(db, revision.project_id, user_id, role)
    return list(db.scalars(select(BOQItem).where(BOQItem.revision_id == revision_id).order_by(BOQItem.item_code)).all())


def estimate_summary(db: Session, revision_id: str, user_id: str, role: str):
    revision = db.scalar(select(BOQRevision).where(BOQRevision.id == revision_id))
    if not revision:
        raise HTTPException(status_code=404, detail="BOQ revision not found")
    _project_or_404(db, revision.project_id, user_id, role)
    estimate_total = db.scalar(select(func.coalesce(func.sum(BOQItem.total), 0)).where(BOQItem.revision_id == revision_id)) or Decimal("0")
    item_count = db.scalar(select(func.count(BOQItem.id)).where(BOQItem.revision_id == revision_id)) or 0
    budget_amount = Decimal("0")
    if revision.budget_id:
        budget_amount = db.scalar(select(Budget.amount).where(Budget.id == revision.budget_id)) or Decimal("0")
    variance = (estimate_total - budget_amount).quantize(CENT)
    variance_percent = None if budget_amount == 0 else (variance / budget_amount * Decimal("100")).quantize(CENT)
    return {"revision_id": revision_id, "budget_amount": budget_amount, "estimate_total": estimate_total, "variance": variance, "variance_percent": variance_percent, "item_count": item_count}
