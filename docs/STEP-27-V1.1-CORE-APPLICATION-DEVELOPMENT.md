# STEP 27 — V1.1 Core Application Development

**Project:** BuildCost Pro  
**Repository:** `mongkol-ux/BuildCost-Pro`  
**Branch:** `main`  
**Status:** COMPLETE — implementation committed to `main`

## Objective

Turn the V1.1 application foundation into a usable core business application with authenticated access and the primary project-cost workflow connected to the existing API.

## Delivered

- V1.1 web application shell and authenticated login flow.
- Access/refresh token persistence in browser storage.
- Automatic local session cleanup when the API returns HTTP 401.
- Project list loading and project selection.
- Project creation.
- Project summary dashboard with Budget, Costs, Income and Balance.
- Budget creation for the selected project.
- Cost creation with category, quantity and unit cost.
- Transaction creation for Income, Expense and Adjustment.
- Budget remaining and expense summary visibility.
- Refresh action for reloading the current application state.
- Loading state for project retrieval.
- Busy/disabled states for mutating actions to reduce duplicate submissions.
- Clear error and dismiss behavior.
- Selected-project visual state.
- Sign-out behavior that clears stored session tokens.

## API integration surface

The core web application consumes the existing API contract for:

- `POST /auth/login`
- `GET /api/v1/projects`
- `POST /api/v1/projects`
- `GET /api/v1/projects/{project_id}/summary`
- `POST /api/v1/projects/{project_id}/budgets`
- `POST /api/v1/projects/{project_id}/costs`
- `POST /api/v1/projects/{project_id}/transactions`

## Implementation evidence

The primary implementation is in `apps/web/app/page.tsx`.

Commit: `4c03c095184ab6172ed4be0576f23f631b32b5af`  
Commit message: `feat(web): complete V1.1 core application UX`

## Completion gate

STEP 27 is considered complete when the repository contains the V1.1 core application implementation, the core user journey is wired to the API, and the implementation is committed to `main`.

### Core user journey

1. Open BuildCost Pro.
2. Sign in.
3. Load/select a project.
4. Review financial summary.
5. Create a project when required.
6. Add a budget.
7. Add a cost.
8. Add a transaction.
9. Refresh and verify the summary.
10. Sign out.

## Next step

**STEP 28 — V1.1 Application Verification & Production Smoke Test**

STEP 28 should validate the deployed V1.1 web application against the live API, verify the core user journey end-to-end, and lock the evidence before proceeding to the next development phase.
