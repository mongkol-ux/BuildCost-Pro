# BuildCost Pro — STEP 31 V1.2 Scope / Architecture / Gate

**Project:** BuildCost Pro  
**Repository:** `mongkol-ux/BuildCost-Pro`  
**Branch:** `main`  
**Date:** 2026-09-01  
**Purpose:** V1.2 transition and M1 Project & Cost Management expansion baseline

## 1. Source-of-Truth alignment

STEP 31 follows the Master Roadmap and the existing V1.2 execution tracker. V1.1 remains the foundation; STEP 31 extends the existing project/cost domain rather than redesigning the V1.1 core.

Authoritative references:
- `docs/BUILDcost-PRO-MASTER-ROADMAP-0-55.md`
- `docs/BUILDcost-PRO-STEP-WORKFLOW-1-55.md`
- `docs/STEP-30-V1.2-PRODUCT-EXPANSION.md`
- `docs/STEP-31-V1.2-M1-PROJECT-COST-EXPANSION.md`
- `docs/IMPLEMENTATION-STATUS-31-55.md`
- `docs/STEP-48-FINAL-UX-UI-SPEC.md`

## 2. STEP 31 scope lock

### In scope
1. Project lifecycle/detail expansion
2. Budget drill-down
3. Cost drill-down
4. Cost categories
5. Project financial controls
6. Protected API schemas/services/routes
7. Web application integration
8. Existing authentication/authorization preservation
9. Unit, integration and UI smoke testing
10. Production release-process validation

### Explicitly out of scope for STEP 31
- BOQ/estimating implementation (STEP 32)
- Resources/suppliers (STEP 33)
- Procurement (STEP 34)
- Accounting module expansion (STEP 35)
- Documents/workflow (STEP 36)
- Reporting/dashboard expansion (STEP 37)
- Notifications/search/security hardening beyond the STEP 31 acceptance surface

## 3. Current V1.1/V1.2 foundation observed

The repository already contains a working core project/cost foundation:
- `Project`, `Budget`, `Cost`, and `Transaction` domain models
- protected `/api/v1/projects` routes and project subresources
- project summary calculation
- business tests for deterministic financial calculations and validation
- persistence/integration coverage for project, budget, cost and transaction flows
- web application project/budget/cost interaction

This is the baseline to extend; it must not be replaced by a parallel domain implementation.

## 4. Architecture contract

```text
Web UI
  -> authenticated REST API /api/v1
      -> domain service layer
          -> SQLAlchemy models / controlled migrations
              -> PostgreSQL-compatible persistence
```

Rules:
- Keep authentication/authorization at the API boundary.
- Keep financial calculations server-side.
- Never trust a client-supplied cost total when quantity and unit cost exist.
- Preserve project ownership isolation for non-admin users.
- Use controlled database migrations for schema changes.
- Keep API response contracts explicit through Pydantic schemas.
- Preserve V1.1 routes and behavior unless a documented backward-compatible extension is required.

## 5. M1 feature acceptance matrix

| ID | Capability | Acceptance criterion | Priority |
|---|---|---|---|
| M1-01 | Project detail | Authenticated owner can retrieve project detail | P1 |
| M1-02 | Project lifecycle | Project status is explicit and updateable through the protected API | P1 |
| M1-03 | Budget drill-down | Project budgets can be listed and created without cross-project access | P1 |
| M1-04 | Cost drill-down | Project costs can be listed and created with server-calculated total | P1 |
| M1-05 | Cost categories | Cost records expose a bounded category field | P1 |
| M1-06 | Financial summary | Budget/cost/income/expense/adjustment aggregates are deterministic | P1 |
| M1-07 | Authorization | Non-admin user cannot read or mutate another owner's project resources | P0 |
| M1-08 | Validation | Invalid project codes and non-positive transaction amounts are rejected | P0 |
| M1-09 | Integration | Project -> budget -> cost -> transaction -> summary flow persists correctly | P1 |
| M1-10 | Web integration | Core project/cost workflow is reachable from the web application | P1 |

## 6. Test gate

Required before STEP 31 can be marked DONE:

- Unit tests: PASS
- Integration tests: PASS
- API/auth authorization tests: PASS
- Web/UI smoke tests: PASS
- Regression suite: PASS
- Production release/health gate: PASS
- Git working baseline: reproducible from `main`

## 7. Evidence snapshot

The current repository contains business and integration tests for the existing core domain. The latest `main` commit is `0b3cecc660ef19f8c73287c1cab7079a140b4d17` (`docs: add STEP E production closure evidence`).

At the checkpoint review, two reported CI/production service checks are successful, while one check is failing. Therefore this document records the implementation/scope baseline but does **not** falsely declare STEP 31 DONE.

## 8. Gate decision

**STEP 31 implementation baseline: READY / PARTIALLY IMPLEMENTED**  
**STEP 31 final gate: BLOCKED** until the failing CI/production check and any remaining M1 acceptance evidence are resolved and re-tested.

### Exit condition

```text
Fix failing gate
    -> run unit/integration/UI/regression tests
    -> verify production release process
    -> confirm all required checks PASS
    -> update implementation tracker: STEP 31 = DONE
    -> open STEP 32
```

## 9. Anti-regression rule

No STEP 32 work may replace or bypass the STEP 31 project/cost contracts. New BOQ functionality must integrate with the project and financial model through explicit, tested contracts.
