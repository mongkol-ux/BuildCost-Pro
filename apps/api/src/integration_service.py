"""Cross-module project integration validation for V1.2."""
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .core_models import BOQItem, BOQRevision, Budget, Cost, Project, Transaction
from .procurement_models import ProcurementRequest, PurchaseOrder


class ProjectIntegrationError(ValueError):
    """Raised when a cross-module record cannot be resolved to the project."""


def build_project_integration_summary(db: Session, project_id: str) -> dict:
    """Return the canonical cross-module chain for one project.

    The project is the ownership boundary. BOQ and procurement records reach the
    project through their project/request relationships; cost and accounting
    transactions carry project_id directly. Commitment is reported separately
    from actual cost/accounting so the same value is never double-counted.
    """
    project = db.get(Project, project_id)
    if project is None:
        raise ProjectIntegrationError("project_not_found")

    budget_total = db.scalar(
        select(func.coalesce(func.sum(Budget.amount), 0)).where(Budget.project_id == project_id)
    )
    boq_total = db.scalar(
        select(func.coalesce(func.sum(BOQItem.total), 0))
        .join(BOQRevision, BOQItem.revision_id == BOQRevision.id)
        .where(BOQRevision.project_id == project_id)
    )
    commitment_total = db.scalar(
        select(func.coalesce(func.sum(PurchaseOrder.total), 0))
        .join(ProcurementRequest, PurchaseOrder.request_id == ProcurementRequest.id)
        .where(
            ProcurementRequest.project_id == project_id,
            PurchaseOrder.status.notin_(["CANCELLED", "VOID"]),
        )
    )
    cost_total = db.scalar(
        select(func.coalesce(func.sum(Cost.total), 0)).where(Cost.project_id == project_id)
    )
    expense_total = db.scalar(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.project_id == project_id,
            Transaction.type == "EXPENSE",
        )
    )

    return {
        "project_id": project_id,
        "budget_total": Decimal(str(budget_total or 0)),
        "boq_total": Decimal(str(boq_total or 0)),
        "commitment_total": Decimal(str(commitment_total or 0)),
        "cost_total": Decimal(str(cost_total or 0)),
        "accounting_expense_total": Decimal(str(expense_total or 0)),
    }
