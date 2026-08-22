"""Protected REST endpoints for the BuildCost Pro core domain."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from .auth_models import User
from .auth_router import current_user, db_session
from .core_schemas import BudgetCreate, BudgetResponse, CostCreate, CostResponse, ProjectCreate, ProjectResponse, ProjectSummary, ProjectUpdate, TransactionCreate, TransactionResponse
from .core_service import create_budget, create_cost, create_project, create_transaction, get_project, list_budgets, list_costs, list_projects, list_transactions, project_summary, update_project

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


@router.patch("/projects/{project_id}", response_model=ProjectResponse)
def project_update(project_id: str, body: ProjectUpdate, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return update_project(db, project_id, user.id, user.role, body.model_dump(exclude_unset=True))


@router.get("/projects/{project_id}/summary", response_model=ProjectSummary)
def summary(project_id: str, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return project_summary(db, project_id, user.id, user.role)


@router.get("/projects/{project_id}/budgets", response_model=list[BudgetResponse])
def budgets(project_id: str, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return list_budgets(db, project_id, user.id, user.role)


@router.post("/projects/{project_id}/budgets", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def budget_create(project_id: str, body: BudgetCreate, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return create_budget(db, project_id, user.id, user.role, body.name, body.amount)


@router.get("/projects/{project_id}/costs", response_model=list[CostResponse])
def costs(project_id: str, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return list_costs(db, project_id, user.id, user.role)


@router.post("/projects/{project_id}/costs", response_model=CostResponse, status_code=status.HTTP_201_CREATED)
def cost_create(project_id: str, body: CostCreate, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return create_cost(db, project_id, user.id, user.role, body.model_dump())


@router.get("/projects/{project_id}/transactions", response_model=list[TransactionResponse])
def transactions(project_id: str, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return list_transactions(db, project_id, user.id, user.role)


@router.post("/projects/{project_id}/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def transaction_create(project_id: str, body: TransactionCreate, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return create_transaction(db, project_id, user.id, user.role, body.model_dump())
