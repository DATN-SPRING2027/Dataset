Customer Order Lifecycle and Fulfillment SOP

*Standard operating procedure for order state transitions, split shipments, and carrier tracking integration.*

|  |  |  |  |
| --- | --- | --- | --- |
| **Document ID** | DOC-ORD-SOP-004 | **Project** | NSC-ORD |
| **Owner** | M-008 | **Version** | 2.0 |
| **Updated** | 2026-08-11 | **Status** | Approved |
| **Classification** | Internal | **Access Groups** | GRP-ALL-STAFF, GRP-MERIDIAN |

# Order Lifecycle States

* State progression: PENDING -> AUTHORIZED -> PROCESSING -> PACKED -> SHIPPED -> DELIVERED.
* Cancellation is permitted only while the order remains in PENDING, AUTHORIZED, or PROCESSING state.
* Once an order transitions to PACKED, cancellation is locked and the customer must utilize the standard return RMA flow.

# Carrier Integration & Tracking

* Tracking numbers are ingested via webhook and published to merchant admin and customer email notifications within 5 minutes.
* Partial shipments generate distinct fulfillment sub-records with item-level tracking references.

# Reference Table

|  |  |  |  |
| --- | --- | --- | --- |
| **State** | **Allowed Next States** | **Customer Cancellation Permitted** | **Inventory Impact** |
| AUTHORIZED | PROCESSING, CANCELLED | Yes (full automated refund) | Reserved |
| PROCESSING | PACKED, CANCELLED | Yes (manual review required) | Reserved |
| PACKED | SHIPPED | No (return request required) | Deducted |
| SHIPPED | DELIVERED, RETURNED | No | Deducted |
