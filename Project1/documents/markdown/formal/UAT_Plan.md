---
document_id: "DOC-ORG-UAT-PLAN-001"
title: "Northstar Commerce User Acceptance Test Plan"
project_id: null
organization_id: "ORG-NSC"
scope: "organization"
owner_id: "M-002"
created_at: "2026-10-12"
updated_at: "2026-10-12"
version: "1.0"
status: "Approved"
classification: "Customer Restricted"
access_groups: ["GRP-MERIDIAN", "GRP-LEADERS"]
source_issue_keys: ["CAT-008", "CHKO-005", "ORD-001"]
canonical_document_id: "DOC-ORG-UAT-PLAN-001"
rendition_paths: []
requirement_ids: []
file_path: "documents/markdown/formal/UAT_Plan.md"
format: "markdown"
synthetic: true
---

# Northstar Commerce User Acceptance Test Plan

Merchant and partner acceptance scenarios, prerequisites, evidence, and decision rules for the synthetic pilot.

## Participants and roles

Meridian participants validate merchandising, shopper purchase, order support, cancellation, and returns. PulsePay validates webhook delivery and reconciliation in its sandbox. Northstar Product, QA, Security, and Operations observe and record evidence.

## Scenarios and prerequisites

UAT covers importing the approved sample catalog, searching within the merchant tenant, applying an eligible coupon, placing an order, retrying a timed-out checkout, reviewing inventory reservation, receiving a shipment event, and initiating an eligible return/refund. Test identities and seeded records are synthetic and reset before each run.

## Acceptance rules

A scenario passes only when the participant completes the expected business outcome, sees understandable validation, and confirms no foreign-tenant data is exposed. Financial totals and refund status must reconcile. Defects are recorded with severity and linked issue.

## Decision and sign-off

Merchant owner records Accept, Accept with Conditions, or Reject per scenario. Any exception identifies impact, workaround, owner, expiry, and retest date. UAT cannot waive a critical security or duplicate-payment defect.
