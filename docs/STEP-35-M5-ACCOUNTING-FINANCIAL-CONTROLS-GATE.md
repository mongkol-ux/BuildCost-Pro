# STEP 35 — M5 Accounting & Financial Controls

## Scope

Implements the V1.2 M5 scope:
- Cost/income/expense transaction expansion
- Payment support
- Retention support
- Financial periods and close controls
- Reconciliation/audit rules
- Protected API and Web UI
- Business validation tests

## Implementation

- `apps/api/src/accounting_models.py`
- `apps/api/src/accounting_schemas.py`
- `apps/api/src/accounting_service.py`
- `apps/api/src/accounting_router.py`
- `apps/api/migrations/006_accounting_financial_controls.sql`
- `apps/api/tests/test_accounting_business.py`
- `apps/web/app/accounting/page.tsx`
- `.github/workflows/api-ci.yml` includes migration 006

## Financial controls

1. Financial periods require an ordered date range.
2. A closed period rejects new accounting transactions.
3. Accounting transaction dates must fall within their selected period.
4. Payment and retention amounts are positive and project-scoped.
5. Retention cannot exceed the linked transaction retention allowance.
6. Reconciliation stores expected total, actual total, difference and match status.

## Gate

Status: **IMPLEMENTED — GATE PENDING CI/PRODUCTION**

Required evidence before DONE:
- API CI success
- Production Release Candidate success
- Production Operations Health success
- No unresolved P0 test or migration failure
