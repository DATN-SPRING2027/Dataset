---
document_id: "DOC-ORG-DBD-001"
title: "Northstar Commerce Database Design and ERD"
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
canonical_document_id: "DOC-ORG-DBD-001"
rendition_paths: ["documents/docx/Database_Design_and_ERD.docx"]
requirement_ids: []
file_path: "documents/markdown/formal/Database_Design_and_ERD.md"
format: "markdown"
synthetic: true
---

# Northstar Commerce Database Design and ERD

Transactional entity boundaries, tenant keys, constraints, indexes, retention, migration sequencing, and recovery requirements.

## Data ownership and relational model

The operational model separates Tenant, Principal, Product, ProductVariant, Cart, CheckoutSession, PaymentIntent, WebhookInbox, StockLedger, Reservation, Order, Shipment, ReturnAuthorization, Refund, and AuditEvent. Merchant-owned rows carry tenant_id; globally unique IDs do not replace tenant predicates.

## Integrity constraints and indexes

Enforce unique (tenant_id, merchant_sku), unique (tenant_id, idempotency_key_hash, operation), unique (tenant_id, provider_event_id), and foreign keys from child records to tenant-scoped parents. Index tenant_id with status/date for common queries. Use partial indexes for active reservations and unresolved reconciliation records.

## ERD and lifecycle

```mermaid
erDiagram
  TENANT ||--o{ PRODUCT : owns
  PRODUCT ||--|{ PRODUCT_VARIANT : has
  TENANT ||--o{ CART : owns
  CART ||--o{ CART_LINE : contains
  CHECKOUT_SESSION ||--o{ IDEMPOTENCY_RECORD : protects
  PAYMENT_INTENT ||--o{ WEBHOOK_INBOX : receives
  TENANT ||--o{ STOCK_LEDGER : scopes
  STOCK_LEDGER ||--o{ RESERVATION : allocates
  ORDER ||--|{ ORDER_LINE_SNAPSHOT : records
  ORDER ||--o{ RETURN_AUTHORIZATION : permits
  PAYMENT_INTENT ||--o{ REFUND : settles
```

## Concurrency and consistency

Money is integer minor units. Reservation and coupon redemption use database transactions and unique constraints, not read-then-write checks alone. Webhook inbox insertion and payment state transition commit atomically. Order snapshots are immutable; corrections create compensating entries.

## Retention and privacy

Operational retention follows the security classification standard and applicable fictional pilot policy. Analytics receives masked identifiers and tenant-scoped views. PAN/CVV are prohibited. Audit and financial records have explicit retention owners; deletion requests preserve legally required transaction evidence while minimizing personal data.

## Migration and rollback

Use expand/contract: add nullable columns/tables and indexes concurrently, deploy compatible readers/writers, backfill in bounded batches, verify counts, then remove old fields in a later release. Each migration has a tested down/forward recovery note; destructive data transformations require a backup and explicit sign-off.
