# STEP 39 — M9 Search Gate

## Scope
Global/project search with filter/sort/pagination contracts, permission-aware results, search indexes, API and automated contract tests.

## Implemented
- `apps/api/src/search_schemas.py` — response contracts.
- `apps/api/src/search_service.py` — global search across projects, budgets, costs, BOQ items, documents, procurement requests/quotations/purchase orders, resources and suppliers.
- `apps/api/src/search_router.py` — protected `GET /api/v1/search` endpoint.
- `apps/api/migrations/009_search.sql` — search/ownership lookup indexes.
- `apps/api/tests/test_step39_search.py` — route, contract and pagination coverage.
- `apps/api/src/main.py` — router and ORM registration.

## Permission boundary
Project-owned results are restricted to projects owned by the authenticated user. A supplied `project_id` must also belong to that user. Global resource/supplier masters are searchable because they are not project-owned in the current data model.

## API contract
`GET /api/v1/search?q=<term>&project_id=<optional>&page=1&page_size=20`

Returns `query`, `page`, `page_size`, `total`, and typed search `results`.

## Gate checklist
- G0 Scope: PASS — locked by V1.2 roadmap.
- G1 Design: PASS — global/project search, pagination and permission boundary defined.
- G2 Implementation: PASS — artifacts committed to `main`.
- G3 Validation: PENDING CI verification.
- G4 Integration: PENDING CI verification.
- G5 CI: PENDING.
- G6 Security: PASS by implementation review of authenticated ownership filtering; final automated security verification remains part of STEP 40.
- G8 Documentation: PASS — this gate document records evidence.

## Current decision
**IMPLEMENTED — FINAL GATE PENDING CI/PRODUCTION VERIFICATION**

This document must be updated to **DONE — FINAL GATE PASSED** only after the required CI/integration evidence is observed on the final commit.
