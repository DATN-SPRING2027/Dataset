---
document_id: "DOC-ORG-FTCAT-001"
title: "Northstar Commerce Functional Test Catalog"
project_id: null
organization_id: "ORG-NSC"
scope: "organization"
owner_id: "M-010"
created_at: "2026-10-12"
updated_at: "2026-10-12"
version: "1.0"
status: "Approved"
classification: "Internal"
access_groups: ["GRP-ALL-STAFF"]
source_issue_keys: ["CHKO-005", "PLAT-003"]
canonical_document_id: "DOC-ORG-FTCAT-001"
rendition_paths: []
requirement_ids: []
file_path: "documents/markdown/formal/Functional_Test_Catalog.md"
format: "markdown"
synthetic: true
---

# Northstar Commerce Functional Test Catalog

Index and execution instructions for project-level positive, negative, boundary, authorization, concurrency, and recovery cases.

## Case format

Each case has a stable case ID, project, requirement IDs, actor, preconditions, ordered steps, expected result, priority, tags, linked issue, automation indicator, and latest execution result. The executable metadata is in structured/functional_test_cases.jsonl.

## Project coverage

The catalog contains eight workstream suites with eight requirement-linked cases per project plus twenty cross-cutting cases. It covers catalog import and SKU rules, search relevance and isolation, cart/promotion behavior, checkout idempotency, payment replay/signatures, inventory concurrency, order/return policy, and platform identity/operations.

## Execution discipline

Reset tenant-scoped test data between cases. Record actual output and evidence in test_execution_results.jsonl. A blocked case is not a pass; a failed case stays failed until a new run proves the fix. Do not alter expected results to match observed defects.

## Coverage boundaries

The 120-plus RAG, ACL, ingestion, progress, and analytics evaluation cases are a separate benchmark suite. They test the dataset and retrieval system, not only the commerce application. The workbook presents both categories separately.
