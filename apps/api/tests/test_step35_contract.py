from datetime import date
from decimal import Decimal
import pytest
from pydantic import ValidationError
from src.accounting_schemas import AccountingTransactionCreate, FinancialPeriodCreate


def test_accounting_transaction_defaults_are_safe():
    item = AccountingTransactionCreate(type="EXPENSE", amount=Decimal("125.00"))
    assert item.tax_amount == Decimal("0")
    assert item.retention_amount == Decimal("0")
    assert item.payment_status == "UNPAID"


def test_accounting_transaction_rejects_negative_controls():
    with pytest.raises(ValidationError):
        AccountingTransactionCreate(type="EXPENSE", amount=Decimal("10.00"), retention_amount=Decimal("-0.01"))


def test_financial_period_accepts_same_day_boundary():
    item = FinancialPeriodCreate(period_code="2026-09-01", start_date=date(2026, 9, 1), end_date=date(2026, 9, 1))
    assert item.start_date == item.end_date
