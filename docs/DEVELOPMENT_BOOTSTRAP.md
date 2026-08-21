# BuildCost Pro V1.0 — Real Development Bootstrap

## Status

STEP 0–15 architecture is the baseline. This phase begins the real implementation.

## Repository Structure

```text
BuildCost-Pro/
├── apps/
│   ├── web/                 # Frontend application
│   └── api/                 # Backend API application
├── packages/
│   ├── domain/              # Core business rules and types
│   ├── contracts/            # API/domain contracts
│   └── config/              # Shared configuration
├── database/
│   ├── migrations/
│   └── seeds/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/
├── infra/
│   ├── docker/
│   └── deployment/
└── .github/workflows/
```

## Initial Implementation Rules

1. Master Document V1.0 remains the source of truth.
2. Domain logic must not depend on UI code.
3. API contracts are versioned and validated.
4. Database changes are migration-based.
5. Authentication and authorization are enforced server-side.
6. Financial calculations require deterministic tests.
7. No production deployment until CI, security, integration and E2E gates pass.

## First Vertical Slice

The first executable slice is:

`Health Check → API bootstrap → configuration → database connection boundary → domain module boundary → test harness`

Business modules will then be implemented incrementally: users, projects, estimates/BOQ, resources, procurement, transactions/accounting, documents/workflow, notifications, search, reporting, integrations and operations.
