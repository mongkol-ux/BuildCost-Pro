from decimal import Decimal
from importlib import import_module


# STEP 37 final verification coverage is intentionally kept in the API CI path.
def test_reporting_dashboard_schema_supports_financial_kpis():
    schemas = import_module("src.reporting_schemas")
    report = schemas.ReportingDashboard(
        project_id="p1",
        kpi=schemas.ReportKPI(
            budget=Decimal("1000.00"),
            actual=Decimal("650.00"),
            commitment=Decimal("200.00"),
            variance=Decimal("350.00"),
            variance_percent=Decimal("35.00"),
            income=Decimal("1200.00"),
            expense=Decimal("650.00"),
            balance=Decimal("550.00"),
        ),
        cost_by_category=[schemas.CategoryReportRow(category="MATERIAL", amount=Decimal("400.00"))],
        boq_total=Decimal("900.00"),
        boq_items=3,
        procurement_commitment=Decimal("200.00"),
        accounting_expense=Decimal("650.00"),
        accounting_income=Decimal("1200.00"),
    )
    assert report.kpi.variance == Decimal("350.00")
    assert report.kpi.variance_percent == Decimal("35.00")
    assert report.boq_items == 3


def test_reporting_api_routes_are_registered():
    main = import_module("src.main")
    paths = set(main.app.openapi()["paths"])
    assert "/api/v1/reports/projects/{project_id}/dashboard" in paths
    assert "/api/v1/reports/projects/{project_id}/export.csv" in paths
