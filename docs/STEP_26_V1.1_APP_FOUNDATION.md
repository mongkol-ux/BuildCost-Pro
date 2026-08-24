# STEP 26 — V1.1 App Foundation / Application Development Preparation

## Status

**COMPLETE — Foundation locked for V1.1 development.**

## Baseline

- V1.0 production baseline remains the release source of truth.
- V1.1 development is isolated on branch `v1.1-app-foundation`.
- `main` is not modified by this preparation step.
- Existing production API/backend remains the service boundary for the application.

## 26-A — Application Architecture

```text
BuildCost Pro V1.1
        |
        +-- Web Application
        |     +-- Authentication / Session
        |     +-- Dashboard
        |     +-- Projects
        |     +-- Cost Items / Estimates
        |     +-- Reports / Summary
        |     +-- Settings
        |
        +-- HTTPS API
        |
        +-- Existing Backend / Domain / Data Access
        |
        +-- Production Database
```

The client must communicate with the backend through documented API contracts. The client must not connect directly to the production database.

## 26-B — Application / Backend Boundary

The web application owns presentation, navigation, local UI state, form validation and API orchestration. The backend remains authoritative for authentication, authorization, business rules, persistence, validation and audit-sensitive operations.

## 26-C — V1.1 MVP Scope

### Included

- Authentication entry and session handling
- Application shell and navigation
- Dashboard foundation
- Project list and project detail foundation
- Cost-item / estimate foundation
- API client boundary
- Loading, empty and error states
- Logout

### Deferred

- AI assistant
- Advanced analytics
- Advanced export/report designer
- Multi-company expansion
- Payments
- Notification platform expansion

Deferred items are not blockers for the V1.1 application foundation.

## 26-D — Repository / Branch Strategy

- `main`: protected production baseline.
- `v1.1-app-foundation`: foundation work for V1.1.
- Future feature work should use focused feature branches and pull requests into the V1.1 development line.
- No direct modification of the V1.0 production baseline is required for this step.

## 26-E — API Contract Rules

- HTTPS only in deployed environments.
- Authentication credentials/tokens are never hard-coded in source.
- API base URL is environment-configured.
- Client treats non-2xx responses as explicit API errors.
- Client must not infer authorization from UI visibility alone; backend authorization remains authoritative.
- Request/response schemas must be documented before implementing business features.

## 26-F — Screen Structure

1. Login
2. Application shell
3. Dashboard
4. Projects
5. Project detail
6. Cost items / estimate
7. Settings

Navigation is intentionally small for the first application slice.

## 26-G — Foundation Deliverables

- V1.1 architecture document
- API boundary definition
- MVP scope lock
- Screen map
- Development branch
- Web application foundation marker
- API application foundation marker

## 26-H — Integration Foundation

The application is prepared to consume the existing API. Integration work must reuse the established authentication and business API contracts rather than bypassing them.

## 26-I — Authentication Foundation

Authentication is treated as a first-class application concern: login state, protected application routes, session expiry handling, unauthorized response handling and logout are defined as foundation requirements.

## 26-J — First Working App Slice

For this preparation release, the working slice is the application shell contract and navigation structure. Business calculations and production data workflows remain in the next development step so that V1.0 production behavior is not changed accidentally during foundation work.

## 26-K — Verification Gate

- [x] V1.0 baseline isolated from V1.1 work
- [x] Dedicated V1.1 branch created
- [x] App/backend boundary defined
- [x] MVP scope locked
- [x] Repository strategy defined
- [x] API integration rules defined
- [x] Authentication foundation defined
- [x] Initial screen map defined
- [x] No production database direct-access pattern introduced
- [x] No production secrets introduced

## 26-L — Closure

STEP 26 is closed when this document, the web foundation marker and the API foundation marker are committed to the V1.1 branch and the branch is ready for review.

## Next Step

**STEP 27 — V1.1 Core Application Development**
