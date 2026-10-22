Checkout API Contract

*Contract specification for checkout sessions, tax quotation, and idempotent order placement.*

|  |  |  |  |
| --- | --- | --- | --- |
| **Document ID** | DOC-CHKO-API-002 | **Project** | NSC-CHKO |
| **Owner** | M-005 | **Version** | 2.0 |
| **Updated** | 2026-09-12 | **Status** | Approved |
| **Classification** | Internal | **Access Groups** | GRP-CHECKOUT, GRP-MERIDIAN |

# Request Conventions

* All endpoints require merchant context headers ('X-Merchant-ID') and standard correlation identifiers ('X-Correlation-ID').
* Monetary amounts are represented as integer minor currency units (e.g., cents) alongside ISO 4217 currency strings.
* Unrecognized merchant context returns HTTP 403 Forbidden; malformed payload schemas return HTTP 422 Unprocessable Entity.

# Checkout Session Lifecycle

* POST /api/v1/checkout/sessions creates or retrieves a checkout session given an active cart ID and customer shipping address.
* Clients must supply an 'Idempotency-Key' header. Submitting the identical key and payload returns the original session.
* Submitting the identical key with a mutated payload returns HTTP 409 IDEMPOTENCY\_CONFLICT with structured error details.

# Order Submission & Provider Handshake

* POST /api/v1/checkout/sessions/{id}/orders commits stock reservation, authorizes payment with PulsePay, and spawns the order record.
* In case of upstream payment provider timeout, the endpoint returns HTTP 202 Accepted with a pending reconciliation reference.
* Clients must NOT spawn a new checkout session upon timeout, but poll the reconciliation endpoint using exponential backoff.

# Reference Table

|  |  |  |  |
| --- | --- | --- | --- |
| **Endpoint Method** | **URI Pattern** | **Success Code** | **Key Error Conditions** |
| POST | /api/v1/checkout/sessions | 201 Created | 409 Conflict, 422 Validation Error |
| GET | /api/v1/checkout/sessions/{id} | 200 OK | 404 Not Found, 410 Expired |
| POST | /api/v1/checkout/sessions/{id}/orders | 201 / 202 Pending | 409 Double Submission, 503 Gateway Timeout |
| GET | /api/v1/orders/{id} | 200 OK | 403 Unauthorized Tenant, 404 Missing |
