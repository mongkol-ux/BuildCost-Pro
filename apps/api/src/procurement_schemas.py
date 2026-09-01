"""Validated DTOs for STEP 34 procurement APIs."""
from datetime import date
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

RequestStatus = Literal["DRAFT", "SUBMITTED", "APPROVED", "ORDERED", "RECEIVED", "CANCELLED"]
QuotationStatus = Literal["RECEIVED", "SELECTED", "REJECTED"]
POStatus = Literal["DRAFT", "ISSUED", "PARTIALLY_RECEIVED", "RECEIVED", "CANCELLED"]

class RequestCreate(BaseModel):
    request_no: str = Field(min_length=2, max_length=64)
    needed_by: date | None = None

class RequestResponse(RequestCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    status: RequestStatus

class RequestItemCreate(BaseModel):
    resource_id: str = Field(min_length=1, max_length=36)
    quantity: Decimal = Field(gt=0, max_digits=18, decimal_places=4)
    unit_rate: Decimal = Field(ge=0, max_digits=18, decimal_places=2)

class RequestItemResponse(RequestItemCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    request_id: str
    total: Decimal

class QuotationCreate(BaseModel):
    supplier_id: str = Field(min_length=1, max_length=36)
    quotation_no: str = Field(min_length=2, max_length=64)
    amount: Decimal = Field(ge=0, max_digits=18, decimal_places=2)
    quoted_at: date

class QuotationResponse(QuotationCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    request_id: str
    status: QuotationStatus

class PurchaseOrderCreate(BaseModel):
    supplier_id: str = Field(min_length=1, max_length=36)
    quotation_id: str | None = Field(default=None, min_length=1, max_length=36)
    po_no: str = Field(min_length=2, max_length=64)
    total: Decimal = Field(ge=0, max_digits=18, decimal_places=2)
    ordered_at: date | None = None

class PurchaseOrderResponse(PurchaseOrderCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    request_id: str
    status: POStatus

class POItemCreate(BaseModel):
    resource_id: str = Field(min_length=1, max_length=36)
    quantity: Decimal = Field(gt=0, max_digits=18, decimal_places=4)
    unit_rate: Decimal = Field(ge=0, max_digits=18, decimal_places=2)

class POItemResponse(POItemCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    purchase_order_id: str
    total: Decimal
    received_quantity: Decimal

class ReceiveCreate(BaseModel):
    quantity: Decimal = Field(gt=0, max_digits=18, decimal_places=4)
