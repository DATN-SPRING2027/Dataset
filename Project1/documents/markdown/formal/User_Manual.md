---
document_id: "DOC-ORG-USER-MAN-001"
title: "Northstar Commerce User Manual"
project_id: null
organization_id: "ORG-NSC"
scope: "organization"
owner_id: "M-016"
created_at: "2026-10-12"
updated_at: "2026-10-12"
version: "1.0"
status: "Approved"
classification: "Internal"
access_groups: ["GRP-ALL-STAFF"]
source_issue_keys: ["CAT-008", "ORD-001"]
canonical_document_id: "DOC-ORG-USER-MAN-001"
rendition_paths: []
requirement_ids: []
file_path: "documents/markdown/formal/User_Manual.md"
format: "markdown"
synthetic: true
---

# Northstar Commerce User Manual

Role-based operating guide for shoppers, merchant administrators, support staff, and platform operators.

## Shopper workflow

Browse or search products, refine results with facets, review the cart total and coupon explanation, enter shipping details, and submit checkout once. If payment is pending, keep the reference number and do not submit a new payment; refresh the order status or contact support.

## Merchant administrator workflow

Sign in with the Meridian tenant account, upload the approved CSV template, review row-level errors, correct invalid rows, preview the catalog, and publish after approval. Manage promotions with a start/end window and usage limit. Review orders and returns only within the merchant tenant.

## Customer support workflow

Search by synthetic order ID, confirm tenant and caller authorization, review payment and fulfillment timeline, and explain pending states without exposing payment tokens. Cancellation is available before packing; after packing, guide the customer to the return flow.

## Platform operator workflow

Use least-privilege operational access, inspect service health and alerts, follow the linked runbook, and record every privileged action. Never paste secrets, full payment payloads, or customer personal data into support notes.

## Common errors and accessibility

A 409 indicates a conflicting retry key or stale version; do not generate a new key until the original outcome is resolved. A 422 indicates input validation details. Forms provide labels and actionable errors; keyboard focus remains visible. Escalate suspected tenant mismatch or payment duplication immediately.
