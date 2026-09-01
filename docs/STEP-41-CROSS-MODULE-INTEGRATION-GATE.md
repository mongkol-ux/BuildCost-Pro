# STEP 41 — Cross-Module Integration Gate

## Scope
Project → BOQ → Budget → Procurement → Commitment → Cost → Accounting.

## Implementation
- Added `apps/api/src/integration_service.py` as the canonical project integration summary service.
- Added protected `GET /api/v1/projects/{project_id}/integration-summary`.
- Reused the established project ownership boundary before traversing cross-module data.
- Commitment is derived from non-cancelled/non-void purchase orders through procurement requests.
- Cost and accounting expense totals are reported separately to avoid double counting.

## Consistency rules
- Budget, BOQ revision, cost, and accounting transaction records are project-scoped.
- Procurement requests are project-scoped and purchase orders resolve to the project through the request.
- A missing project is rejected by the integration service.

## Tests
`apps/api/tests/test_step41_cross_module_integration.py` covers:
- integration summary contract
- missing-project rejection
- protected route registration
- shared project ownership foreign-key chain
- commitment/cost/accounting separation

## Gate status
IMPLEMENTED — FINAL CI/PRODUCTION GATE PENDING.

STEP 41 must not be marked DONE until API CI, production release-candidate validation, and production operations health checks pass for the final integration commit.
