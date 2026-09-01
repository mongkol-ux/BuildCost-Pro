"""Business rules for purchase requests, quotations, purchase orders and receiving."""
from decimal import Decimal
from uuid import uuid4
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .core_models import Project
from .resource_models import Resource, Supplier
from .procurement_models import ProcurementRequest, ProcurementRequestItem, ProcurementQuotation, PurchaseOrder, PurchaseOrderItem


def _project(db: Session, project_id: str, user_id: str, role: str):
    stmt = select(Project).where(Project.id == project_id)
    if role != "admin": stmt = stmt.where(Project.owner_user_id == user_id)
    obj = db.scalar(stmt)
    if not obj: raise HTTPException(404, "project not found")
    return obj

def _commit(db, obj):
    db.add(obj)
    try: db.commit()
    except IntegrityError:
        db.rollback(); raise HTTPException(409, "procurement reference already exists")
    db.refresh(obj); return obj

def _resource(db, rid):
    obj = db.get(Resource, rid)
    if not obj: raise HTTPException(404, "resource not found")
    return obj

def _supplier(db, sid):
    obj = db.get(Supplier, sid)
    if not obj or not obj.active: raise HTTPException(404, "active supplier not found")
    return obj

def create_request(db, project_id, user_id, role, data):
    _project(db, project_id, user_id, role)
    return _commit(db, ProcurementRequest(id=str(uuid4()), project_id=project_id, **data))

def list_requests(db, project_id, user_id, role):
    _project(db, project_id, user_id, role)
    return list(db.scalars(select(ProcurementRequest).where(ProcurementRequest.project_id == project_id).order_by(ProcurementRequest.created_at.desc())).all())

def add_request_item(db, request_id, user_id, role, data):
    req = db.get(ProcurementRequest, request_id)
    if not req: raise HTTPException(404, "procurement request not found")
    _project(db, req.project_id, user_id, role); _resource(db, data["resource_id"])
    total = (data["quantity"] * data["unit_rate"]).quantize(Decimal("0.01"))
    return _commit(db, ProcurementRequestItem(id=str(uuid4()), request_id=request_id, total=total, **data))

def list_request_items(db, request_id, user_id, role):
    req = db.get(ProcurementRequest, request_id)
    if not req: raise HTTPException(404, "procurement request not found")
    _project(db, req.project_id, user_id, role)
    return list(db.scalars(select(ProcurementRequestItem).where(ProcurementRequestItem.request_id == request_id)).all())

def create_quotation(db, request_id, user_id, role, data):
    req = db.get(ProcurementRequest, request_id)
    if not req: raise HTTPException(404, "procurement request not found")
    _project(db, req.project_id, user_id, role); _supplier(db, data["supplier_id"])
    return _commit(db, ProcurementQuotation(id=str(uuid4()), request_id=request_id, **data))

def list_quotations(db, request_id, user_id, role):
    req = db.get(ProcurementRequest, request_id)
    if not req: raise HTTPException(404, "procurement request not found")
    _project(db, req.project_id, user_id, role)
    return list(db.scalars(select(ProcurementQuotation).where(ProcurementQuotation.request_id == request_id).order_by(ProcurementQuotation.amount)).all())

def select_quotation(db, quotation_id, user_id, role):
    q = db.get(ProcurementQuotation, quotation_id)
    if not q: raise HTTPException(404, "quotation not found")
    req = db.get(ProcurementRequest, q.request_id); _project(db, req.project_id, user_id, role)
    for row in db.scalars(select(ProcurementQuotation).where(ProcurementQuotation.request_id == q.request_id)).all(): row.status = "SELECTED" if row.id == q.id else "REJECTED"
    db.commit(); db.refresh(q); return q

def create_po(db, request_id, user_id, role, data):
    req = db.get(ProcurementRequest, request_id)
    if not req: raise HTTPException(404, "procurement request not found")
    _project(db, req.project_id, user_id, role); _supplier(db, data["supplier_id"])
    if data.get("quotation_id"):
        q = db.get(ProcurementQuotation, data["quotation_id"])
        if not q or q.request_id != request_id: raise HTTPException(422, "quotation does not belong to request")
    return _commit(db, PurchaseOrder(id=str(uuid4()), request_id=request_id, **data))

def list_pos(db, request_id, user_id, role):
    req = db.get(ProcurementRequest, request_id)
    if not req: raise HTTPException(404, "procurement request not found")
    _project(db, req.project_id, user_id, role)
    return list(db.scalars(select(PurchaseOrder).where(PurchaseOrder.request_id == request_id).order_by(PurchaseOrder.created_at.desc())).all())

def add_po_item(db, po_id, user_id, role, data):
    po = db.get(PurchaseOrder, po_id)
    if not po: raise HTTPException(404, "purchase order not found")
    req = db.get(ProcurementRequest, po.request_id); _project(db, req.project_id, user_id, role); _resource(db, data["resource_id"])
    total = (data["quantity"] * data["unit_rate"]).quantize(Decimal("0.01"))
    return _commit(db, PurchaseOrderItem(id=str(uuid4()), purchase_order_id=po_id, total=total, **data))

def receive(db, item_id, user_id, role, quantity):
    item = db.get(PurchaseOrderItem, item_id)
    if not item: raise HTTPException(404, "purchase order item not found")
    po = db.get(PurchaseOrder, item.purchase_order_id); req = db.get(ProcurementRequest, po.request_id); _project(db, req.project_id, user_id, role)
    new_qty = item.received_quantity + quantity
    if new_qty > item.quantity: raise HTTPException(422, "received quantity exceeds ordered quantity")
    item.received_quantity = new_qty
    po.status = "RECEIVED" if _all_received(db, po.id) else "PARTIALLY_RECEIVED"
    db.commit(); db.refresh(item); return item

def _all_received(db, po_id):
    items = list(db.scalars(select(PurchaseOrderItem).where(PurchaseOrderItem.purchase_order_id == po_id)).all())
    return bool(items) and all(i.received_quantity >= i.quantity for i in items)
