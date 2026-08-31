# STEP 30 — V1.2 Product Expansion / Advanced Application Modules

**Project:** BuildCost Pro  
**Repository:** `mongkol-ux/BuildCost-Pro`  
**Branch:** `main`  
**Status:** READY TO START — gated by STEP 29 runtime verification

## Objective

Expand BuildCost Pro beyond the V1.1 core application into the next controlled product-development phase, without changing the approved architecture or silently changing business rules.

## Entry condition

STEP 29 must have a green post-change production-health verification. The repository already contains the STEP 29 hardening changes and closure evidence; runtime verification remains the gate.

## Scope framework

STEP 30 will be executed in controlled sub-steps covering:

1. Product scope and module prioritization.
2. API contract expansion required by approved V1.2 functionality.
3. Application navigation and module shell expansion.
4. BOQ / estimating expansion.
5. Materials, labor, equipment and supplier workflows.
6. Procurement and transaction workflows.
7. Reporting, dashboard and analytics expansion.
8. Documents, workflow and notification integration.
9. Search and discovery integration.
10. Security, QA, regression and production verification.
11. Release evidence and V1.2 acceptance preparation.

## Engineering rule

Every V1.2 change must preserve the BuildCost Pro Master Document as the source of truth, reuse verified contracts where applicable, add tests for changed behavior, and produce explicit evidence before release.

## Current state

V1.1 core application implementation is complete from STEP 27. STEP 29 corrected the production web health-monitoring mismatch and established the final hardening gate. STEP 30 is therefore prepared as the next development phase, but production acceptance must not be marked complete until the post-change runtime check is green.

## First action

Begin with **STEP 30-A — V1.2 Scope Lock & Application Module Map**, using the current repository as the implementation baseline.
