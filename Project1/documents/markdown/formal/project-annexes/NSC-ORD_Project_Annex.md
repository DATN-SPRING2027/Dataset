---
document_id: "DOC-ORD-ANNEX-001"
title: "Orders, Returns & Refunds Project Annex"
project_id: "NSC-ORD"
organization_id: "ORG-NSC"
scope: "project"
owner_id: "M-008"
created_at: "2026-10-12"
updated_at: "2026-10-12"
version: "1.0"
status: "Approved"
classification: "Internal"
access_groups: ["GRP-ORDERS"]
source_issue_keys: ["ORD-001", "ORD-002", "ORD-003"]
canonical_document_id: "DOC-ORD-ANNEX-001"
rendition_paths: []
requirement_ids: ["FR-ORD-001", "FR-ORD-002", "FR-ORD-003", "FR-ORD-004", "FR-ORD-005", "FR-ORD-006", "FR-ORD-007", "FR-ORD-008"]
file_path: "documents/markdown/formal/project-annexes/NSC-ORD_Project_Annex.md"
format: "markdown"
synthetic: true
---

# Orders, Returns & Refunds Project Annex

Scope, requirements, ownership, dependencies, acceptance, and operational boundary for Orders, Returns & Refunds

## Objective and boundary

Maintain an auditable order lifecycle from placement through fulfillment, cancellation, return, and refund settlement. Owns order state, immutable purchase snapshots, shipment/return records, and refund coordination. Payment owns provider authorization and settlement events.

## Requirements and acceptance

This annex implements eight approved project requirements. The IDs and exact acceptance criteria are generated from structured/requirements.jsonl and linked in the RTM. The workstream owner must approve any scope change before the Jira baseline is updated.

## Data and service contracts

Owned data: Order, OrderLineSnapshot, Shipment, ReturnAuthorization, RefundRequest, OrderEvent. Integrations: Checkout order placement, Inventory fulfillment events, carrier adapter, Payment refund and settlement events, merchant support console. All tenant-owned records and events carry explicit tenant scope and correlation IDs.

## Invariants and failure handling

Transitions follow the state machine; customer cancellation is disabled after packing; return window is 30 days after delivery for Meridian; refund is complete only after settlement confirmation. Failures are surfaced with stable error codes, trace IDs, and a recovery path; retries are bounded and must not duplicate side effects.

## Dependencies and delivery

The workstream depends on shared identity, API gateway, event envelope, observability, and release controls. Jira source issues: ORD-001, ORD-002, ORD-003. Delivery follows two-week sprints and the release gate in the PMP.

## Acceptance measures

Every order has a traceable terminal or active state; duplicate fulfillment and refund events are idempotent; financial totals reconcile to the payment ledger.

## Requirement IDs and verification

| Requirement | Priority | Statement | Acceptance criteria | Jira source | Test cases |
| --- | --- | --- | --- | --- | --- |
| FR-ORD-001 | High | Persist immutable item, price, tax, and address snapshots at order placement | Later catalog or address edits do not change the historical order view. | ORD-001, ORD-002, ORD-003 | FT-ORD-001 |
| FR-ORD-002 | High | Enforce valid order state transitions with actor and timestamp | Invalid transitions return a stable error and append no state event. | ORD-001, ORD-002, ORD-003 | FT-ORD-002 |
| FR-ORD-003 | Medium | Allow customer cancellation only before warehouse packing begins | PENDING/AUTHORIZED orders may cancel; PACKED orders require the return workflow. | ORD-001, ORD-002, ORD-003 | FT-ORD-003 |
| FR-ORD-004 | Medium | Open Meridian return requests within 30 days of carrier delivery | The service uses delivered_at in UTC and rejects requests outside the configured window. | ORD-001, ORD-002, ORD-003 | FT-ORD-004 |
| FR-ORD-005 | Medium | Calculate partial refunds without exceeding remaining captured balance | Previously settled refunds reduce the remaining refundable amount before submission. | ORD-001, ORD-002, ORD-003 | FT-ORD-005 |
| FR-ORD-006 | High | Mark a refund complete only after provider settlement confirmation | A request or authorization alone remains pending until the settlement event arrives. | ORD-001, ORD-002, ORD-003 | FT-ORD-006 |
| FR-ORD-007 | High | Deduplicate repeated shipment, return, and refund events | Duplicate event IDs do not repeat inventory or financial side effects. | ORD-001, ORD-002, ORD-003 | FT-ORD-007 |
| FR-ORD-008 | Medium | Restrict order and customer-support records to authorized tenant roles | Merchant users and support agents only see orders allowed by tenant and role policy. | ORD-001, ORD-002, ORD-003 | FT-ORD-008 |
