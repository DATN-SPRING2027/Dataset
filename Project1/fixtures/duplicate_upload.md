---
document_id: "DOC-PAY-ADR-003"
title: "ADR-003: Payment Orchestration and Idempotency"
project_id: "NSC-PAY"
organization_id: "ORG-NSC"
scope: "project"
owner_id: "M-006"
created_at: "2026-08-19"
updated_at: "2026-08-19"
version: "3.0"
status: "Approved"
classification: "Restricted"
access_groups: ["GRP-PAYMENT", "GRP-PULSEPAY"]
source_issue_keys: ["PAY-001", "PAY-002", "PAY-003"]
canonical_document_id: "DOC-PAY-ADR-003"
rendition_paths: []
requirement_ids: []
file_path: "documents/markdown/formal/Payment_Orchestration_ADR_v3.md"
format: "markdown"
synthetic: true
---

# ADR-003: Payment Orchestration and Idempotency

Active architectural decision governing payment idempotency, provider retries, webhook inbox deduplication, and PCI boundaries.

## Architectural Decision

Persist merchant-scoped idempotency keys in PostgreSQL for at least 72 hours. An identical key with an identical payload hash returns the original cached response. A matching key with a differing payload returns HTTP 409 Conflict.

## Provider Retry Policy

Retry transient network connectivity errors and HTTP 5xx responses using exponential backoff with full jitter. Maximum 5 retry attempts spanning 20 minutes. Hard payment declines (HTTP 4xx) must never be retried.

## Webhook Deduplication Protocol

Upon receipt of a PulsePay webhook, verify HMAC-SHA256 signature, insert (merchant_id, provider_event_id) into a unique inbox table within a database transaction, then apply state transitions. Replays are acknowledged with HTTP 200 without executing side effects.

## Security & PCI Invariants

Only provider payment tokens, authorization codes, and minimal transaction metadata are persisted. Storing credit card PAN or CVV is strictly prohibited. Refund policies adhere to DOC-ORD-POL-005.

## Version Lineage

Supersedes DOC-PAY-ADR-001. The old decision remains available for historical audit and conflict testing.
