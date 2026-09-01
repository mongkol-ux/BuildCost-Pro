# BuildCost Pro — STEP 32 M2 BOQ & Estimating Gate

**Date:** 2026-09-01
**Branch:** main
**Scope:** BOQ structure/revisions, estimate items, quantity/rate calculation, budget linkage, variance, API/UI/tests.

## Requirements
- BOQ revisions are project-scoped and sequential.
- A revision may link to a budget owned by the same project.
- Estimate items require item code, description, unit, positive quantity and non-negative unit rate.
- Line totals are calculated server-side as quantity × unit rate and rounded to cents.
- Estimate summary exposes budget amount, estimate total, variance, variance percent and item count.
- Project ownership/role enforcement is inherited from the existing protected core service boundary.

## Implemented artifacts
- `apps/api/src/core_models.py`: BOQRevision and BOQItem ORM models.
- `apps/api/src/core_schemas.py`: BOQ request/response/summary DTOs and validation.
- `apps/api/src/boq_service.py`: revision/item services and deterministic calculation.
- `apps/api/src/core_router.py`: protected BOQ API endpoints.
- `apps/api/migrations/003_boq_estimating.sql`: BOQ schema and constraints.
- `apps/api/tests/test_boq_business.py`: calculation and validation tests.
- `apps/web/app/boq/page.tsx`: BOQ/Estimating UI.
- `.github/workflows/api-ci.yml`: CI now applies migration 003 before tests.

## API
- `GET/POST /api/v1/projects/{project_id}/boq`
- `GET/POST /api/v1/boq/{revision_id}/items`
- `GET /api/v1/boq/{revision_id}/summary`

## Gate evidence
Implementation commits landed on `main` before the CI trigger:
- `e8a7b6b167282da03b981cb5aabe9fd066189f2e`
- `d4672b214d9ebb0e924576b6dd6b4e7c1574cbb5`
- `52b1a78809e81268cd9c58ddc215d6cfdbd29041`
- `75f99617da8e031b6099ef5e35cf8770d0fa4485`
- `d55df2244b0129cf640ad2fc8969386a859e772a`
- `a12b3c964d9ed0cb74858d7b8d4f15d01404ee28`
- `31805b9661d7b332630fc7167c369d2ce960d910`
- `89e5684bec5123cb4d12a7533777b1a29120af70`

The latest API CI run for `89e5684bec5123cb4d12a7533777b1a29120af70` is currently **in progress**. The test job has reached container initialization and the container-build job is also in progress.

## Gate status

- G0 Scope: PASS
- G1 Design: PASS
- G2 Implementation: PASS
- G3 Validation: PENDING CI completion
- G4 Integration: PENDING CI completion
- G5 CI: PENDING
- G6 Security: Existing protected API boundary retained; final STEP gate remains pending CI/review.
- G7 Release: NOT REQUIRED to close the estimating implementation gate.
- G8 Closure: PENDING

**STEP 32 status: IMPLEMENTED — GATE PENDING CI**

Do not mark STEP 32 DONE until the CI/test and integration evidence is successful and this document is updated with the final evidence.
