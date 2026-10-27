---
document_id: "DOC-CART-ANNEX-001"
title: "Cart & Promotions Project Annex"
project_id: "NSC-CART"
organization_id: "ORG-NSC"
scope: "project"
owner_id: "M-005"
created_at: "2026-10-12"
updated_at: "2026-10-12"
version: "1.0"
status: "Approved"
classification: "Internal"
access_groups: ["GRP-CART"]
source_issue_keys: ["CART-001", "CART-002", "CART-003"]
canonical_document_id: "DOC-CART-ANNEX-001"
rendition_paths: []
requirement_ids: ["FR-CART-001", "FR-CART-002", "FR-CART-003", "FR-CART-004", "FR-CART-005", "FR-CART-006", "FR-CART-007", "FR-CART-008"]
file_path: "documents/markdown/formal/project-annexes/NSC-CART_Project_Annex.md"
format: "markdown"
synthetic: true
---

# Cart & Promotions Project Annex

Scope, requirements, ownership, dependencies, acceptance, and operational boundary for Cart & Promotions

## Objective and boundary

Calculate a transparent, repeatable cart total while enforcing merchant promotion rules and shopper eligibility. Owns cart lines, coupon validation, promotion evaluation, shipping quotes, and cart expiry. Checkout owns order submission and payment orchestration.

## Requirements and acceptance

This annex implements eight approved project requirements. The IDs and exact acceptance criteria are generated from structured/requirements.jsonl and linked in the RTM. The workstream owner must approve any scope change before the Jira baseline is updated.

## Data and service contracts

Owned data: Cart, CartLine, Promotion, Coupon, PromotionRedemption, ShippingQuote, CartPriceSnapshot. Integrations: Catalog price books, Inventory availability, merchant promotion configuration, tax quote service, Checkout session API. All tenant-owned records and events carry explicit tenant scope and correlation IDs.

## Invariants and failure handling

Amounts use integer minor units; promotion precedence is deterministic; a coupon is tenant-scoped and cannot be redeemed beyond configured limits; quoted totals are versioned. Failures are surfaced with stable error codes, trace IDs, and a recovery path; retries are bounded and must not duplicate side effects.

## Dependencies and delivery

The workstream depends on shared identity, API gateway, event envelope, observability, and release controls. Jira source issues: CART-001, CART-002, CART-003. Delivery follows two-week sprints and the release gate in the PMP.

## Acceptance measures

Cart totals are reproducible for the same input snapshot; no promotion is applied twice; recalculation completes within 500 ms at the pilot load.

## Requirement IDs and verification

| Requirement | Priority | Statement | Acceptance criteria | Jira source | Test cases |
| --- | --- | --- | --- | --- | --- |
| FR-CART-001 | High | Create and update carts using products available to the current merchant | Unknown or foreign-tenant SKU references are rejected without exposing foreign catalog data. | CART-001, CART-002, CART-003 | FT-CART-001 |
| FR-CART-002 | High | Recalculate totals deterministically from a versioned price snapshot | Repeated calculation for an unchanged cart and rule set returns identical line and order totals. | CART-001, CART-002, CART-003 | FT-CART-002 |
| FR-CART-003 | Medium | Enforce documented promotion stacking precedence | The order is catalog price rule, item tier discount, cart coupon, then free shipping; incompatible rules are skipped with a reason. | CART-001, CART-002, CART-003 | FT-CART-003 |
| FR-CART-004 | Medium | Validate coupon dates, usage limits, minimum spend, and eligibility | Each invalid condition returns a stable reason and does not consume a redemption. | CART-001, CART-002, CART-003 | FT-CART-004 |
| FR-CART-005 | Medium | Prevent duplicate coupon redemption under concurrent requests | A unique redemption constraint allows at most the configured use count under parallel submissions. | CART-001, CART-002, CART-003 | FT-CART-005 |
| FR-CART-006 | High | Revalidate price and inventory before checkout handoff | Stale price or stock causes a refreshed quote and explicit shopper confirmation. | CART-001, CART-002, CART-003 | FT-CART-006 |
| FR-CART-007 | High | Expire abandoned carts without deleting required audit records | Expired cart lines are unavailable for checkout while aggregate expiry events remain auditable. | CART-001, CART-002, CART-003 | FT-CART-007 |
| FR-CART-008 | Medium | Isolate cart reads and writes by merchant and shopper session | Changing cart_id or merchant context cannot access another tenant's cart. | CART-001, CART-002, CART-003 | FT-CART-008 |
