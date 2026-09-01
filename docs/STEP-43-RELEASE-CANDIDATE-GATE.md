# BuildCost Pro — STEP 43 Release Candidate Gate

## Scope
STEP 43 prepares the V1.2 release candidate without declaring production release. The locked roadmap requires release-scope freeze, database migration rehearsal, build/container verification, CI/CD verification, staging smoke validation, and a documented production rollback plan.

## Release scope freeze
The V1.2 release candidate is frozen to the completed STEP 31–42 implementation and verification scope. No new feature work is admitted during RC validation unless it is a release-blocking fix and is revalidated from the resulting commit.

## Required gates
- [x] Release scope and acceptance criteria are recorded.
- [x] Database migration rehearsal uses a fresh PostgreSQL 16 database and applies all checked-in migrations in order.
- [x] Production application import and Python compilation are part of RC validation.
- [x] Production container build verification is part of RC validation.
- [x] CI/CD verification is required on the final RC commit.
- [x] Staging-equivalent runtime smoke validation is performed against the production-shaped container/runtime contract.
- [x] Production public health/runtime smoke remains mandatory.
- [x] Production rollback plan is documented separately.
- [ ] Final STEP 43 gate: all RC checks must be SUCCESS for the same final release-candidate commit.

## Migration rehearsal
The RC workflow provisions an isolated PostgreSQL 16 service and applies the complete checked-in migration chain to an empty database. This is a rehearsal of the release migration path; it does not modify the production database.

## Container verification
The repository root `Dockerfile` is the production container definition. RC validation builds the image from the frozen commit and starts a local staging-equivalent container for the public health contract.

## Rollback
See `docs/STEP-43-RELEASE-CANDIDATE-ROLLBACK.md`. Production rollback is a deployment rollback first; database rollback is not assumed safe for destructive migrations. Any production migration requiring rollback must have an explicitly tested forward-fix or restore path before release approval.

## Gate rule
`IMPLEMENTED` != `DONE`. STEP 43 becomes DONE only after the final RC commit passes CI, migration rehearsal, container/build validation, staging-equivalent smoke validation, production runtime checks, and the documented release rollback readiness checks.
