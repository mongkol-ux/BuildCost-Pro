from decimal import Decimal
from types import SimpleNamespace
import pytest
from fastapi import HTTPException
from src.procurement_service import receive


def test_procurement_item_total_formula():
    quantity = Decimal("12.5000")
    unit_rate = Decimal("80.25")
    assert (quantity * unit_rate).quantize(Decimal("0.01")) == Decimal("1003.13")


def test_receive_rejects_over_receipt(monkeypatch):
    item = SimpleNamespace(received_quantity=Decimal("8"), quantity=Decimal("10"), purchase_order_id="po")
    po = SimpleNamespace(request_id="req", status="ISSUED")
    req = SimpleNamespace(project_id="project")

    class DB:
        def get(self, model, key):
            name = getattr(model, "__name__", "")
            return {"PurchaseOrderItem": item, "PurchaseOrder": po, "ProcurementRequest": req}.get(name)
        def commit(self): pass
        def refresh(self, obj): pass

    with pytest.raises(HTTPException) as exc:
        receive(DB(), "item", "user", "admin", Decimal("3"))
    assert exc.value.status_code == 422


def test_receive_accepts_partial(monkeypatch):
    item = SimpleNamespace(received_quantity=Decimal("2"), quantity=Decimal("10"), purchase_order_id="po")
    po = SimpleNamespace(request_id="req", status="ISSUED", id="po")
    req = SimpleNamespace(project_id="project")

    class DB:
        def get(self, model, key):
            name = getattr(model, "__name__", "")
            return {"PurchaseOrderItem": item, "PurchaseOrder": po, "ProcurementRequest": req}.get(name)
        def commit(self): pass
        def refresh(self, obj): pass
        def scalars(self, stmt): return self
        def all(self): return [item]

    monkeypatch.setattr("src.procurement_service._project", lambda *args: req)
    result = receive(DB(), "item", "user", "admin", Decimal("3"))
    assert result.received_quantity == Decimal("5")
    assert po.status == "PARTIALLY_RECEIVED"
