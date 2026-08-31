# STEP 29 — Post-V1.1 Production Hardening / Application Completion

**Project:** BuildCost Pro  
**Repository:** `mongkol-ux/BuildCost-Pro`  
**Branch:** `main`  
**Date:** 2026-08-31

## Objective

Harden the V1.1 application after core implementation, align production health monitoring with the deployed web application, and establish the production-completion gate before entering the next product-development phase.

## Baseline

STEP 27 delivered the authenticated V1.1 core application and primary project-cost workflow. The implementation is documented in `docs/STEP-27-V1.1-CORE-APPLICATION-DEVELOPMENT.md` and was committed in `4c03c095184ab6172ed4be0576f23f631b32b5af`.

## STEP 29 hardening completed

- Confirmed the current production web application exposes `GET /api/health` with service `buildcost-pro-web` and version `1.1.0`.
- Confirmed the API service separately exposes `GET /health` with service `buildcost-pro-api` and version `1.0.0`.
- Corrected the production operations workflow so the public production web monitor checks the web application's actual health endpoint instead of incorrectly calling `/health` on the web URL.
- Preserved production security-header assertions for `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, and HSTS.
- Kept the API production health contract intact; the API Railway configuration continues to use `/health` as its service healthcheck.

## Evidence

Web health endpoint: `apps/web/app/api/health/route.ts`  
API health endpoint: `apps/api/src/main.py`  
Web deployment configuration: `apps/web/railway.toml`  
API deployment configuration: `apps/api/railway.toml`  
Production monitor: `.github/workflows/production-ops-health.yml`

## Verification note

Before this correction, the scheduled production monitor was failing because it requested `/health` from the public web deployment and received HTTP 404. The failing run was GitHub Actions run `33373317521` on 2026-08-31. The failure was an observability/configuration mismatch, not evidence that the API `/health` contract was broken.

The corrected monitor now targets `/api/health` on the public V1.1 web deployment. A successful post-change workflow run is required as the final runtime evidence for the STEP 29 production-health gate.

## STEP 29 completion gate

STEP 29 is complete when:

1. The corrected production monitor is committed to `main`.
2. The post-change GitHub Actions production-health run succeeds.
3. V1.1 web health and security-header checks pass.
4. No known blocker remains in the V1.1 core application journey from STEP 27.
5. The repository contains explicit evidence for the transition to the next step.

## Next step

**STEP 30 — V1.2 Product Expansion / Advanced Application Modules**

STEP 30 begins only after STEP 29 runtime verification is green. It is the next controlled development phase for expanding BuildCost Pro beyond the V1.1 core application while keeping the Master Document and verified API contracts as the source of truth.
