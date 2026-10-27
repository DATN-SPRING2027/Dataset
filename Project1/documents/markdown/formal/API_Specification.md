---
document_id: "DOC-ORG-API-001"
title: "Northstar Commerce API Specification"
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
source_issue_keys: ["PLAT-001", "CHKO-002", "PAY-008"]
canonical_document_id: "DOC-ORG-API-001"
rendition_paths: ["documents/docx/API_Specification.docx"]
requirement_ids: []
file_path: "documents/markdown/formal/API_Specification.md"
format: "markdown"
synthetic: true
---

# Northstar Commerce API Specification

Cross-service API conventions, endpoint inventory, error model, tenant context, idempotency, events, and versioning policy.

## Transport and authentication

All APIs use HTTPS and versioned paths under /api/v1. User requests use OIDC bearer tokens; service calls use scoped service identities. Tenant context is resolved from trusted claims and validated against resource ownership. Correlation IDs are accepted or generated and returned.

## Endpoint inventory

Catalog: POST /catalog/imports, GET/POST /products, POST /products/{id}/publish. Search: GET /search and GET /search/facets. Cart: POST /carts, PATCH /carts/{id}/lines, POST /carts/{id}/quote. Checkout: POST /checkout/sessions and POST /checkout/sessions/{id}/orders. Payment: POST /payment-intents and POST /webhooks/pulsepay. Inventory: POST /reservations, POST /reservations/{id}/release. Orders: GET /orders/{id}, POST /orders/{id}/returns, POST /orders/{id}/refunds.

## Request and response conventions

JSON uses camelCase at the HTTP boundary and stable IDs. Pagination uses cursor plus limit with a bounded maximum. Dates are ISO 8601 UTC; monetary values use amountMinor and currency. Responses include requestId and resource version where concurrency matters.

## Errors and retries

Errors use code, message, requestId, and optional fieldErrors. 400 indicates malformed syntax; 401 unauthenticated; 403 denied scope; 404 absent or intentionally concealed resource; 409 idempotency/version conflict; 422 validation failure; 429 rate limit; 5xx service failure. Retry only when the operation is idempotent or has a durable key.

## Idempotency, webhooks, and events

Mutating order/payment endpoints require Idempotency-Key retained for at least 72 hours. Identical payload replay returns the original response; changed payload returns 409. PulsePay webhooks use HMAC-SHA256. Internal events include eventId, schemaVersion, tenantId, occurredAt, and correlationId.

## Versioning and detailed contracts

Additive optional fields are backward compatible; breaking behavior requires a new API major version and migration window. Checkout details are in Checkout_API_Contract.docx; PulsePay signature and delivery rules are in Partner_Webhook_Specification_PulsePay.md. The OpenAPI representation is the next implementation artifact and must be generated from the approved endpoint contract before production integration.
