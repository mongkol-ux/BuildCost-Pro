from decimal import Decimal

from src.core_models import BOQRevision, Budget, Cost, Transaction
from src.core_router import router
from src.integration_service import ProjectIntegrationError, build_project_integration_summary
from src.main import app
from src.procurement_models import ProcurementRequest, PurchaseOrder


class FakeDB:
    def __init__(self):
        self.scalar_values = iter(
            [
                Decimal("100000.00"),
                Decimal("90000.00"),
                Decimal("25000.00"),
                Decimal("18000.00"),
                Decimal("17000.00"),
            ]
        )

    def get(self, model, project_id):
        assert model.__name__ == "Project"
        return object()

    def scalar(self, statement):
        return next(self.scalar_values)


def test_step41_integration_summary_contract():
    result = build_project_integration_summary(FakeDB(), "project-1")
    assert result == {
        "project_id": "project-1",
        "budget_total": Decimal("100000.00"),
        "boq_total": Decimal("90000.00"),
        "commitment_total": Decimal("25000.00"),
        "cost_total": Decimal("18000.00"),
        "accounting_expense_total": Decimal("17000.00"),
    }


def test_step41_missing_project_is_blocked():
    class MissingProjectDB(FakeDB):
        def get(self, model, project_id):
            return None

    try:
        build_project_integration_summary(MissingProjectDB(), "missing")
        assert False, "expected ProjectIntegrationError"
    except ProjectIntegrationError as exc:
        assert str(exc) == "project_not_found"


def test_step41_route_registered_and_protected():
    paths = app.openapi()["paths"]
    assert "/api/v1/projects/{project_id}/integration-summary" in paths
    route = next(r for r in router.routes if r.path == "/api/v1/projects/{project_id}/integration-summary")
    assert route.methods == {"GET"}
    assert {d.call.__name__ for d in route.dependant.dependencies} >= {"current_user", "db_session"}


def _fk_targets(model, column_name):
    column = model.__table__.c[column_name]
    return {fk.target_fullname for fk in column.foreign_keys}


def test_step41_shared_project_ownership_chain():
    assert "projects.id" in _fk_targets(Budget, "project_id")
    assert "projects.id" in _fk_targets(Cost, "project_id")
    assert "projects.id" in _fk_targets(Transaction, "project_id")
    assert "projects.id" in _fk_targets(BOQRevision, "project_id")
    assert "projects.id" in _fk_targets(ProcurementRequest, "project_id")
    assert "procurement_requests.id" in _fk_targets(PurchaseOrder, "request_id")


def test_step41_commitment_is_not_accounting_cost():
    result = build_project_integration_summary(FakeDB(), "project-1")
    assert result["commitment_total"] != result["cost_total"]
    assert result["commitment_total"] != result["accounting_expense_total"]
