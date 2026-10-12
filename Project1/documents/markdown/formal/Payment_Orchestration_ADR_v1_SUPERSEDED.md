---
document_id: "DOC-PAY-ADR-001"
title: "ADR-001: Initial Payment Orchestration (SUPERSEDED)"
project_id: "NSC-PAY"
organization_id: "ORG-NSC"
scope: "project"
owner_id: "M-018"
created_at: "2026-06-02"
updated_at: "2026-06-02"
version: "1.0"
status: "Superseded"
classification: "Restricted"
access_groups: ["GRP-CHECKOUT"]
source_issue_keys: ["PAY-001", "PAY-002"]
file_path: "documents/markdown/formal/Payment_Orchestration_ADR_v1_SUPERSEDED.md"
format: "markdown"
synthetic: true
---

# ADR-001: Initial Payment Orchestration (SUPERSEDED)

Historic architectural decision for payment orchestration. Retained to evaluate stale-version search suppression and conflict tests.

## Decision (Superseded)

Retain idempotency keys for 12 hours. Retry payment provider timeouts up to 3 times without jitter. Accept refund requests within 14 calendar days of shipment.

## Historical Context

The early prototype used short-lived Redis keys and did not implement durable inbox deduplication or delayed webhook replay handling.

## Superseded Notice

SUPERSEDED by DOC-PAY-ADR-003 on 2026-08-19. Do not treat this document as active architectural guidance.
