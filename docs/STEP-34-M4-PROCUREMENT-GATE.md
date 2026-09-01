# BuildCost Pro — STEP 34 M4 Procurement Gate

## Scope
STEP 34 implements the M4 Procurement scope defined by the V1.2 remaining-steps plan:
- Purchase request
- RFQ / quotation comparison
- Purchase order
- Commitment-ready PO totals
- Receiving/status lifecycle
- Protected API, UI and tests

## Implementation evidence
- `apps/api/src/procurement_models.py`
- `apps/api/src/procurement_schemas.py`
- `apps/api/src/procurement_service.py`
- `apps/api/src/procurement_router.py`
- `apps/api/migrations/005_procurement.sql`
- `apps/api/tests/test_procurement_business.py`
- `apps/web/app/procurement/page.tsx`
- API CI migration sequence includes migration 005.

## Business rules
1. Procurement requests belong to a project and are access-controlled by project ownership/admin role.
2. Request and PO items require positive quantity and non-negative unit rate.
3. Line totals are calculated server-side and rounded to 2 decimals.
4. Only active suppliers can be selected.
5. Quotations are compared by amount and selection marks the winner while rejecting other quotations for the request.
6. A purchase order may reference only a quotation belonging to the same request.
7. Receiving cannot exceed the ordered quantity.
8. PO status changes to `PARTIALLY_RECEIVED` or `RECEIVED` from receiving progress.

## Gate checklist
- [x] Scope aligned to M4 Procurement
- [x] Database schema implemented
- [x] Protected API implemented
- [x] Business validation implemented
- [x] Purchase request flow implemented
- [x] Quotation comparison/selection implemented
- [x] Purchase order flow implemented
- [x] Receiving lifecycle implemented
- [x] Web procurement page implemented
- [x] Business tests added
- [ ] API CI green on final STEP 34 commit
- [ ] Production Release Candidate green on final STEP 34 commit
- [ ] Production Operations Health green on final STEP 34 commit

## Status

**IMPLEMENTED — GATE PENDING CI/PRODUCTION**

`IMPLEMENTED` is not `DONE`. STEP 34 can be closed only after the final commit's CI, production release-candidate validation and production health checks are verified as successful.
