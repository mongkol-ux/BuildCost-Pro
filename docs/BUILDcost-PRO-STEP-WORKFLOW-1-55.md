# BuildCost Pro — Master STEP Workflow & Gate 1–55

**Status:** LOCKED MASTER WORKFLOW  
**Project:** BuildCost Pro  
**Source of Truth:** GitHub `main`  
**Scope:** STEP 1 through STEP 55

## 1. Universal workflow

Every STEP follows this controlled lifecycle:

`Requirement → Design → Implementation → Validation → Integration → CI/Test → Review → Gate → Documentation → Close`

A STEP is **not DONE** merely because code or documentation exists. Its acceptance gate must pass.

## 2. Universal gates

- **G0 Scope:** objective, dependencies and acceptance criteria are defined.
- **G1 Design:** architecture/data/UI/API impact is reviewed.
- **G2 Implementation:** required artifacts are committed to GitHub.
- **G3 Validation:** unit/static/schema/calculation validation passes as applicable.
- **G4 Integration:** affected modules work together without breaking existing contracts.
- **G5 CI:** required automated checks pass.
- **G6 Security:** authentication, authorization, secrets and data isolation are checked where applicable.
- **G7 Release:** staging/production verification is completed where the STEP requires it.
- **G8 Closure:** evidence, documentation and status are recorded.

## 3. STEP workflow matrix

| STEP | Workstream | Required workflow | Primary gate/output |
|---|---|---|---|
| 1 | Requirements / System Baseline | Requirements → architecture → baseline review | G0/G1: approved baseline |
| 2 | Core Architecture | Architecture → components → interfaces → review | G1: architecture baseline |
| 3 | Data Model | Schema → relationships → migrations → validation | G1/G3: schema validated |
| 4 | API Foundation | Routes → schemas → services → API tests | G3/G5: API contract passes |
| 5 | Authentication | Auth design → implementation → negative tests | G3/G6: auth gate |
| 6 | Authorization | Roles → permissions → enforcement → tests | G6: RBAC gate |
| 7 | Database / Persistence | Models → migration → CRUD → integrity tests | G3/G5: persistence gate |
| 8 | Core Business Logic | Rules → calculations → edge cases → tests | G3: calculation gate |
| 9 | Frontend Foundation | UI architecture → components → API client | G1/G3: UI foundation |
| 10 | Core UI | Screens → forms → states → integration | G4/G5: UI gate |
| 11 | Project Module | Project workflow → API/UI → tests | G4: project gate |
| 12 | Budget Module | Budget rules → API/UI → reconciliation | G3/G4: budget gate |
| 13 | Cost Module | Cost rules → API/UI → reconciliation | G3/G4: cost gate |
| 14 | Transaction Module | Transaction rules → API/UI → audit checks | G3/G4: transaction gate |
| 15 | Dashboard / Summary | Aggregation → UI → calculation checks | G3/G4: summary gate |
| 16 | Integration Baseline | Cross-module integration → regression | G4/G5: integration gate |
| 17 | API Hardening | validation → error handling → contract tests | G3/G5: API hardening |
| 18 | Web Hardening | loading/error/empty states → responsive checks | G3/G5: web gate |
| 19 | Data Integrity | constraints → duplicate/ownership tests | G3/G6: integrity gate |
| 20 | Observability | health → logs → metrics/error handling | G5/G7: operations gate |
| 21 | CI/CD | workflows → build/test → deployment checks | G5: CI/CD gate |
| 22 | Deployment Foundation | environment → container/hosting → smoke test | G7: deployment gate |
| 23 | Security Baseline | threat review → secrets → auth/RBAC checks | G6: security gate |
| 24 | Post-Release Governance | release process → incident/change control | G8: governance gate |
| 25 | Production Readiness Prep | checklist → environment → smoke validation | G7: readiness gate |
| 26 | V1.1 App Foundation | application preparation → contracts → integration | G4/G5: foundation gate |
| 27 | V1.1 Core Application | feature implementation → tests → integration | G4/G5: core app gate |
| 28 | V1.1 Completion | regression → hardening → release checks | G5/G7: completion gate |
| 29 | Post-V1.1 Production Hardening | production fixes → reliability/security checks | G6/G7: hardening gate |
| 30 | V1.2 Scope Lock | product scope → dependencies → acceptance criteria | G0/G1: V1.2 baseline |
| 31 | M1 Project & Cost Expansion | requirements → API/model/UI → tests → integration | G3/G4/G5: M1 gate |
| 32 | M2 BOQ & Estimating | BOQ model → quantities/rates → calculations → UI | G3/G4: estimating gate |
| 33 | M3 Resources & Suppliers | masters → classifications → search/linking → tests | G3/G4: resource gate |
| 34 | M4 Procurement | PR → RFQ → quotation → PO → receiving → commitments | G4/G5: procurement gate |
| 35 | M5 Accounting & Financial Controls | financial rules → transactions → reconciliation → tests | G3/G6: finance gate |
| 36 | M6 Documents & Workflow | metadata → versions → approvals → audit trail | G4/G6: document gate |
| 37 | M7 Reporting & Dashboard | aggregates → reports → filters → export validation | G3/G4: reporting gate |
| 38 | M8 Notifications | events → notification rules → preferences → tests | G4/G5: notification gate |
| 39 | M9 Search | indexing strategy → filters → permissions → tests | G4/G6: search gate |
| 40 | M10 Security / QA / Ops | RBAC → audit → errors → regression/security suite | G5/G6: security/QA gate |
| 41 | Cross-Module Integration | Project → BOQ → Budget → Procurement → Commitment → Cost → Accounting | G4/G5: E2E integration gate |
| 42 | Full QA / UAT | unit → integration → API → UI → permission → financial reconciliation → UAT | G5/G8: UAT acceptance |
| 43 | Release Candidate | scope freeze → migration rehearsal → build → staging → rollback | G5/G7: RC gate |
| 44 | Production Release | deploy → migration → health → auth → core workflows → monitoring | G7: production release gate |
| 45 | V1.2 Production Ready | blocker closure → backup/restore → docs → release evidence | G7/G8: V1.2 READY |
| 46 | Production App Packaging | PWA/web packaging → production config → responsive validation | G5/G7: packaging gate |
| 47 | Mobile App Development | mobile shell → auth → core modules → API integration → device tests | G4/G5: mobile gate |
| 48 | Final UX/UI | Design System → all screens → responsive/accessibility/localization → visual QA | G3/G5: UX/UI gate |
| 49 | Real User UAT | realistic workflows → feedback → defect triage → fixes → acceptance | G8: UAT sign-off |
| 50 | Security Audit | threat model → auth/RBAC → storage → API → privacy → remediation | G6: security audit gate |
| 51 | Performance & Scale | load tests → DB/API tuning → caching/pagination → monitoring | G3/G5: performance gate |
| 52 | Billing & Subscription | plans → entitlements → payment → invoices → limits → failure handling | G4/G6: billing gate |
| 53 | App Store Release | signing → metadata → privacy/legal → release builds → store validation | G7: store release gate |
| 54 | Public Launch | production launch → monitoring → support → incident readiness | G7/G8: PUBLIC LAUNCH |
| 55 | V1.3 Continuous Development | feedback → backlog → prioritization → implementation → release cycle | G0/G8: V1.3 cycle active |

## 4. Special workflow — Excel validation

Canonical test workbook flow:

`Populate → Validate → Import to test project → Compare Expected_Results → Export → Reconcile → Record evidence`

Excel remains a test/import/export interface, not the system-of-record database.

Reference: `docs/EXCEL-TEST-IMPORT-SPEC.md`

## 5. Special workflow — receipt/bill capture

`Camera/Upload → Image Quality Check → OCR → Field Extraction → Confidence Review → User Confirmation → Expense → Project/BOQ/Category → Evidence Storage → Audit Trail`

Original receipt evidence must be preserved. Low-confidence OCR must require user review before final financial save.

Reference: `docs/RECEIPT-BILL-CAPTURE-OCR-SPEC.md`

## 6. Final UX/UI authority

All screens from STEP 31 through Public Launch must follow:

`docs/STEP-48-FINAL-UX-UI-SPEC.md`

No feature may introduce a conflicting navigation pattern, component behavior, financial display convention, permission-aware action, or mobile interaction without updating the UX/UI specification first.

## 7. Release rule

The project must never declare a STEP complete when a required gate is failing. Failed gates create a blocker and the workflow returns to implementation/validation until resolved.

## 8. Definition of production-ready

BuildCost Pro is considered production-ready only when the applicable implementation, automated tests, integration tests, security checks, deployment verification, operational evidence, backup/restore procedure, documentation, and acceptance gates have passed.

## 9. Source-of-truth hierarchy

1. Current production-safe code and migrations in GitHub `main`
2. Approved STEP specifications
3. `BUILDcost-PRO-MASTER-ROADMAP-0-55.md`
4. This master workflow/gate document
5. Supporting test and UX/UI specifications

If documents conflict, do not silently choose one; reconcile and update the source of truth before implementation.
