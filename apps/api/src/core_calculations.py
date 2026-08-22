"""Pure financial calculations shared by application and tests."""
from decimal import Decimal


def summarize(budget_total: Decimal, cost_total: Decimal, income_total: Decimal, expense_total: Decimal, adjustment_total: Decimal) -> dict[str, Decimal]:
    return {
        "budget_total": budget_total,
        "cost_total": cost_total,
        "income_total": income_total,
        "expense_total": expense_total,
        "adjustment_total": adjustment_total,
        "balance": income_total - expense_total + adjustment_total,
        "budget_remaining": budget_total - cost_total,
    }
