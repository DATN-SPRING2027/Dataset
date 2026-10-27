---
document_id: "DOC-PLAT-ANNEX-001"
title: "Platform Reliability & Governance Project Annex"
project_id: "NSC-PLAT"
organization_id: "ORG-NSC"
scope: "project"
owner_id: "M-009"
created_at: "2026-10-12"
updated_at: "2026-10-12"
version: "1.0"
status: "Approved"
classification: "Internal"
access_groups: ["GRP-PLATFORM"]
source_issue_keys: ["PLAT-001", "PLAT-004", "PLAT-007"]
canonical_document_id: "DOC-PLAT-ANNEX-001"
rendition_paths: []
requirement_ids: ["FR-PLAT-001", "FR-PLAT-002", "FR-PLAT-003", "FR-PLAT-004", "FR-PLAT-005", "FR-PLAT-006", "FR-PLAT-007", "FR-PLAT-008"]
file_path: "documents/markdown/formal/project-annexes/NSC-PLAT_Project_Annex.md"
format: "markdown"
synthetic: true
---

# Platform Reliability & Governance Project Annex

Scope, requirements, ownership, dependencies, acceptance, and operational boundary for Platform Reliability & Governance

## Objective and boundary

Provide secure tenant boundaries, identity lifecycle, platform operations, observability, deployment safety, and recoverability. Owns gateway identity/tenant context, platform policies, deployment and recovery controls, audit events, and service-level telemetry.

## Requirements and acceptance

This annex implements eight approved project requirements. The IDs and exact acceptance criteria are generated from structured/requirements.jsonl and linked in the RTM. The workstream owner must approve any scope change before the Jira baseline is updated.

## Data and service contracts

Owned data: Tenant, Principal, AccessGroup, Membership, AuditEvent, FeatureFlag, DeploymentRecord, BackupManifest. Integrations: OIDC identity provider, API gateway, PostgreSQL, Redis, object storage, CI pipeline, metrics/logging/alerting stack. All tenant-owned records and events carry explicit tenant scope and correlation IDs.

## Invariants and failure handling

Deny by default; filter ACL before retrieval or snippets; revoke inactive users promptly; secrets are externalized; migrations use expand/contract; backups are restore-tested. Failures are surfaced with stable error codes, trace IDs, and a recovery path; retries are bounded and must not duplicate side effects.

## Dependencies and delivery

The workstream depends on shared identity, API gateway, event envelope, observability, and release controls. Jira source issues: PLAT-001, PLAT-004, PLAT-007. Delivery follows two-week sprints and the release gate in the PMP.

## Acceptance measures

Checkout availability target 99.9%; RPO 15 minutes and RTO 4 hours for pilot data; all privileged actions are attributable and searchable.

## Requirement IDs and verification

| Requirement | Priority | Statement | Acceptance criteria | Jira source | Test cases |
| --- | --- | --- | --- | --- | --- |
| FR-PLAT-001 | High | Resolve tenant context from authenticated identity, not caller-supplied headers alone | A forged tenant header cannot grant access to another tenant's resources. | PLAT-001, PLAT-004, PLAT-007 | FT-PLAT-001 |
| FR-PLAT-002 | High | Apply authorization before search ranking, counts, and snippet generation | Unauthorized documents reveal no title, count, excerpt, or existence signal. | PLAT-001, PLAT-004, PLAT-007 | FT-PLAT-002 |
| FR-PLAT-003 | Medium | Revoke sessions and memberships when an account becomes inactive | Inactive principals cannot authenticate or retain group permissions; historical audit attribution remains. | PLAT-001, PLAT-004, PLAT-007 | FT-PLAT-003 |
| FR-PLAT-004 | Medium | Record privileged actions in a tamper-evident audit stream | Actor, action, target, tenant, timestamp, and correlation ID are retained. | PLAT-001, PLAT-004, PLAT-007 | FT-PLAT-004 |
| FR-PLAT-005 | Medium | Externalize credentials and rotate them without storing secrets in the repository | Runtime reads scoped secrets from a secret provider; configuration samples contain placeholders only. | PLAT-001, PLAT-004, PLAT-007 | FT-PLAT-005 |
| FR-PLAT-006 | High | Deploy database changes using backward-compatible expand/contract sequencing | Old and new application versions operate during the migration window and rollback remains defined. | PLAT-001, PLAT-004, PLAT-007 | FT-PLAT-006 |
| FR-PLAT-007 | High | Monitor service SLOs, queue health, and tenant-isolation failures | Threshold breaches generate actionable alerts with service, severity, and runbook link. | PLAT-001, PLAT-004, PLAT-007 | FT-PLAT-007 |
| FR-PLAT-008 | Medium | Prove backup restore against documented RPO and RTO targets | A scheduled restore drill records measured recovery time, integrity checks, and approver. | PLAT-001, PLAT-004, PLAT-007 | FT-PLAT-008 |
