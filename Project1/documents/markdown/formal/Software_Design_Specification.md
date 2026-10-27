---
document_id: "DOC-ORG-SDS-001"
title: "Northstar Commerce Software Design Specification"
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
source_issue_keys: ["PLAT-001", "PLAT-004"]
canonical_document_id: "DOC-ORG-SDS-001"
rendition_paths: ["documents/docx/Software_Design_Specification.docx"]
requirement_ids: []
file_path: "documents/markdown/formal/Software_Design_Specification.md"
format: "markdown"
synthetic: true
---

# Northstar Commerce Software Design Specification

Logical architecture, service ownership, data flows, tenancy boundaries, failure behavior, and operational design for the pilot.

## Architecture overview

The design uses a modular commerce API with domain ownership boundaries and separate storefront/admin clients. Laravel is the backend reference and Vue.js is the administration UI reference; PostgreSQL stores transactional state, Redis supports bounded cache/queue use, and an Elasticsearch-compatible service supports search. These are synthetic design assumptions, not deployed infrastructure claims.

## Service boundaries

Catalog owns source product data and emits published snapshots. Search builds tenant-scoped indexes. Cart calculates quotes from versioned price and promotion inputs. Checkout coordinates reservations, tax, payment authorization, and order creation. Payment owns provider attempts and webhook inbox. Inventory owns stock ledger and leases. Orders owns lifecycle and return/refund requests. Platform owns identity context, policy, audit, deployment, and recovery.

## Tenant and trust boundaries

The gateway validates identity and derives tenant context from trusted claims; caller-supplied tenant headers are checked, never trusted alone. Service-to-service calls use scoped identities. Every database query includes tenant scope or uses a tenant-keyed repository contract. Search ACL is evaluated before retrieval ranking or content rendering.

## Checkout and payment sequence

A valid cart produces a versioned checkout snapshot. Checkout reserves inventory, requests authorization using a durable idempotency key, and creates one order. A provider timeout returns a pending reconciliation reference. Signed webhooks enter a unique inbox transaction before state changes; duplicate events are acknowledged with no repeated side effect.

## Asynchrony and failure handling

Events have stable IDs, tenant IDs, schema versions, and correlation IDs. Consumers are idempotent and retain retry state. Transient failures use bounded backoff with jitter; hard declines are terminal. Compensation releases holds when safe. Dead-letter items are visible to operators and have replay controls.

## Observability and quality

Logs omit secrets and cardholder data. Metrics use tenant-safe aggregates. Traces connect API request, reservation, provider attempt, webhook, and order event. SLO alerts have severity, owner, runbook link, and escalation path. Schema migrations follow expand/contract and every release has a rollback route.
