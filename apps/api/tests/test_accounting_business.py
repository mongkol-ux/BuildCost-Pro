from datetime import date
from decimal import Decimal
import pytest
from pydantic import ValidationError
from src.accounting_schemas import FinancialPeriodCreate, PaymentCreate, RetentionCreate
from src.accounting_service import reconciliation_status


def test_financial_period_requires_ordered_dates():
    with pytest.raises(ValidationError):
        FinancialPeriodCreate(period_code="2026-01", start_date=date(2026, 2, 1), end_date=date(2026, 1, 31))


def test_payment_amount_must_be_positive():
    with pytest.raises(ValidationError):
        PaymentCreate(amount=Decimal("0"), payment_date=date(2026, 1, 1))


def test_retention_amount_must_be_positive():
    with pytest.raises(ValidationError):
        RetentionCreate(amount=Decimal("0"))


def test_reconciliation_status_is_deterministic():
    assert reconciliation_status(Decimal("100.00"), Decimal("100.00")) == "MATCHED"
    assert reconciliation_status(Decimal("100.00"), Decimal("99.99")) == "MISMATCH"
