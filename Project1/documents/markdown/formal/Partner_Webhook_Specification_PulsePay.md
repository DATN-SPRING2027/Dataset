---
document_id: "DOC-INT-PULSEPAY-002"
title: "Partner Webhook Specification: PulsePay Network"
project_id: "NSC-PAY"
organization_id: "ORG-NSC"
scope: "project"
owner_id: "M-017"
created_at: "2026-05-22"
updated_at: "2026-05-22"
version: "2.2"
status: "Approved"
classification: "Restricted"
access_groups: ["GRP-PULSEPAY", "GRP-PAYMENT"]
source_issue_keys: ["PAY-008", "PAY-010"]
canonical_document_id: "DOC-INT-PULSEPAY-002"
rendition_paths: []
requirement_ids: []
file_path: "documents/markdown/formal/Partner_Webhook_Specification_PulsePay.md"
format: "markdown"
synthetic: true
---

# Partner Webhook Specification: PulsePay Network

Technical webhook specifications, payload contracts, signature verification, and replay policies for PulsePay.

## Webhook Delivery Rules

PulsePay delivers JSON events via HTTPS POST with header 'X-PulsePay-Signature' containing HMAC-SHA256 signature.

## Retry Intervals

PulsePay retries failed endpoints (non-2xx) at 1m, 5m, 15m, 1h, 6h, and 24h intervals.
