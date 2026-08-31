# BuildCost Pro — STEP 48 Final UX/UI Specification

**Status:** LOCKED DESIGN STANDARD
**Scope:** STEP 31 through STEP 54 Public Launch
**Product:** BuildCost Pro
**Repository:** `mongkol-ux/BuildCost-Pro`
**Branch:** `main`
**Purpose:** Single UX/UI reference for web, responsive web/PWA, and mobile application surfaces.

---

## 1. Design Principles

1. Construction-first: project, BOQ, budget, cost, procurement and financial status must be visible with minimal navigation.
2. Data-first: tables, totals, variances and status are more important than decorative UI.
3. Safe financial actions: destructive, approval, posting and payment actions require clear confirmation and permission-aware controls.
4. Consistent: the same terminology, components, states and interaction patterns are used across all modules.
5. Responsive: every production screen must work on desktop, tablet and mobile.
6. Accessible: keyboard navigation, readable contrast, focus states, semantic labels and touch-friendly controls are required.
7. Localized: Thai is the primary target language for the Thailand release; English is supported by the UI architecture.
8. No fake functionality: disabled/unavailable features must communicate their state rather than pretending to complete an action.

## 2. Visual Direction

- Product name: BuildCost Pro
- Tone: professional construction / finance / operations
- Theme: light-first production UI
- Primary navigation: dark navy/indigo
- Primary action: blue
- Surface: white / neutral gray
- Radius: compact-to-medium rounded cards and controls
- Density: information-dense desktop tables; simplified mobile cards
- Typography: Sarabun for Thai/English UI where available

## 3. Design Tokens

### Color roles

Use semantic roles rather than hard-coded colors in feature components.

- Primary: `primary-600` for main actions and active navigation
- Primary hover: `primary-700`
- Primary subtle: `primary-50`
- Success: green semantic role
- Warning: amber semantic role
- Danger: red semantic role
- Info: blue semantic role
- Neutral: slate/gray scale
- Background: neutral-50
- Surface: white
- Text: neutral-900
- Muted text: neutral-600
- Border: neutral-200

### Typography

- Display: 32 px / bold
- H1: 28 px / bold
- H2: 24 px / bold
- H3: 20 px / semibold
- H4: 18 px / semibold
- Body: 14–16 px / regular
- Small: 12–13 px / regular
- Numeric financial values: tabular/monospaced numerals where supported

### Spacing

Use a consistent 4 px base scale. Common production values: 4, 8, 12, 16, 20, 24, 32, 40.

### Controls

- Minimum touch target: 44 px on mobile
- Inputs: visible label, focus state, validation state
- Primary buttons: one clear action per section
- Destructive actions: danger treatment plus confirmation

## 4. Global Application Shell

### Desktop

- Left sidebar navigation
- Topbar with breadcrumb/context, notifications and user menu
- Main content area
- Optional right-side contextual drawer

### Mobile

- Compact top bar
- Bottom navigation for highest-frequency destinations
- Drawer/menu for secondary modules
- Sticky primary action when appropriate
- Tables collapse into cards or horizontally scroll only when necessary

### Global navigation

1. Dashboard
2. Projects
3. BOQ
4. Budget
5. Costs
6. Procurement
7. Suppliers
8. Accounting
9. Documents
10. Reports
11. Notifications
12. Settings

## 5. Production Screen Inventory

The following screen families are the baseline screens to be implemented and visually validated.

### Authentication

1. Login
2. Forgot Password
3. Reset Password
4. Session Expired / Re-authentication

### Dashboard

5. Main Dashboard
6. Dashboard Filters
7. KPI Detail / Drill-down

### Projects

8. Project List
9. Create Project
10. Edit Project
11. Project Overview
12. Project Activity / Timeline
13. Project Members / Permissions

### BOQ / Estimating

14. BOQ List
15. Create BOQ
16. BOQ Detail
17. BOQ Revision History
18. BOQ Item Editor
19. Estimate Summary
20. Estimate Variance

### Budget

21. Budget Summary
22. Budget Detail
23. Budget Category Breakdown
24. Budget vs Actual
25. Budget Adjustment

### Costs

26. Cost List
27. Create Cost
28. Cost Detail
29. Cost Category View
30. Cost Approval / Review
31. Cost Import / Validation

### Resources / Suppliers

32. Resource List
33. Resource Detail
34. Supplier List
35. Supplier Detail
36. Supplier Create/Edit

### Procurement

37. Purchase Request List
38. Purchase Request Detail
39. Create Purchase Request
40. RFQ List
41. Quotation Comparison
42. Purchase Order List
43. Purchase Order Detail
44. Receiving / Delivery Status
45. Commitment View

### Accounting / Finance

46. Accounting Overview
47. Transaction List
48. Transaction Detail
49. Create Transaction
50. Payment / Settlement
51. Financial Period / Controls
52. Reconciliation

### Documents / Workflow

53. Document List
54. Document Detail
55. Upload / Attach Document
56. Document Version History
57. Approval Inbox
58. Approval Detail
59. Workflow History / Audit Trail

### Reporting / Analytics

60. Reports Dashboard
61. Budget vs Actual Report
62. BOQ / Estimate Report
63. Cost Report
64. Procurement / Commitment Report
65. Profit & Loss
66. Cash Flow
67. Project Performance
68. Export / Report Options

### Notifications / User / Settings

69. Notifications List
70. Notification Detail
71. User Management
72. User Profile
73. Role / Permission Management
74. Company Settings
75. Project Settings
76. Application Preferences
77. Security / Sessions

### Mobile

78. Mobile Login
79. Mobile Dashboard
80. Mobile Project List
81. Mobile Project Detail
82. Mobile Cost List/Create
83. Mobile BOQ
84. Mobile Procurement
85. Mobile Reports
86. Mobile Notifications
87. Mobile Menu

The screen inventory may expand for implementation details, but existing screens must not diverge from these interaction conventions.

## 6. Dashboard Standard

The dashboard must prioritize:

- Total projects
- Total budget
- Actual cost
- Remaining budget
- Income
- Expense
- Balance / profit-loss where applicable
- Project progress
- Budget vs actual chart
- Recent activity
- Alerts requiring action

Users must be able to drill from KPI → project/module detail.

## 7. Project Detail Standard

Project Detail uses tabs or equivalent navigation:

`Overview | BOQ | Budget | Costs | Procurement | Transactions | Documents | Reports`

The header must show project identity, status and key financial KPIs.

## 8. Tables

Every major list must provide:

- Search
- Relevant filters
- Sort
- Pagination or controlled infinite loading
- Empty state
- Loading state
- Error state
- Permission-aware actions
- Row/detail navigation
- Mobile adaptation

Financial columns must use consistent currency formatting and right alignment for numeric values.

## 9. Forms

Every form must provide:

- Clear labels
- Required/optional indication
- Input constraints
- Inline validation
- Server-error display
- Save/Cancel behavior
- Loading state during submission
- Success feedback
- Unsaved-change protection where appropriate

Financial amounts must never be silently rounded in the UI. Display precision must follow the domain field contract.

## 10. Status System

Use consistent semantic status badges.

Examples:

- Draft
- Active / In Progress
- Pending
- Approved
- Rejected
- Completed
- Cancelled
- Archived
- Over Budget
- Paid
- Partially Paid

Status labels must be understandable without relying only on color.

## 11. Financial Display Rules

Canonical flow:

`BOQ/Estimate → Budget → Commitment → Actual Cost → Remaining → Variance → Profit/Loss`

Use:

- consistent currency symbol/locale
- thousands separators
- two decimal places for currency unless domain rules require otherwise
- explicit negative values
- clear variance sign and meaning
- no ambiguous green/red-only interpretation

## 12. Charts

Charts are secondary to exact numbers.

Required patterns:

- Budget vs Actual: grouped bars
- Trend: line chart
- Category distribution: donut/pie only when useful
- Progress: bar/progress indicator
- Financial composition: cards plus chart

Every chart requires a textual summary or accessible data alternative.

## 13. Feedback States

Every asynchronous surface must support:

### Loading
Skeleton or spinner with stable layout.

### Empty
Explain what is missing and provide the appropriate creation/import action.

### Error
Explain what failed and provide Retry when retry is meaningful.

### Success
Use concise confirmation and refresh affected data.

### Offline / Network failure
Preserve entered data where possible and clearly state that the operation did not complete.

### Permission denied
Explain that access is restricted; do not expose protected data.

## 14. Modal / Confirmation Rules

Confirmation is required for:

- Delete
- Archive
- Cancel committed workflow
- Posting/finalizing financial records
- Approval/rejection where irreversible or materially consequential
- Removing members/permissions

Modal copy must state the action and consequence clearly.

## 15. Mobile UX Rules

Mobile is not a shrunken desktop.

- Prioritize one task per screen
- Use cards for dense records
- Use bottom sheets/drawers for secondary actions
- Keep primary action reachable
- Use sticky totals for long financial forms when helpful
- Avoid tiny table text
- Support portrait-first layouts
- Preserve all critical financial information

## 16. Accessibility

Minimum requirements:

- Semantic HTML
- Keyboard navigation on web
- Visible focus state
- Form labels associated with inputs
- Accessible names for icon buttons
- Color is never the only status signal
- Charts have text alternatives
- Error messages are associated with fields
- Touch targets meet mobile minimums

## 17. Localization

Thai UI terminology must be consistent across modules. English strings must be externalized rather than hard-coded inside feature components.

Currency, date and number formatting must respect locale and project/company configuration.

## 18. Permission-Aware UX

The UI must reflect server authorization but must not be treated as the security boundary.

- Hide actions the user cannot perform when appropriate
- Also handle server-side 403 responses gracefully
- Read-only users can view permitted data without edit controls
- Admin controls are isolated from ordinary workflows

## 19. Design-to-Code Rules

1. Components must consume design tokens.
2. Feature pages must reuse shared components.
3. Do not create one-off button/input/table variants without documenting the reason.
4. API state must map to explicit UI states.
5. No production page may contain placeholder lorem ipsum or fake success data.
6. Test data must be visually distinguishable in development/staging where necessary.
7. Responsive breakpoints must be centralized.
8. Accessibility checks are part of Definition of Done.

## 20. UX/UI Definition of Done

A screen is complete only when:

- Desktop layout is validated
- Tablet layout is validated where applicable
- Mobile layout is validated
- Loading/empty/error/success states exist
- Permission behavior is correct
- Form validation is complete
- API data is real and correctly formatted
- Financial calculations display consistently
- Accessibility checks pass
- Visual regression/smoke checks pass where configured
- No known critical UX defect remains

## 21. Release Gates

### STEP 31–40
New screens must follow this specification from the first implementation; do not postpone consistency to STEP 48.

### STEP 41–42
Cross-module flows and UAT validate navigation, terminology and state consistency.

### STEP 43–44
Release Candidate and Production Release require all critical screens to pass responsive and functional smoke checks.

### STEP 48
Final UX/UI is a hardening and consistency phase, not a redesign from scratch.

### STEP 53–54
Store/public-launch screenshots and marketing surfaces must represent the actual production UI.

## 22. Source-of-Truth Rule

This file is the UX/UI baseline for BuildCost Pro from STEP 31 through Public Launch. Any material change to navigation, visual tokens, terminology, screen hierarchy or interaction pattern must update this specification and be reviewed before implementation.

## 23. Final Target

BuildCost Pro should feel like one coherent construction-finance application across:

`Web → Responsive Web/PWA → Android → iOS`

The user should be able to move from project setup to BOQ, budget, procurement, cost, accounting and reporting without learning a different interface for each module.
