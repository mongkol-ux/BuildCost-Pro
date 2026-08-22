# BuildCost Pro — Core Business API V1

## Scope

This slice moves the production API beyond authentication into the first real business domain:

- Projects
- Budgets
- Costs
- Transactions
- Project financial summary

## API

Protected endpoints are under `/api/v1` and require a valid authentication session.

- `GET/POST /api/v1/projects`
- `GET/PATCH /api/v1/projects/{project_id}`
- `GET /api/v1/projects/{project_id}/summary`
- `GET/POST /api/v1/projects/{project_id}/budgets`
- `GET/POST /api/v1/projects/{project_id}/costs`
- `GET/POST /api/v1/projects/{project_id}/transactions`

## Security boundary

Normal users and managers can access only projects they own. Administrators can access all projects. Business records are linked to the owning project with PostgreSQL foreign keys and cascading child deletion.

## Financial rules

- Cost `total` is calculated server-side as `quantity × unit_cost` and rounded to 2 decimal places.
- Budget amounts cannot be negative.
- Cost quantities must be positive and unit costs cannot be negative.
- Transaction amounts must be positive.
- Balance = income − expense + adjustment.
- Budget remaining = budget total − cost total.

## Database

`apps/api/migrations/002_core_business.sql` adds the PostgreSQL schema. Production containers execute all checked-in SQL migrations before starting the API.

## Validation

The release-candidate CI applies all migrations, imports the application, runs unit/integration tests, compiles the Python sources, and executes the existing public production smoke gate.
