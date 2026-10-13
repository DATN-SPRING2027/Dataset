---
document_id: "DOC-ORG-THREAT-001"
title: "Northstar Commerce Threat Model"
project_id: null
organization_id: "ORG-NSC"
scope: "organization"
owner_id: "M-012"
created_at: "2026-10-12"
updated_at: "2026-10-12"
version: "1.0"
status: "Approved"
classification: "Restricted"
access_groups: ["GRP-SECURITY", "GRP-LEADERS"]
source_issue_keys: ["PLAT-001", "PLAT-003"]
canonical_document_id: "DOC-ORG-THREAT-001"
rendition_paths: []
requirement_ids: []
file_path: "documents/markdown/formal/Threat_Model.md"
format: "markdown"
synthetic: true
---

# Northstar Commerce Threat Model

Trust boundaries, protected assets, abuse cases, controls, residual risks, and release security gates for the pilot.

## Assets and trust boundaries

Protected assets include tenant catalog/order data, identity tokens, payment references, webhook signing material, audit history, and search indexes. Boundaries exist between browser and gateway, Northstar and merchant tenant, Northstar and PulsePay, API and workers, and application services and persistence.

## Threat actors and abuse cases

Consider an unauthenticated internet user, compromised merchant account, malicious tenant administrator, compromised partner credential, replaying network client, insider with excess privilege, and poisoned document upload. Abuse cases include tenant ID spoofing, IDOR, coupon race, webhook replay, SSRF via catalog image URL, log/secret leakage, and retrieval of restricted snippets.

## Required mitigations

Derive tenant from trusted identity claims; enforce object-level authorization; filter ACL before retrieval; use HMAC verification and durable dedupe; use idempotency and unique constraints; validate URLs and upload types; externalize secrets; redact logs; rate-limit public endpoints; maintain immutable audit evidence.

## Security verification

Release checks include cross-tenant negative tests, role matrix tests, inactive-user revocation, webhook tampering/replay, dependency review, secret scanning, upload validation, and restore of security audit records. Findings are triaged with severity, owner, due date, and evidence.

## Residual risk and acceptance

Sandbox providers, synthetic identities, and simulated traffic cannot prove production security. Any residual high risk requires explicit sponsor and Security acceptance, compensating control, expiry date, and tracked issue before release. No raw card data is accepted in the pilot.
