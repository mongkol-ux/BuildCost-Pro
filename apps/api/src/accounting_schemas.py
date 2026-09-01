from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class FinancialPeriodCreate(BaseModel):
    period_code: str = Field(min_length=1, max_length=32)
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def valid_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class FinancialPeriodResponse(FinancialPeriodCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    status: Literal["OPEN", "CLOSED"]
    closed_at: datetime | None
    created_at: datetime


class PaymentCreate(BaseModel):
    transaction_id: str | None = Field(default=None, min_length=1, max_length=36)
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    payment_date: date
    status: Literal["PAID", "VOID"] = "PAID"
    reference: str | None = Field(default=None, max_length=120)


class PaymentResponse(PaymentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    created_at: datetime


class RetentionCreate(BaseModel):
    transaction_id: str | None = Field(default=None, min_length=1, max_length=36)
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)


class RetentionResponse(RetentionCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    released_amount: Decimal
    status: Literal["HELD", "PARTIALLY_RELEASED", "RELEASED"]
    release_date: date | None
    created_at: datetime


class ReconciliationCreate(BaseModel):
    financial_period_id: str = Field(min_length=1, max_length=36)
    expected_total: Decimal = Field(ge=0, max_digits=18, decimal_places=2)


class ReconciliationResponse(ReconciliationCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    actual_total: Decimal
    difference: Decimal
    status: Literal["MATCHED", "MISMATCH"]
    reconciled_at: datetime
