# BuildCost Pro — Excel Test / Import Specification

## Purpose
Define the canonical Excel structure used to test BuildCost Pro calculations, data validation, import/export mapping, and reconciliation before production release.

## Rule
Excel is a test/import/export interface. It is not the system-of-record database.

## Workbook
Recommended workbook: `BuildCost-Pro-Test-Template.xlsx`

### Sheets
1. `README` — instructions, version, sample workflow
2. `Projects` — project master/test records
3. `BOQ` — BOQ headers and estimate lines
4. `Budget` — approved budget by category
5. `Costs` — actual costs/expenses
6. `Transactions` — income, expense, adjustment, payment records
7. `Suppliers` — supplier master/test records
8. `Procurement` — PR/RFQ/PO/receiving test records
9. `Documents` — document and receipt references
10. `Users` — role/permission test matrix (non-production sample data only)
11. `Expected_Results` — expected totals and reconciliation checks
12. `Lookup` — controlled values such as status, category, unit, payment type

## Canonical relationships
`Projects.project_id` links to project-owned records.
`BOQ.project_id` and `Budget.project_id` link estimates and budget.
`Costs.project_id` and `Transactions.project_id` link actual financial activity.
`Procurement.project_id` links purchasing commitments.
`Documents.project_id` links evidence files/receipts.

## Minimum validation
- Required IDs are unique.
- Foreign keys reference an existing parent record.
- Dates use ISO-compatible dates.
- Money fields are numeric and non-negative unless the transaction type explicitly permits a reversal/adjustment.
- Quantity and rate are numeric.
- Currency is explicit.
- Status values come from `Lookup`.
- Duplicate import rows are detected.
- Totals reconcile with the application after import.

## Calculation checks
At minimum validate:
- BOQ amount = quantity × rate
- Budget remaining = approved budget − actual cost − committed amount, according to the application's accounting rule
- Project total cost = sum of accepted cost records
- Income − cost = project gross result where applicable
- Imported totals match application totals within the defined rounding policy

## Test workflow
1. Populate sample workbook.
2. Validate workbook.
3. Import into a non-production/test project.
4. Compare application values against `Expected_Results`.
5. Export application data.
6. Reconcile exported data back to workbook.
7. Record pass/fail evidence.

## Security
Never place production passwords, API keys, tokens, payment secrets, or sensitive personal information in the test workbook.

## Versioning
Changes to column names, types, relationships, or calculations require a specification version update and regression test.
