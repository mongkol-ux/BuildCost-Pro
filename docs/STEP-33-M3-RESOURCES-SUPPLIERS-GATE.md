# BuildCost Pro — STEP 33 M3 Resources & Suppliers

## Scope

Implement resource master data for Materials, Labor and Equipment; classifications; Supplier master data; resource rates and effective dates; protected API access; validation; tests; and CI/release evidence.

## Acceptance Criteria

- [x] Material resource master
- [x] Labor resource master
- [x] Equipment resource master
- [x] Resource classification/category
- [x] Supplier master
- [x] Resource-to-supplier linkage
- [x] Resource rate history
- [x] Effective-from/effective-to dates
- [x] Effective rate lookup
- [x] Server-side validation
- [x] Protected API endpoints
- [x] Database migration
- [x] Automated business test
- [ ] CI verification for final STEP 33 commit
- [ ] Production release-candidate verification for final STEP 33 commit
- [ ] Production health verification for final STEP 33 commit

## Implementation

Migration: `apps/api/migrations/004_resources_suppliers.sql`

Models: `apps/api/src/resource_models.py`

DTOs: `apps/api/src/resource_schemas.py`

Service: `apps/api/src/resource_service.py`

Router: `apps/api/src/resource_router.py`

Test: `apps/api/tests/test_resource_service.py`

## API

- `GET/POST /api/v1/resource-categories`
- `GET/POST /api/v1/suppliers`
- `GET/POST /api/v1/resources`
- `GET/POST /api/v1/resources/{resource_id}/rates`

All endpoints require the existing authenticated-user boundary.

## Gate rule

Implementation is not DONE until CI, production release-candidate validation and production health checks for the final commit are successful.

## Current state

**IMPLEMENTED — GATE PENDING CI**
