---
document_id: "DOC-SRCH-ANNEX-001"
title: "Search & Discovery Project Annex"
project_id: "NSC-SRCH"
organization_id: "ORG-NSC"
scope: "project"
owner_id: "M-002"
created_at: "2026-10-12"
updated_at: "2026-10-12"
version: "1.0"
status: "Approved"
classification: "Internal"
access_groups: ["GRP-SEARCH"]
source_issue_keys: ["SRCH-001", "SRCH-002", "SRCH-003"]
canonical_document_id: "DOC-SRCH-ANNEX-001"
rendition_paths: []
requirement_ids: ["FR-SRCH-001", "FR-SRCH-002", "FR-SRCH-003", "FR-SRCH-004", "FR-SRCH-005", "FR-SRCH-006", "FR-SRCH-007", "FR-SRCH-008"]
file_path: "documents/markdown/formal/project-annexes/NSC-SRCH_Project_Annex.md"
format: "markdown"
synthetic: true
---

# Search & Discovery Project Annex

Scope, requirements, ownership, dependencies, acceptance, and operational boundary for Search & Discovery

## Objective and boundary

Help shoppers find in-stock products using tenant-scoped relevance, filters, synonyms, and locale-aware matching. Owns query parsing, ranking, facets, synonym sets, and search index lifecycle. Catalog owns source product data; Inventory supplies availability.

## Requirements and acceptance

This annex implements eight approved project requirements. The IDs and exact acceptance criteria are generated from structured/requirements.jsonl and linked in the RTM. The workstream owner must approve any scope change before the Jira baseline is updated.

## Data and service contracts

Owned data: SearchDocument, SynonymSet, SearchQueryLog, FacetDefinition, IndexBuild, RelevanceJudgment. Integrations: Catalog publication events, Inventory availability, Elasticsearch-compatible search cluster, storefront search API, metrics pipeline. All tenant-owned records and events carry explicit tenant scope and correlation IDs.

## Invariants and failure handling

Tenant filter is applied before ranking; unavailable items are excluded when the request requires buyable stock; synonyms never cross tenants; indexing is eventually consistent and observable. Failures are surfaced with stable error codes, trace IDs, and a recovery path; retries are bounded and must not duplicate side effects.

## Dependencies and delivery

The workstream depends on shared identity, API gateway, event envelope, observability, and release controls. Jira source issues: SRCH-001, SRCH-002, SRCH-003. Delivery follows two-week sprints and the release gate in the PMP.

## Acceptance measures

P95 query latency below 300 ms at 100 queries per second for a 50,000 SKU tenant index; nDCG@10 at least 0.82 on the approved relevance set.

## Requirement IDs and verification

| Requirement | Priority | Statement | Acceptance criteria | Jira source | Test cases |
| --- | --- | --- | --- | --- | --- |
| FR-SRCH-001 | High | Return exact SKU and exact title matches ahead of fuzzy matches | Ranking tests show exact SKU above exact title and exact title above fuzzy/category-only matches. | SRCH-001, SRCH-002, SRCH-003 | FT-SRCH-001 |
| FR-SRCH-002 | High | Apply merchant identity to every query and synonym lookup | A query under one merchant returns no products or terms owned only by another merchant. | SRCH-001, SRCH-002, SRCH-003 | FT-SRCH-002 |
| FR-SRCH-003 | Medium | Support merchant-managed versioned synonym sets | A synonym change is validated, versioned, auditable, and reversible without changing source catalog text. | SRCH-001, SRCH-002, SRCH-003 | FT-SRCH-003 |
| FR-SRCH-004 | Medium | Provide filterable facets for category, size, color, price, and availability | Facet counts use the same tenant, query, and filter scope as the returned hits. | SRCH-001, SRCH-002, SRCH-003 | FT-SRCH-004 |
| FR-SRCH-005 | Medium | Support locale-aware normalization without destructive rewriting | Accent and case normalization improves matching while preserving original display text. | SRCH-001, SRCH-002, SRCH-003 | FT-SRCH-005 |
| FR-SRCH-006 | High | Exclude unavailable inventory from buyable-result mode | Out-of-stock records are omitted when availability_only is true and remain discoverable otherwise. | SRCH-001, SRCH-002, SRCH-003 | FT-SRCH-006 |
| FR-SRCH-007 | High | Expose zero-result and latency telemetry without customer identifiers | Metrics contain tenant-safe aggregates and no raw email, name, or address. | SRCH-001, SRCH-002, SRCH-003 | FT-SRCH-007 |
| FR-SRCH-008 | Medium | Make index build completion and failures visible to operators | Every build has a version, start/end time, document count, status, and retryable failure reason. | SRCH-001, SRCH-002, SRCH-003 | FT-SRCH-008 |
