from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from .auth_models import User
from .auth_router import current_user, db_session
from .accounting_schemas import FinancialPeriodCreate, FinancialPeriodResponse, PaymentCreate, PaymentResponse, RetentionCreate, RetentionResponse, ReconciliationCreate, ReconciliationResponse
from .accounting_service import close_period, create_payment, create_period, create_retention, list_payments, list_periods, list_retentions, reconcile

router = APIRouter(prefix="/api/v1", tags=["accounting"])


def actor(user: User):
    return user.id, user.role


@router.get("/projects/{project_id}/financial-periods", response_model=list[FinancialPeriodResponse])
def financial_periods(project_id: str, user: User = Depends(current_user), db: Session = Depends(db_session)):
    uid, role = actor(user)
    return list_periods(db, project_id, uid, role)


@router.post("/projects/{project_id}/financial-periods", response_model=FinancialPeriodResponse, status_code=status.HTTP_201_CREATED)
def financial_period_create(project_id: str, body: FinancialPeriodCreate, user: User = Depends(current_user), db: Session = Depends(db_session)):
    uid, role = actor(user)
    return create_period(db, project_id, uid, role, body.period_code, body.start_date, body.end_date)


@router.post("/projects/{project_id}/financial-periods/{period_id}/close", response_model=FinancialPeriodResponse)
def financial_period_close(project_id: str, period_id: str, user: User = Depends(current_user), db: Session = Depends(db_session)):
    uid, role = actor(user)
    return close_period(db, project_id, period_id, uid, role)


@router.get("/projects/{project_id}/payments", response_model=list[PaymentResponse])
def payments(project_id: str, user: User = Depends(current_user), db: Session = Depends(db_session)):
    uid, role = actor(user)
    return list_payments(db, project_id, uid, role)


@router.post("/projects/{project_id}/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def payment_create(project_id: str, body: PaymentCreate, user: User = Depends(current_user), db: Session = Depends(db_session)):
    uid, role = actor(user)
    return create_payment(db, project_id, uid, role, body.model_dump())


@router.get("/projects/{project_id}/retentions", response_model=list[RetentionResponse])
def retentions(project_id: str, user: User = Depends(current_user), db: Session = Depends(db_session)):
    uid, role = actor(user)
    return list_retentions(db, project_id, uid, role)


@router.post("/projects/{project_id}/retentions", response_model=RetentionResponse, status_code=status.HTTP_201_CREATED)
def retention_create(project_id: str, body: RetentionCreate, user: User = Depends(current_user), db: Session = Depends(db_session)):
    uid, role = actor(user)
    return create_retention(db, project_id, uid, role, body.model_dump())


@router.post("/projects/{project_id}/reconciliations", response_model=ReconciliationResponse, status_code=status.HTTP_201_CREATED)
def reconciliation_create(project_id: str, body: ReconciliationCreate, user: User = Depends(current_user), db: Session = Depends(db_session)):
    uid, role = actor(user)
    return reconcile(db, project_id, uid, role, body.financial_period_id, body.expected_total)
