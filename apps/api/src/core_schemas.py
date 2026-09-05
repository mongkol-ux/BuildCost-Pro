"""Validated DTOs for the core business API."""
from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

ProjectStatus = Literal["DRAFT", "ACTIVE", "COMPLETED", "ARCHIVED"]
TransactionType = Literal["INCOME", "EXPENSE", "ADJUSTMENT"]
BOQStatus = Literal["DRAFT", "APPROVED", "ARCHIVED"]


class ProjectCreate(BaseModel):
    code: str = Field(min_length=2, max_length=64, pattern=r"^[A-Za-z0-9._-]+$")
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    status: ProjectStatus | None = None


class ProjectResponse(ProjectCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    owner_user_id: str
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime


class BudgetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    amount: Decimal = Field(ge=0, max_digits=18, decimal_places=2)


class BudgetResponse(BudgetCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    created_at: datetime
    updated_at: datetime


class CostCreate(BaseModel):
    category: str = Field(min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=5000)
    quantity: Decimal = Field(gt=0, max_digits=18, decimal_places=4)
    unit_cost: Decimal = Field(ge=0, max_digits=18, decimal_places=2)
    occurred_at: datetime | None = None


class CostResponse(CostCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    total: Decimal
    created_at: datetime


class TransactionCreate(BaseModel):
    type: TransactionType
    reference: str | None = Field(default=None, max_length=120)
    description: str | None = Field(default=None, max_length=5000)
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    occurred_at: datetime | None = None
    financial_period_id: str | None = Field(default=None, min_length=1, max_length=36)


class TransactionResponse(TransactionCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    created_at: datetime


class ProjectSummary(BaseModel):
    project_id: str
    budget_total: Decimal
    cost_total: Decimal
    income_total: Decimal
    expense_total: Decimal
    adjustment_total: Decimal
    balance: Decimal
    budget_remaining: Decimal


class BOQRevisionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    budget_id: str | None = Field(default=None, min_length=1, max_length=36)


class BOQRevisionResponse(BOQRevisionCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    revision_no: int
    status: BOQStatus
    created_at: datetime
    updated_at: datetime


class BOQItemCreate(BaseModel):
    item_code: str = Field(min_length=1, max_length=64)
    description: str = Field(min_length=1, max_length=1000)
    unit: str = Field(min_length=1, max_length=32)
    quantity: Decimal = Field(gt=0, max_digits=18, decimal_places=4)
    unit_rate: Decimal = Field(ge=0, max_digits=18, decimal_places=2)


class BOQItemResponse(BOQItemCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    revision_id: str
    total: Decimal
    created_at: datetime
    updated_at: datetime


class BOQEstimateSummary(BaseModel):
    revision_id: str
    budget_amount: Decimal
    estimate_total: Decimal
    variance: Decimal
