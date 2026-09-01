"""Protected REST endpoints for STEP 34 procurement."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from .auth_models import User
from .auth_router import current_user, db_session
from .procurement_schemas import RequestCreate, RequestResponse, RequestItemCreate, RequestItemResponse, QuotationCreate, QuotationResponse, PurchaseOrderCreate, PurchaseOrderResponse, POItemCreate, POItemResponse, ReceiveCreate
from .procurement_service import create_request, list_requests, add_request_item, list_request_items, create_quotation, list_quotations, select_quotation, create_po, list_pos, add_po_item, receive

router = APIRouter(prefix="/api/v1", tags=["procurement"])

@router.get("/projects/{project_id}/procurement/requests", response_model=list[RequestResponse])
def requests(project_id: str, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return list_requests(db, project_id, user.id, user.role)

@router.post("/projects/{project_id}/procurement/requests", response_model=RequestResponse, status_code=status.HTTP_201_CREATED)
def request_create(project_id: str, body: RequestCreate, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return create_request(db, project_id, user.id, user.role, body.model_dump())

@router.get("/procurement/requests/{request_id}/items", response_model=list[RequestItemResponse])
def request_items(request_id: str, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return list_request_items(db, request_id, user.id, user.role)

@router.post("/procurement/requests/{request_id}/items", response_model=RequestItemResponse, status_code=status.HTTP_201_CREATED)
def request_item_create(request_id: str, body: RequestItemCreate, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return add_request_item(db, request_id, user.id, user.role, body.model_dump())

@router.get("/procurement/requests/{request_id}/quotations", response_model=list[QuotationResponse])
def quotations(request_id: str, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return list_quotations(db, request_id, user.id, user.role)

@router.post("/procurement/requests/{request_id}/quotations", response_model=QuotationResponse, status_code=status.HTTP_201_CREATED)
def quotation_create(request_id: str, body: QuotationCreate, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return create_quotation(db, request_id, user.id, user.role, body.model_dump())

@router.post("/procurement/quotations/{quotation_id}/select", response_model=QuotationResponse)
def quotation_select(quotation_id: str, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return select_quotation(db, quotation_id, user.id, user.role)

@router.get("/procurement/requests/{request_id}/purchase-orders", response_model=list[PurchaseOrderResponse])
def purchase_orders(request_id: str, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return list_pos(db, request_id, user.id, user.role)

@router.post("/procurement/requests/{request_id}/purchase-orders", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
def purchase_order_create(request_id: str, body: PurchaseOrderCreate, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return create_po(db, request_id, user.id, user.role, body.model_dump())

@router.post("/procurement/purchase-orders/{po_id}/items", response_model=POItemResponse, status_code=status.HTTP_201_CREATED)
def po_item_create(po_id: str, body: POItemCreate, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return add_po_item(db, po_id, user.id, user.role, body.model_dump())

@router.post("/procurement/purchase-order-items/{item_id}/receive", response_model=POItemResponse)
def po_item_receive(item_id: str, body: ReceiveCreate, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return receive(db, item_id, user.id, user.role, body.quantity)
