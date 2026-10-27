---
document_id: "DOC-INV-ANNEX-001"
title: "Inventory & Fulfillment Project Annex"
project_id: "NSC-INV"
organization_id: "ORG-NSC"
scope: "project"
owner_id: "M-007"
created_at: "2026-10-12"
updated_at: "2026-10-12"
version: "1.0"
status: "Approved"
classification: "Internal"
access_groups: ["GRP-INVENTORY"]
source_issue_keys: ["INV-001", "INV-002", "INV-003"]
canonical_document_id: "DOC-INV-ANNEX-001"
rendition_paths: []
requirement_ids: ["FR-INV-001", "FR-INV-002", "FR-INV-003", "FR-INV-004", "FR-INV-005", "FR-INV-006", "FR-INV-007", "FR-INV-008"]
file_path: "documents/markdown/formal/project-annexes/NSC-INV_Project_Annex.md"
format: "markdown"
synthetic: true
---

# Inventory & Fulfillment Project Annex

Scope, requirements, ownership, dependencies, acceptance, and operational boundary for Inventory & Fulfillment

## Objective and boundary

Provide accurate available-to-promise inventory and short-lived reservations that prevent overselling. Owns stock balances, warehouse locations, safety buffers, reservation leases, and adjustment audit. Orders owns shipment lifecycle.

## Requirements and acceptance

This annex implements eight approved project requirements. The IDs and exact acceptance criteria are generated from structured/requirements.jsonl and linked in the RTM. The workstream owner must approve any scope change before the Jira baseline is updated.

## Data and service contracts

Owned data: StockLedger, WarehouseBalance, Reservation, SafetyStockRule, InventoryAdjustment, AvailabilitySnapshot. Integrations: Catalog variants, Checkout reservation/release API, warehouse import adapter, order shipment events, operations metrics. All tenant-owned records and events carry explicit tenant scope and correlation IDs.

## Invariants and failure handling

ATP = on-hand - allocated reserves - safety buffer; mutations are atomic; reservations expire and release idempotently; negative stock is not silently accepted. Failures are surfaced with stable error codes, trace IDs, and a recovery path; retries are bounded and must not duplicate side effects.

## Dependencies and delivery

The workstream depends on shared identity, API gateway, event envelope, observability, and release controls. Jira source issues: INV-001, INV-002, INV-003. Delivery follows two-week sprints and the release gate in the PMP.

## Acceptance measures

No oversell in concurrent reservation tests; expired holds release within one worker interval; adjustments reconcile to the immutable ledger.

## Requirement IDs and verification

| Requirement | Priority | Statement | Acceptance criteria | Jira source | Test cases |
| --- | --- | --- | --- | --- | --- |
| FR-INV-001 | High | Calculate ATP from on-hand, allocated reservations, and safety buffer | The returned quantity equals the documented formula and is never below zero for sellable availability. | INV-001, INV-002, INV-003 | FT-INV-001 |
| FR-INV-002 | High | Reserve available units atomically for a checkout session | Concurrent requests cannot reserve more than eligible ATP. | INV-001, INV-002, INV-003 | FT-INV-002 |
| FR-INV-003 | Medium | Expire and release unconfirmed reservations idempotently | A repeated expiry event releases quantity once and records the reason. | INV-001, INV-002, INV-003 | FT-INV-003 |
| FR-INV-004 | Medium | Scope stock balances and reservations by merchant, SKU, and warehouse | Identical SKU strings in different merchant or warehouse scopes do not share balances. | INV-001, INV-002, INV-003 | FT-INV-004 |
| FR-INV-005 | Medium | Reject unauthorized or unbalanced manual adjustments | An adjustment requires an active authorized actor, reason code, and before/after ledger entry. | INV-001, INV-002, INV-003 | FT-INV-005 |
| FR-INV-006 | High | Apply safety-stock thresholds to buyable availability | Units at or below the configured buffer are not promised to new checkouts. | INV-001, INV-002, INV-003 | FT-INV-006 |
| FR-INV-007 | High | Support safe reconciliation imports with row-level errors | Invalid rows are quarantined with source line and do not corrupt valid balances. | INV-001, INV-002, INV-003 | FT-INV-007 |
| FR-INV-008 | Medium | Emit availability changes with monotonic versions | Consumers can discard stale events and identify the newest snapshot. | INV-001, INV-002, INV-003 | FT-INV-008 |
