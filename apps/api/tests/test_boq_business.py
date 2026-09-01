from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.boq_service import calculate_item_total
from src.core_schemas import BOQItemCreate


def test_boq_item_calculation_rounds_to_cents():
    assert calculate_item_total(Decimal("2.5000"), Decimal("120.00")) == Decimal("300.00")
    assert calculate_item_total(Decimal("3"), Decimal("10.125")) == Decimal("30.38")


def test_boq_quantity_must_be_positive():
    with pytest.raises(ValidationError):
        BOQItemCreate(item_code="A-1", description="Concrete", unit="m3", quantity=Decimal("0"), unit_rate=Decimal("100"))


def test_boq_rate_cannot_be_negative():
    with pytest.raises(ValidationError):
        BOQItemCreate(item_code="A-1", description="Concrete", unit="m3", quantity=Decimal("1"), unit_rate=Decimal("-1"))
