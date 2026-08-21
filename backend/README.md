# BuildCost Pro Backend

NestJS modular backend with PostgreSQL + Prisma.

## Layers
- Data Access: PrismaService + repositories
- Application: ProjectService + FinancialService
- API: REST controllers under `/api/v1`

## Endpoints
- `GET/POST /api/v1/projects`
- `GET/PATCH /api/v1/projects/:id`
- `GET/POST /api/v1/projects/:projectId/transactions`
- `GET/POST /api/v1/projects/:projectId/costs`
- `GET/POST /api/v1/projects/:projectId/budgets`

## Run
1. Copy `.env.example` to `.env` and configure PostgreSQL.
2. `npm install`
3. `npx prisma generate`
4. `npx prisma migrate deploy`
5. `npm run start:dev`
