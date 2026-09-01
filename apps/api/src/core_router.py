"""Protected REST endpoints for the BuildCost Pro core domain."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from .auth_models import User
from .auth_router import current_user, db_session
from .core_schemas import BudgetCreate, BudgetResponse, CostCreate, CostResponse, ProjectCreate, ProjectResponse, ProjectSummary, ProjectUpdate, TransactionCreate, TransactionResponse, BOQRevisionCreate, BOQRevisionResponse, BOQItemCreate, BOQItemResponse, BOQEstimateSummary
from .core_service import create_budget, create_cost, create_project, create_transaction, get_project, list_budgets, list_costs, list_projects, list_transactions, project_summary, update_project
from .boq_service import create_revision, list_revisions, create_item, list_items, estimate_summary
from .integration_service import build_project_integration_summary

router = APIRouter(prefix="/api/v1", tags=["core"])


def _actor(user: User) -> tuple[str, str]:
    return user.id, user.role


@router.get("/projects", response_model=list[ProjectResponse])
def projects(user: User = Depends(current_user), db: Session = Depends(db_session)):
    uid, role = _actor(user)
    return list_projects(db, uid, role)


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def project_create(body: ProjectCreate, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return create_project(db, user.id, body.code, body.name, body.description)


@router.get("/projects/{project_id}", response_model=ProjectResponse)
def project_get(project_id: str, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return get_project(db, project_id, user.id, user.role)


@router.get("/projects/{project_id}/integration-summary")
def project_integration_summary(project_id: str, user: User = Depends(current_user), db: Session = Depends(db_session)):
    # Reuse the established project ownership boundary before traversing modules.
    get_project(db, project_id, user.id, user.role)
    return build_project_integration_summary(db, project_id)
