"""Protected REST endpoints for STEP 33 resources."""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from .auth_models import User
from .auth_router import current_user, db_session
from .resource_schemas import CategoryCreate, CategoryResponse, SupplierCreate, SupplierResponse, ResourceCreate, ResourceResponse, ResourceRateCreate, ResourceRateResponse, ResourceType
from .resource_service import create_category, list_categories, create_supplier, list_suppliers, create_resource, list_resources, create_rate, list_rates

router = APIRouter(prefix="/api/v1", tags=["resources"])

@router.get("/resource-categories", response_model=list[CategoryResponse])
def categories(resource_type: ResourceType | None = Query(None), user: User = Depends(current_user), db: Session = Depends(db_session)):
    return list_categories(db, resource_type)

@router.post("/resource-categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def category_create(body: CategoryCreate, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return create_category(db, body.name, body.resource_type)

@router.get("/suppliers", response_model=list[SupplierResponse])
def suppliers(active: bool | None = Query(None), user: User = Depends(current_user), db: Session = Depends(db_session)):
    return list_suppliers(db, active)

@router.post("/suppliers", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
def supplier_create(body: SupplierCreate, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return create_supplier(db, body.model_dump())

@router.get("/resources", response_model=list[ResourceResponse])
def resources(resource_type: ResourceType | None = Query(None), active: bool | None = Query(None), user: User = Depends(current_user), db: Session = Depends(db_session)):
    return list_resources(db, resource_type, active)

@router.post("/resources", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
def resource_create(body: ResourceCreate, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return create_resource(db, body.model_dump())

@router.get("/resources/{resource_id}/rates", response_model=list[ResourceRateResponse])
def rates(resource_id: str, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return list_rates(db, resource_id)

@router.post("/resources/{resource_id}/rates", response_model=ResourceRateResponse, status_code=status.HTTP_201_CREATED)
def rate_create(resource_id: str, body: ResourceRateCreate, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return create_rate(db, resource_id, body.model_dump())
