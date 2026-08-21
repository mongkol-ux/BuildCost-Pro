# BuildCost Pro V1.0 — Production Deployment

## Runtime

- Platform: Railway
- Service root: repository root
- Dockerfile: `apps/api/Dockerfile`
- Health check: `GET /health`
- Database: Railway PostgreSQL

## Required production variables

- `BUILD_COST_ENVIRONMENT=production`
- `BUILD_COST_DATABASE_URL=<Railway PostgreSQL connection URL>`
- `BUILD_COST_JWT_SECRET=<random secret, 32+ characters>`
- `BUILD_COST_ALLOWED_HOSTS=<generated Railway hostname>`
- `BUILD_COST_CORS_ORIGINS=<frontend origin>`

Never commit production secrets to Git.
