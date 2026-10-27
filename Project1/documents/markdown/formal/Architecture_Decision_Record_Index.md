---
document_id: "DOC-ORG-ADR-INDEX-001"
title: "Architecture Decision Record Index"
project_id: null
organization_id: "ORG-NSC"
scope: "organization"
owner_id: "M-009"
created_at: "2026-10-12"
updated_at: "2026-10-12"
version: "1.0"
status: "Approved"
classification: "Internal"
access_groups: ["GRP-ALL-STAFF"]
source_issue_keys: ["PLAT-001", "PAY-001"]
canonical_document_id: "DOC-ORG-ADR-INDEX-001"
rendition_paths: []
requirement_ids: []
file_path: "documents/markdown/formal/Architecture_Decision_Record_Index.md"
format: "markdown"
synthetic: true
---

# Architecture Decision Record Index

Index of active and superseded architecture decisions with owners, scope, status, and related implementation records.

## Decision governance

Each ADR records context, considered alternatives, decision, consequences, owner, approval date, and linked requirements. Accepted decisions are stable; changing one creates a new ADR that explicitly supersedes the prior record.

## Current and historic records

DOC-PAY-ADR-003 is the active payment idempotency and webhook decision. DOC-PAY-ADR-001 is superseded and retained for historical retrieval tests. Platform architecture, database expand/contract, tenant isolation, event envelope, and API versioning decisions are summarized in the current SDS and component standards until separate ADRs are needed.

## Review triggers

Reopen a decision when an assumption changes, an operational metric misses its threshold, a security finding challenges a control, or a new integration changes a trust boundary. The review links to the affected SRS requirement, issue, test, and release.

## Decision record index

| Document ID | Decision | Version | Status | Owner | Linked issues |
| --- | --- | --- | --- | --- | --- |
| DOC-PAY-ADR-001 | ADR-001: Initial Payment Orchestration (SUPERSEDED) | 1.0 | Superseded | M-018 | PAY-001, PAY-002 |
| DOC-PAY-ADR-003 | ADR-003: Payment Orchestration and Idempotency | 3.0 | Approved | M-006 | PAY-001, PAY-002, PAY-003 |
| DOC-ORG-MEETING-2026-10-09 | Pilot Weekly Decisions and Actions — 9 October | 1.0 | Approved | M-002 | PAY-002, CHKO-005, CAT-002 |
| DOC-ORG-ADR-INDEX-001 | Architecture Decision Record Index | 1.0 | Approved | M-009 | PLAT-001, PAY-001 |
