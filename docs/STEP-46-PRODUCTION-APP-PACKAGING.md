# STEP 46 — Production App Packaging

**Purpose:** establish a repeatable production packaging gate for the BuildCost Pro web and API applications after STEP 45.

## Scope

- Validate production packaging inputs and deployment configuration.
- Build the Next.js web application with the production build command.
- Build the production API container and validate its runtime contract.
- Verify Railway healthcheck contracts for Web and API.
- Produce a CI evidence bundle as a GitHub Actions artifact.

## Gate

STEP 46 is **PASS** only when the dedicated `step46-production-packaging.yml` workflow completes successfully and the `step46-production-package` artifact is uploaded.

`IMPLEMENTED` is not equivalent to `DONE`; the implementation tracker must only be advanced after the CI gate has passed.

## Current packaging contracts

### Web

- Build: `npm install && npm run build`
- Start: `npm run start`
- Railway healthcheck: `/api/health`

### API

- Production container: `apps/api/Dockerfile`
- Railway healthcheck: `/health`
- Runtime command includes migration and Uvicorn startup.

## Evidence

The workflow records build/package validation in the Actions log and uploads `step46-production-package.tgz` containing the production web build output and packaging configuration.
