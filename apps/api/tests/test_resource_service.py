from datetime import date
from decimal import Decimal
from uuid import uuid4
from src.auth_router import SessionLocal
from src.resource_service import create_category, create_resource, create_supplier, create_rate, rate_on


def test_resource_master_and_effective_rate():
    db = SessionLocal()
    suffix = uuid4().hex[:8]
    try:
        category = create_category(db, f"Concrete-{suffix}", "MATERIAL")
        supplier = create_supplier(db, {"code": f"SUP-{suffix}", "name": "Test Supplier"})
        resource = create_resource(db, {"code": f"MAT-{suffix}", "name": "Concrete", "resource_type": "MATERIAL", "category_id": category.id, "unit": "m3", "supplier_id": supplier.id, "active": True})
        old = create_rate(db, resource.id, {"rate": Decimal("100.00"), "effective_from": date(2026, 1, 1), "effective_to": date(2026, 5, 31)})
        current = create_rate(db, resource.id, {"rate": Decimal("125.50"), "effective_from": date(2026, 6, 1)})
        assert rate_on(db, resource.id, date(2026, 3, 1)).rate == Decimal("100.00")
        assert rate_on(db, resource.id, date(2026, 9, 1)).rate == Decimal("125.50")
        assert old.effective_to < current.effective_from
    finally:
        db.close()
