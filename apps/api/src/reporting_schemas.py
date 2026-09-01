from decimal import Decimal
from pydantic import BaseModel


class ReportKPI(BaseModel):
    budget: Decimal
    actual: Decimal
    commitment: Decimal
    variance: Decimal
    variance_percent: Decimal | None
    income: Decimal
    expense: Decimal
    balance: Decimal


class CategoryReportRow(BaseModel):
    category: str
    amount: Decimal


class ReportingDashboard(BaseModel):
    project_id: str
    kpi: ReportKPI
    cost_by_category: list[CategoryReportRow]
    boq_total: Decimal
    boq_items: int
    procurement_commitment: Decimal
    accounting_expense: Decimal
    accounting_income: Decimal


class ReportExport(BaseModel):
    project_id: str
    report: ReportingDashboard
