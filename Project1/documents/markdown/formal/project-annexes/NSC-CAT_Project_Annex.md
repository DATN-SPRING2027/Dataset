---
document_id: "DOC-CAT-ANNEX-001"
title: "Product Catalog & Merchandising Project Annex"
project_id: "NSC-CAT"
organization_id: "ORG-NSC"
scope: "project"
owner_id: "M-002"
created_at: "2026-10-12"
updated_at: "2026-10-12"
version: "1.0"
status: "Approved"
classification: "Internal"
access_groups: ["GRP-CATALOG"]
source_issue_keys: ["CAT-001", "CAT-002", "CAT-004"]
canonical_document_id: "DOC-CAT-ANNEX-001"
rendition_paths: []
requirement_ids: ["FR-CAT-001", "FR-CAT-002", "FR-CAT-003", "FR-CAT-004", "FR-CAT-005", "FR-CAT-006", "FR-CAT-007", "FR-CAT-008"]
file_path: "documents/markdown/formal/project-annexes/NSC-CAT_Project_Annex.md"
format: "markdown"
synthetic: true
---

# Product Catalog & Merchandising Project Annex

Scope, requirements, ownership, dependencies, acceptance, and operational boundary for Product Catalog & Merchandising

## Objective and boundary

Give Meridian merchandisers a safe, auditable way to import, enrich, price, and publish product records. Owns product, variant, attribute, taxonomy, price-book, and import-job records. Checkout owns the purchase-time price snapshot; Search owns the query index.

## Requirements and acceptance

This annex implements eight approved project requirements. The IDs and exact acceptance criteria are generated from structured/requirements.jsonl and linked in the RTM. The workstream owner must approve any scope change before the Jira baseline is updated.

## Data and service contracts

Owned data: Product, ProductVariant, MerchantSku, AttributeDefinition, CategoryNode, PriceBook, ImportJob, ImportRowError. Integrations: Merchant CSV upload, object storage, catalog validation worker, event bus, search indexing, merchant administration UI. All tenant-owned records and events carry explicit tenant scope and correlation IDs.

## Invariants and failure handling

SKU uniqueness is scoped to merchant; archived SKUs remain reserved; invalid rows do not erase valid rows; a draft import is not searchable until publication. Failures are surfaced with stable error codes, trace IDs, and a recovery path; retries are bounded and must not duplicate side effects.

## Dependencies and delivery

The workstream depends on shared identity, API gateway, event envelope, observability, and release controls. Jira source issues: CAT-001, CAT-002, CAT-004. Delivery follows two-week sprints and the release gate in the PMP.

## Acceptance measures

At least 99.5% of valid rows in the approved pilot file are imported; invalid rows have actionable error codes; catalog publication reaches Search within five minutes.

## Requirement IDs and verification

| Requirement | Priority | Statement | Acceptance criteria | Jira source | Test cases |
| --- | --- | --- | --- | --- | --- |
| FR-CAT-001 | High | Validate CSV headers and required fields before accepting an import job | The service returns a row-level report and does not create products from malformed rows. | CAT-001, CAT-002, CAT-004 | FT-CAT-001 |
| FR-CAT-002 | High | Enforce merchant-scoped SKU uniqueness across active and archived products | A duplicate SKU is rejected with a stable conflict code; another merchant may reuse the SKU. | CAT-001, CAT-002, CAT-004 | FT-CAT-002 |
| FR-CAT-003 | Medium | Support parent products with independently sellable variants | Each variant has its own SKU, option values, price, and inventory reference. | CAT-001, CAT-002, CAT-004 | FT-CAT-003 |
| FR-CAT-004 | Medium | Validate currency and non-negative integer minor-unit prices | Unsupported currency and fractional minor units are rejected before persistence. | CAT-001, CAT-002, CAT-004 | FT-CAT-004 |
| FR-CAT-005 | Medium | Allow partial success for mixed-validity bulk files | Valid rows commit atomically per row; rejected rows remain downloadable with source row numbers. | CAT-001, CAT-002, CAT-004 | FT-CAT-005 |
| FR-CAT-006 | High | Keep draft catalog changes out of public search until publication | Only published versions emit catalog.changed events consumed by Search. | CAT-001, CAT-002, CAT-004 | FT-CAT-006 |
| FR-CAT-007 | High | Restrict merchant catalog administration to the authenticated tenant | A user cannot read or modify another merchant's products by changing an identifier. | CAT-001, CAT-002, CAT-004 | FT-CAT-007 |
| FR-CAT-008 | Medium | Preserve product audit history and actor attribution | Every publish, archive, price, and taxonomy change records actor, timestamp, and before/after values. | CAT-001, CAT-002, CAT-004 | FT-CAT-008 |
