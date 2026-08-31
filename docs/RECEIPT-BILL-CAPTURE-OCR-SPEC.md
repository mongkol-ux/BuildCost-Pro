# BuildCost Pro — Receipt / Bill Photo Capture & OCR Specification

## Purpose
Define the production workflow for capturing receipts/bills by camera or image upload, extracting data with OCR, validating the result, and creating an auditable cost/expense record.

## User flow
`Camera / Upload → Image Quality Check → OCR → Field Extraction → User Review → Save Expense → Link Project/BOQ/Category → Store Evidence → Audit Trail`

## Capture
- Camera capture on mobile.
- Gallery/file upload where supported.
- Support common receipt/document image formats.
- Crop, rotate, and retake when image quality is insufficient.
- Preserve the original image as evidence; processed images are derivatives.

## OCR fields
The extraction model should attempt:
- supplier/vendor name
- tax/VAT ID when present
- receipt/invoice number
- document date
- due date when present
- line-item description
- quantity
- unit
- unit price
- discount
- subtotal
- VAT/tax
- withholding tax when applicable
- total amount
- currency
- payment method when detectable

## Confidence and review
Each extracted field should carry a confidence/result state. Low-confidence or missing critical fields must be highlighted for user review. The system must not silently create a final accounting record from uncertain OCR data.

## Expense mapping
After user confirmation, map the receipt to:
- project
- BOQ item when applicable
- cost category
- supplier
- payment/transaction type
- cost date
- amount and tax components

## Evidence and audit
Store:
- original image reference
- processed image reference if used
- OCR result/version
- extracted structured fields
- user corrections
- final saved record ID
- creator and timestamps

Do not overwrite the original evidence after capture.

## Duplicate detection
Use document number, supplier, date, amount, image fingerprint and related project context where available to warn about likely duplicate receipts before final save.

## Error handling
Provide clear states for:
- unreadable image
- unsupported format
- OCR unavailable
- partial extraction
- conflicting totals
- duplicate candidate
- missing project/category
- save failure

## Privacy and security
Receipt images may contain sensitive financial or personal information. Apply authenticated access, project-level authorization, secure storage, controlled retention, audit logging, and no exposure through public URLs.

## Implementation phases
- STEP 31–40: data model, document references, expense integration and contracts.
- STEP 41–42: end-to-end integration and UAT.
- STEP 43–45: production readiness and evidence validation.
- STEP 47–48: mobile camera UX and final UX/UI.
- STEP 50: security/privacy audit.

## Definition of Done
A receipt is considered successfully captured only when the original evidence is safely stored, OCR data is reviewable, the user confirms the extracted financial values, the expense is linked to the correct project/cost context, and the complete audit trail is retained.
