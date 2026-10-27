---
document_id: "DOC-CHKO-ANNEX-001"
title: "Checkout Experience Project Annex"
project_id: "NSC-CHKO"
organization_id: "ORG-NSC"
scope: "project"
owner_id: "M-005"
created_at: "2026-10-12"
updated_at: "2026-10-12"
version: "1.0"
status: "Approved"
classification: "Internal"
access_groups: ["GRP-CHECKOUT"]
source_issue_keys: ["CHKO-002", "CHKO-003", "CHKO-005"]
canonical_document_id: "DOC-CHKO-ANNEX-001"
rendition_paths: []
requirement_ids: ["FR-CHKO-001", "FR-CHKO-002", "FR-CHKO-003", "FR-CHKO-004", "FR-CHKO-005", "FR-CHKO-006", "FR-CHKO-007", "FR-CHKO-008"]
file_path: "documents/markdown/formal/project-annexes/NSC-CHKO_Project_Annex.md"
format: "markdown"
synthetic: true
---

# Checkout Experience Project Annex

Scope, requirements, ownership, dependencies, acceptance, and operational boundary for Checkout Experience

## Objective and boundary

Convert an accepted cart into one auditable order while handling retries, stock holds, tax quotes, and provider uncertainty safely. Coordinates Cart, Inventory, Payment, and Orders. It owns checkout sessions and the order-placement saga, not provider settlement ledgers.

## Requirements and acceptance

This annex implements eight approved project requirements. The IDs and exact acceptance criteria are generated from structured/requirements.jsonl and linked in the RTM. The workstream owner must approve any scope change before the Jira baseline is updated.

## Data and service contracts

Owned data: CheckoutSession, AddressSnapshot, TaxQuote, IdempotencyRecord, OrderPlacementAttempt, ReconciliationReference. Integrations: Cart calculation API, Inventory reservation API, tax quote adapter, PulsePay authorization API, Orders API, event bus. All tenant-owned records and events carry explicit tenant scope and correlation IDs.

## Invariants and failure handling

Idempotency keys are durable for at least 72 hours; same key and payload returns the same result; changed payload returns 409; uncertain provider outcomes are reconciled, never blindly resubmitted. Failures are surfaced with stable error codes, trace IDs, and a recovery path; retries are bounded and must not duplicate side effects.

## Dependencies and delivery

The workstream depends on shared identity, API gateway, event envelope, observability, and release controls. Jira source issues: CHKO-002, CHKO-003, CHKO-005. Delivery follows two-week sprints and the release gate in the PMP.

## Acceptance measures

No duplicate order or capture in retry tests; checkout p95 below 1.5 seconds excluding an upstream timeout; unresolved provider outcomes are visible within one minute.

## Requirement IDs and verification

| Requirement | Priority | Statement | Acceptance criteria | Jira source | Test cases |
| --- | --- | --- | --- | --- | --- |
| FR-CHKO-001 | High | Create a checkout session from an active tenant-bound cart | The session snapshots accepted cart lines, price version, currency, and shipping address. | CHKO-002, CHKO-003, CHKO-005 | FT-CHKO-001 |
| FR-CHKO-002 | High | Require durable idempotency for order-placement mutations | An exact replay within 72 hours returns the original order/session response. | CHKO-002, CHKO-003, CHKO-005 | FT-CHKO-002 |
| FR-CHKO-003 | Medium | Reject reuse of an idempotency key with a different payload | The API returns HTTP 409 IDEMPOTENCY_CONFLICT and performs no additional side effect. | CHKO-002, CHKO-003, CHKO-005 | FT-CHKO-003 |
| FR-CHKO-004 | Medium | Reserve stock atomically before final order confirmation | The checkout saga compensates the reservation if payment authorization definitively fails. | CHKO-002, CHKO-003, CHKO-005 | FT-CHKO-004 |
| FR-CHKO-005 | Medium | Return a pending reconciliation response for uncertain provider timeouts | The API returns HTTP 202 with a stable reconciliation reference and does not create another payment attempt on replay. | CHKO-002, CHKO-003, CHKO-005 | FT-CHKO-005 |
| FR-CHKO-006 | High | Validate address, tax quote, currency, and cart freshness before submission | Invalid or expired inputs return field-level errors before reservation or authorization. | CHKO-002, CHKO-003, CHKO-005 | FT-CHKO-006 |
| FR-CHKO-007 | High | Persist a single order despite duplicate and concurrent submit requests | Concurrent requests sharing an idempotency key produce one order identifier and one financial authorization. | CHKO-002, CHKO-003, CHKO-005 | FT-CHKO-007 |
| FR-CHKO-008 | Medium | Emit correlated state transitions for support and audit | Every saga step includes session, order, tenant, idempotency, and correlation identifiers. | CHKO-002, CHKO-003, CHKO-005 | FT-CHKO-008 |
