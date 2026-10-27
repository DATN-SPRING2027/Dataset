---
document_id: "DOC-ORG-DEPLOY-001"
title: "Northstar Commerce Deployment Guide"
project_id: null
organization_id: "ORG-NSC"
scope: "organization"
owner_id: "M-009"
created_at: "2026-10-12"
updated_at: "2026-10-12"
version: "1.0"
status: "Approved"
classification: "Internal"
access_groups: ["GRP-PLATFORM", "GRP-SECURITY"]
source_issue_keys: ["PLAT-007", "PLAT-009"]
canonical_document_id: "DOC-ORG-DEPLOY-001"
rendition_paths: []
requirement_ids: []
file_path: "documents/markdown/formal/Deployment_Guide.md"
format: "markdown"
synthetic: true
---

# Northstar Commerce Deployment Guide

Repeatable deployment sequence for isolated demo/staging environments, including configuration, migrations, health checks, and rollback.

## Prerequisites and environments

Use a clean isolated environment, approved image digest, matching migration bundle, synthetic seed, and least-privilege deployment identity. Required services are PostgreSQL, Redis, object storage, search, identity provider, and PulsePay sandbox adapter. Environment variables contain references to secret-manager paths, never literal credentials.

## Configuration

Set environment name, public base URL, tenant resolver, database endpoint, queue names, search index prefix, identity issuer/audience, webhook public key reference, retention policy, and observability endpoint. Validate mandatory values at startup and fail closed when tenant/security settings are missing.

## Deployment sequence

1) Verify change approval and backups. 2) Apply backward-compatible expand migrations. 3) Deploy API and workers. 4) Verify readiness and queue consumers. 5) run smoke checks for auth, tenant boundary, catalog lookup, search, cart quote, and payment sandbox health. 6) Enable the release feature flag for an internal tenant, then merchant pilot after sign-off.

## Health and rollback

Rollback triggers include checkout 5xx above 1.5% for five minutes, duplicate payment evidence, tenant isolation failure, or irrecoverable migration error. Disable the flag, stop new checkout placement, preserve reconciliation queues, redeploy the prior compatible image, and verify order/payment integrity before resuming traffic.

## Post-deployment evidence

Record image digest, migration IDs, operator, start/end time, health checks, smoke case IDs, alert status, feature-flag state, and rollback decision. Never mark deployment successful from a process exit code alone.
