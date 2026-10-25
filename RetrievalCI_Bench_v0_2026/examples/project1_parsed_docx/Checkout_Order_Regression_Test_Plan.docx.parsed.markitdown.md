Checkout and Order Regression Test Plan

*Formal test suites and quality gates governing checkout session orchestration, payment callbacks, and order states.*

|  |  |  |  |
| --- | --- | --- | --- |
| **Document ID** | DOC-QA-CHECKOUT-017 | **Project** | NSC-CHKO |
| **Owner** | M-010 | **Version** | 1.4 |
| **Updated** | 2026-10-01 | **Status** | In Review |
| **Classification** | Internal | **Access Groups** | GRP-CHECKOUT |

# Scope & Coverage

* Covers automated end-to-end regression suites across checkout sessions, PulsePay webhooks, inventory holds, and order returns.
* Tests execute against simulated multi-tenant fixtures representing Meridian Outfitters and synthetic benchmark test stores.

# Critical Acceptance Scenarios

* Duplicate Request Replay: Submit identical checkout creation requests within 72 hours; assert exactly one order entity is created.
* Webhook Crash Replay: Simulate server crash immediately after payment webhook ingestion; assert no duplicate capture or fulfillment event.
* Cross-Tenant Boundary: Attempt to access Meridian order records using another merchant credential; assert strict HTTP 403 response.
* Partial Refund Boundary: Issue consecutive line-item refunds; assert total refunded minor units never exceed initial authorization capture.

# Exit Criteria for Release

* Zero open P0 or P1 severity defects in payment orchestration or order lifecycle state machines.
* 100% pass rate on multi-tenant access control and cross-tenant data isolation security matrices.

# Reference Table

|  |  |  |  |
| --- | --- | --- | --- |
| **Test Case ID** | **Scenario Description** | **Expected Invariant** | **Severity** |
| TC-CHKO-001 | Concurrent checkout button clicks | Single order, idempotent response | P0 |
| TC-PAY-004 | Duplicate webhook delivery from PulsePay | Deduplicated in inbox, zero re-capture | P0 |
| TC-SEC-012 | Cross-tenant order retrieval attempt | Strict HTTP 403 Forbidden | P0 |
| TC-ORD-008 | Partial refund amount exceeding total | HTTP 422 rejected, zero state mutation | P1 |
