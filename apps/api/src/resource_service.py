"""Business service for STEP 33 resource master data."""
from datetime import date
from uuid import uuid4
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .resource_models import ResourceCategory, Supplier, Resource, ResourceRate


def _commit(db, obj):
    db.add(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="resource master code or name already exists")
    db.refresh(obj)
    return obj


def create_category(db, name, resource_type):
    return _commit(db, ResourceCategory(id=str(uuid4()), name=name.strip(), resource_type=resource_type))

def list_categories(db, resource_type=None):
    stmt = select(ResourceCategory).order_by(ResourceCategory.name)
    if resource_type:
        stmt = stmt.where(ResourceCategory.resource_type == resource_type)
    return list(db.scalars(stmt).all())

def create_supplier(db, data):
    data = {k: v for k, v in data.items() if v is not None}
    return _commit(db, Supplier(id=str(uuid4()), **data))

def list_suppliers(db, active=None):
    stmt = select(Supplier).order_by(Supplier.name)
    if active is not None:
        stmt = stmt.where(Supplier.active == active)
    return list(db.scalars(stmt).all())

def create_resource(db, data):
    data = {k: v for k, v in data.items() if v is not None}
    return _commit(db, Resource(id=str(uuid4()), **data))

def list_resources(db, resource_type=None, active=None):
    stmt = select(Resource).order_by(Resource.name)
    if resource_type:
        stmt = stmt.where(Resource.resource_type == resource_type)
    if active is not None:
        stmt = stmt.where(Resource.active == active)
    return list(db.scalars(stmt).all())

def create_rate(db, resource_id, data):
    if data.get("effective_to") and data["effective_to"] < data["effective_from"]:
        raise HTTPException(status_code=422, detail="effective_to must be on or after effective_from")
    resource = db.get(Resource, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="resource not found")
    rate = ResourceRate(id=str(uuid4()), resource_id=resource_id, **data)
    return _commit(db, rate)

def list_rates(db, resource_id):
    if not db.get(Resource, resource_id):
        raise HTTPException(status_code=404, detail="resource not found")
    return list(db.scalars(select(ResourceRate).where(ResourceRate.resource_id == resource_id).order_by(ResourceRate.effective_from.desc())).all())

def rate_on(db, resource_id, on_date: date):
    stmt = select(ResourceRate).where(ResourceRate.resource_id == resource_id, ResourceRate.effective_from <= on_date).order_by(ResourceRate.effective_from.desc())
    for row in db.scalars(stmt).all():
        if row.effective_to is None or row.effective_to >= on_date:
            return row
    return None
