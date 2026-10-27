---
document_id: "DOC-PAY-ANNEX-001"
title: "Payment Orchestration Project Annex"
project_id: "NSC-PAY"
organization_id: "ORG-NSC"
scope: "project"
owner_id: "M-006"
created_at: "2026-10-12"
updated_at: "2026-10-12"
version: "1.0"
status: "Approved"
classification: "Internal"
access_groups: ["GRP-PAYMENT"]
source_issue_keys: ["PAY-001", "PAY-002", "PAY-003"]
canonical_document_id: "DOC-PAY-ANNEX-001"
rendition_paths: []
requirement_ids: ["FR-PAY-001", "FR-PAY-002", "FR-PAY-003", "FR-PAY-004", "FR-PAY-005", "FR-PAY-006", "FR-PAY-007", "FR-PAY-008"]
file_path: "documents/markdown/formal/project-annexes/NSC-PAY_Project_Annex.md"
format: "markdown"
synthetic: true
---

# Payment Orchestration Project Annex

Scope, requirements, ownership, dependencies, acceptance, and operational boundary for Payment Orchestration

## Objective and boundary

Integrate PulsePay safely with durable idempotency, signed webhooks, retry controls, and auditable refunds. Owns payment intents, provider adapter, webhook inbox, retry state, and refund orchestration. Checkout owns the shopper-facing session; PulsePay owns its external settlement platform.

## Requirements and acceptance

This annex implements eight approved project requirements. The IDs and exact acceptance criteria are generated from structured/requirements.jsonl and linked in the RTM. The workstream owner must approve any scope change before the Jira baseline is updated.

## Data and service contracts

Owned data: PaymentIntent, ProviderAttempt, WebhookInbox, Refund, SettlementReference, PayloadDigest. Integrations: PulsePay sandbox/API, Checkout saga, Orders ledger, secret manager, operational alerts. All tenant-owned records and events carry explicit tenant scope and correlation IDs.

## Invariants and failure handling

Verify HMAC before processing; deduplicate by merchant and provider event ID in a transaction; never store PAN/CVV; retry only transient failures with bounded jitter; refunds cannot exceed captured balance. Failures are surfaced with stable error codes, trace IDs, and a recovery path; retries are bounded and must not duplicate side effects.

## Dependencies and delivery

The workstream depends on shared identity, API gateway, event envelope, observability, and release controls. Jira source issues: PAY-001, PAY-002, PAY-003. Delivery follows two-week sprints and the release gate in the PMP.

## Acceptance measures

Zero duplicate captures in replay testing; signature failures are rejected and audited; provider timeout backlog is reconciled within the agreed recovery window.

## Requirement IDs and verification

| Requirement | Priority | Statement | Acceptance criteria | Jira source | Test cases |
| --- | --- | --- | --- | --- | --- |
| FR-PAY-001 | High | Persist merchant-scoped idempotency records for at least 72 hours | Same key and payload hash returns the original result; different payload hash returns a conflict. | PAY-001, PAY-002, PAY-003 | FT-PAY-001 |
| FR-PAY-002 | High | Verify PulsePay HMAC-SHA256 signatures before accepting webhook events | Invalid, missing, or stale signatures are rejected without changing payment state. | PAY-001, PAY-002, PAY-003 | FT-PAY-002 |
| FR-PAY-003 | Medium | Deduplicate webhook event IDs atomically before applying side effects | A repeated provider event returns 200 and changes the ledger exactly once. | PAY-001, PAY-002, PAY-003 | FT-PAY-003 |
| FR-PAY-004 | Medium | Retry only transient network and provider 5xx failures with bounded jitter | Retries stop after five attempts or twenty minutes; hard 4xx declines are not retried. | PAY-001, PAY-002, PAY-003 | FT-PAY-004 |
| FR-PAY-005 | Medium | Prevent sensitive cardholder data from entering persistent stores or logs | PAN/CVV are rejected/redacted and absent from database, traces, analytics, and exported fixtures. | PAY-001, PAY-002, PAY-003 | FT-PAY-005 |
| FR-PAY-006 | High | Enforce refund ceiling against captured amount minus settled refunds | Over-refund attempts fail before provider submission and do not mutate balances. | PAY-001, PAY-002, PAY-003 | FT-PAY-006 |
| FR-PAY-007 | High | Reconcile uncertain provider outcomes without creating a second capture | A timeout remains pending until provider lookup or webhook resolution records a single terminal state. | PAY-001, PAY-002, PAY-003 | FT-PAY-007 |
| FR-PAY-008 | Medium | Restrict partner access to payment contracts explicitly shared with PulsePay | PulsePay users can access approved integration docs but not general employee or merchant data. | PAY-001, PAY-002, PAY-003 | FT-PAY-008 |
