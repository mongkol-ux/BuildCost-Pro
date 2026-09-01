# BuildCost Pro — STEP 42 Full QA / UAT Gate

## Scope

STEP 42 validates the V1.2 system as a whole after cross-module integration. The required scope is unit tests, integration tests, API contract coverage, UI smoke/build verification, permission tests, calculation/financial reconciliation tests, and a repeatable UAT acceptance checklist.

## Acceptance checklist

- [x] Unit/business tests cover core financial invariants.
- [x] Cross-module integration coverage exists for the Project ownership boundary and integration summary.
- [x] Authentication/permission regression coverage is retained.
- [x] Financial reconciliation checks verify budget, cost, income/expense balance and remaining budget without double-counting accounting expense.
- [x] API release-candidate validation runs schema, import, unit/integration tests, compilation and production web smoke checks.
- [x] Production operations health check verifies public production health.
- [ ] Final STEP 42 gate: API CI, production RC and production health must all be SUCCESS for the final implementation commit.

## UAT scenarios

1. Authenticated user can access their project and its integrated summary.
2. A different user cannot access the first user's project through the project ownership boundary.
3. Budget, cost and accounting expense totals reconcile to their source transactions.
4. Existing V1.1/V1.2 authentication and protected routes remain intact.
5. Production health and public web runtime remain available after the QA changes.

## Gate rule

Implementation alone is not completion. STEP 42 is DONE only after the final CI/release-candidate/production-health evidence passes for the same implementation state and the tracker records the evidence.
