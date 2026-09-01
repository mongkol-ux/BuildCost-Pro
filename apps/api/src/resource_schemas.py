"""Validated DTOs for STEP 33 resources and suppliers."""
from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

ResourceType = Literal["MATERIAL", "LABOR", "EQUIPMENT"]

class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    resource_type: ResourceType

class CategoryResponse(CategoryCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime

class SupplierCreate(BaseModel):
    code: str = Field(min_length=2, max_length=64, pattern=r"^[A-Za-z0-9._-]+$")
    name: str = Field(min_length=1, max_length=255)
    contact_name: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=80)
    email: str | None = Field(default=None, max_length=255)
    active: bool = True

class SupplierResponse(SupplierCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime
    updated_at: datetime

class ResourceCreate(BaseModel):
    code: str = Field(min_length=2, max_length=64, pattern=r"^[A-Za-z0-9._-]+$")
    name: str = Field(min_length=1, max_length=255)
    resource_type: ResourceType
    category_id: str | None = Field(default=None, max_length=36)
    unit: str = Field(min_length=1, max_length=32)
    supplier_id: str | None = Field(default=None, max_length=36)
    active: bool = True

class ResourceResponse(ResourceCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime
    updated_at: datetime

class ResourceRateCreate(BaseModel):
    rate: Decimal = Field(ge=0, max_digits=18, decimal_places=2)
    effective_from: date
    effective_to: date | None = None

class ResourceRateResponse(ResourceRateCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    resource_id: str
    created_at: datetime
