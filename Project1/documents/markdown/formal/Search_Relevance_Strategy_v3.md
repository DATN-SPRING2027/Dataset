---
document_id: "DOC-SRCH-STRATEGY-003"
title: "Search Relevance and Discovery Strategy"
project_id: "NSC-SRCH"
organization_id: "ORG-NSC"
scope: "project"
owner_id: "M-004"
created_at: "2026-09-18"
updated_at: "2026-09-18"
version: "3.0"
status: "In Review"
classification: "Internal"
access_groups: ["GRP-ALL-STAFF"]
source_issue_keys: ["SRCH-001", "SRCH-002"]
file_path: "documents/markdown/formal/Search_Relevance_Strategy_v3.md"
format: "markdown"
synthetic: true
---

# Search Relevance and Discovery Strategy

Search ranking models, merchant-scoped synonym expansion, relevance benchmarks, and latency targets.

## Ranking Model Hierarchy

Exact SKU matches and exact product title matches receive highest ranking boost, followed by fuzzy title and category matching. Inventory availability acts as a hard filter.

## Synonym Dictionary Management

Each merchant maintains a versioned synonym dictionary. Synonym expansions operate within tenant boundaries and must never bleed across merchants.

## Offline Benchmark Evaluation

Offline test harness runs 120 synthetic queries measuring nDCG@10, zero-result rate, and p95 query latency across product categories.

## Performance Target

P95 search response latency must remain strictly below 300ms under 100 queries per second for an index of 50,000 SKUs.

## Privacy & Personalization Boundary

User profiling or tracking across search queries is not authorized for the pilot release; model versioning is recorded per request.
