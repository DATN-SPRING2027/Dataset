Commerce Platform Architecture Overview

*Service boundaries, multi-tenant database isolation, and asynchronous event bus architecture for the fictional commerce platform.*

|  |  |  |  |
| --- | --- | --- | --- |
| **Document ID** | DOC-ARCH-PLAT-001 | **Project** | NSC-PLAT |
| **Owner** | M-009 | **Version** | 2.0 |
| **Updated** | 2026-08-28 | **Status** | Approved |
| **Classification** | Internal | **Access Groups** | GRP-ALL-STAFF |

# System Context

* Storefront and merchant administration surfaces access the Commerce API Gateway, which resolves tenant context before delegating to downstream services.
* The fictional stack utilizes modular Laravel domain packages, Vue.js single-page administration interfaces, Redis queue workers, and PostgreSQL schemas.

# Service Boundaries

* Catalog Service owns product variants, merchandising taxonomies, and price books scoped strictly by merchant ID.
* Search & Discovery executes tenant-isolated queries against Elasticsearch clusters, applying merchant access filters prior to text ranking.
* Checkout Service coordinates cart conversions, tax computation, stock reservations, and payment sessions with idempotent guarantees.
* Orders Service encapsulates state machines for authorizations, captures, shipments, cancellations, and return merchandise authorizations.

# Core Architecture Invariants

* All mutating external HTTP requests must include a durable Idempotency-Key retained for at least 72 hours.
* Event consumers must deduplicate messages using durable provider event inbox tables with unique constraints.
* Direct cross-tenant database joins or queries without an explicit tenant\_id filter are strictly forbidden by gateway middleware.

# Reference Table

|  |  |  |  |
| --- | --- | --- | --- |
| **Service Domain** | **Primary Entity** | **Isolation Mechanism** | **Audit Requirement** |
| Catalog | Products & Variants | Tenant-scoped SKU & Attribute Groups | Full change history |
| Checkout | Checkout Sessions | Durable idempotency key (72h TTL) | Session state transitions |
| Payments | Payment Intents & Webhooks | Durable inbox deduplication | Raw payload & response hash |
| Orders | Orders & Returns | Cryptographic state transition chain | Financial audit ledger |
| Platform | Tenants & Access Groups | Row-level tenant isolation middleware | Security access log |
