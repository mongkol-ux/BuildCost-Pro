from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.core_calculations import summarize
from src.core_schemas import CostCreate, ProjectCreate, TransactionCreate


def test_financial_summary_is_deterministic():
    result = summarize(Decimal("100000.00"), Decimal("37500.00"), Decimal("50000.00"), Decimal("12000.00"), Decimal("1500.00"))
    assert result["balance"] == Decimal("39500.00")
    assert result["budget_remaining"] == Decimal("62500.00")


def test_cost_total_is_not_client_supplied():
    item = CostCreate(category="materials", quantity=Decimal("2.5000"), unit_cost=Decimal("120.00"))
    assert item.quantity * item.unit_cost == Decimal("300.0000")


def test_project_code_is_safe_and_bounded():
    assert ProjectCreate(code="PRJ-001", name="Warehouse").code == "PRJ-001"
    with pytest.raises(ValidationError):
        ProjectCreate(code="bad code", name="Warehouse")


def test_transaction_amount_must_be_positive():
    with pytest.raises(ValidationError):
        TransactionCreate(type="EXPENSE", amount=Decimal("0"))
