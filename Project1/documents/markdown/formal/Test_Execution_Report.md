---
document_id: "DOC-ORG-TEST-REPORT-001"
title: "Northstar Commerce Test Execution Report"
project_id: null
organization_id: "ORG-NSC"
scope: "organization"
owner_id: "M-010"
created_at: "2026-10-12"
updated_at: "2026-10-12"
version: "1.0"
status: "In Review"
classification: "Internal"
access_groups: ["GRP-ALL-STAFF"]
source_issue_keys: ["CHKO-005", "PAY-002"]
canonical_document_id: "DOC-ORG-TEST-REPORT-001"
rendition_paths: []
requirement_ids: []
file_path: "documents/markdown/formal/Test_Execution_Report.md"
format: "markdown"
synthetic: true
---

# Northstar Commerce Test Execution Report

Synthetic staging-sim execution snapshot with explicit pass, fail, and blocked outcomes for the functional baseline.

## Run identity

Run RUN-2026-10-12-01 uses build commerce-demo-1.0.0-rc3, schema baseline 2026.10, deterministic seed 42, and environment staging-sim. QA lead M-010 and the QA engineering team (M-037, M-038, M-039, M-040) executed the suite across regular hours and evening overtime (08:30 to 20:45 +07:00) on 12 October 2026. This is a synthetic dataset record, not evidence from a live production system.

## Results

The functional suite contains 84 cases: 82 Passed, 1 Failed, and 1 Blocked. The failing case is FT-CHKO-007 (concurrent duplicate submission) and is linked to CHKO-005. The blocked case is FT-PAY-008 (partner sandbox certificate rotation) and is linked to PAY-002. All other cases have explicit result records.

## Defect disposition

The failed duplicate submission case is a release blocker until Checkout demonstrates one order and one authorization under concurrent replay. The blocked certificate case requires PulsePay sandbox access and must be rerun after the partner change window. Neither result is silently counted as passed.

## Exit recommendation

Do not declare release-ready from this snapshot. Re-run the failed and blocked cases, complete security and performance gates, attach evidence, and obtain QA, Security, Operations, and merchant UAT sign-off. The release gate remains conditional.
