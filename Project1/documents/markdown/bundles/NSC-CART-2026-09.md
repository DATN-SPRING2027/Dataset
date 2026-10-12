---
bundle_id: "BUNDLE-NSC-CART-2026-09"
project_id: "NSC-CART"
project_name: "Cart & Promotions"
period: "2026-09"
classification: "Internal"
access_groups: ["GRP-ALL-STAFF"]
logical_document_count: 30
synthetic: true
---

# Cart & Promotions — Monthly Engineering Records (2026-09)

This Markdown bundle organizes 30 verified logical project records, decisions, meeting outcomes, and technical milestone updates for NSC-CART during 2026-09.

### [DOC-CART-20260901-01] Cart & Promotions: Regression Test Summary #1 (2026-09-01)
<a id="doc-cart-20260901-01"></a>

- **Document ID**: `DOC-CART-20260901-01`
- **Date**: 2026-09-01
- **Author**: Jordan Lee (`M-002`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-086`](https://jira.northstar.invalid/browse/CART-086)
- **Record Type**: Regression Test Summary

#### Context & Technical Objective
During iteration delivery on [CART-086] (Promotion stacking hierarchy and discount evaluation engine - Phase 8), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260902-02] Cart & Promotions: Database Migration Checklist #2 (2026-09-02)
<a id="doc-cart-20260902-02"></a>

- **Document ID**: `DOC-CART-20260902-02`
- **Date**: 2026-09-02
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-086`](https://jira.northstar.invalid/browse/CART-086)
- **Record Type**: Database Migration Checklist

#### Context & Technical Objective
During iteration delivery on [CART-086] (Promotion stacking hierarchy and discount evaluation engine - Phase 8), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260902-03] Cart & Promotions: Daily Standup & Blocker Log #3 (2026-09-02)
<a id="doc-cart-20260902-03"></a>

- **Document ID**: `DOC-CART-20260902-03`
- **Date**: 2026-09-02
- **Author**: Lily Perez (`M-059`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-102`](https://jira.northstar.invalid/browse/CART-102)
- **Record Type**: Daily Standup & Blocker Log

#### Context & Technical Objective
During iteration delivery on [CART-102] (Immutable cart audit transition event logging - Phase 9), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260903-04] Cart & Promotions: API Contract Revision #4 (2026-09-03)
<a id="doc-cart-20260903-04"></a>

- **Document ID**: `DOC-CART-20260903-04`
- **Date**: 2026-09-03
- **Author**: William Miller (`M-023`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-099`](https://jira.northstar.invalid/browse/CART-099)
- **Record Type**: API Contract Revision

#### Context & Technical Objective
During iteration delivery on [CART-099] (Abandoned cart expiration workflow with automated stock release - Phase 9), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260904-05] Cart & Promotions: Database Migration Checklist #5 (2026-09-04)
<a id="doc-cart-20260904-05"></a>

- **Document ID**: `DOC-CART-20260904-05`
- **Date**: 2026-09-04
- **Author**: Grace Wilson (`M-009`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-096`](https://jira.northstar.invalid/browse/CART-096)
- **Record Type**: Database Migration Checklist

#### Context & Technical Objective
During iteration delivery on [CART-096] (Bundle product component price breakdown in cart session - Phase 8), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260907-06] Cart & Promotions: Daily Standup & Blocker Log #6 (2026-09-07)
<a id="doc-cart-20260907-06"></a>

- **Document ID**: `DOC-CART-20260907-06`
- **Date**: 2026-09-07
- **Author**: Jordan Lee (`M-002`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-081`](https://jira.northstar.invalid/browse/CART-081)
- **Record Type**: Daily Standup & Blocker Log

#### Context & Technical Objective
During iteration delivery on [CART-081] (Cart currency conversion with cached FX exchange rates - Phase 7), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260907-07] Cart & Promotions: API Contract Revision #7 (2026-09-07)
<a id="doc-cart-20260907-07"></a>

- **Document ID**: `DOC-CART-20260907-07`
- **Date**: 2026-09-07
- **Author**: Owen Garcia (`M-010`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-097`](https://jira.northstar.invalid/browse/CART-097)
- **Record Type**: API Contract Revision

#### Context & Technical Objective
During iteration delivery on [CART-097] (Guest cart merging into customer account upon login - Phase 9), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260908-08] Cart & Promotions: Incident Post-Mortem Action #8 (2026-09-08)
<a id="doc-cart-20260908-08"></a>

- **Document ID**: `DOC-CART-20260908-08`
- **Date**: 2026-09-08
- **Author**: Lily Perez (`M-059`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-093`](https://jira.northstar.invalid/browse/CART-093)
- **Record Type**: Incident Post-Mortem Action

#### Context & Technical Objective
During iteration delivery on [CART-093] (Cart currency conversion with cached FX exchange rates - Phase 8), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260909-09] Cart & Promotions: Merchant Sync Decision #9 (2026-09-09)
<a id="doc-cart-20260909-09"></a>

- **Document ID**: `DOC-CART-20260909-09`
- **Date**: 2026-09-09
- **Author**: William Miller (`M-023`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-090`](https://jira.northstar.invalid/browse/CART-090)
- **Record Type**: Merchant Sync Decision

#### Context & Technical Objective
During iteration delivery on [CART-090] (Immutable cart audit transition event logging - Phase 8), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260909-10] Cart & Promotions: Architecture Decision Note #10 (2026-09-09)
<a id="doc-cart-20260909-10"></a>

- **Document ID**: `DOC-CART-20260909-10`
- **Date**: 2026-09-09
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-106`](https://jira.northstar.invalid/browse/CART-106)
- **Record Type**: Architecture Decision Note

#### Context & Technical Objective
During iteration delivery on [CART-106] (Cart coupon eligibility against customer group rules - Phase 9), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260910-11] Cart & Promotions: Incident Post-Mortem Action #11 (2026-09-10)
<a id="doc-cart-20260910-11"></a>

- **Document ID**: `DOC-CART-20260910-11`
- **Date**: 2026-09-10
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-107`](https://jira.northstar.invalid/browse/CART-107)
- **Record Type**: Incident Post-Mortem Action

#### Context & Technical Objective
During iteration delivery on [CART-107] (Cart session TTL extension on user checkout interaction - Phase 9), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260911-12] Cart & Promotions: Merchant Sync Decision #12 (2026-09-11)
<a id="doc-cart-20260911-12"></a>

- **Document ID**: `DOC-CART-20260911-12`
- **Date**: 2026-09-11
- **Author**: Owen Garcia (`M-010`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-104`](https://jira.northstar.invalid/browse/CART-104)
- **Record Type**: Merchant Sync Decision

#### Context & Technical Objective
During iteration delivery on [CART-104] (Merchant cart item maximum quantity limit constraints - Phase 9), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260914-13] Cart & Promotions: Sprint Planning Update #13 (2026-09-14)
<a id="doc-cart-20260914-13"></a>

- **Document ID**: `DOC-CART-20260914-13`
- **Date**: 2026-09-14
- **Author**: Lily Perez (`M-059`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-084`](https://jira.northstar.invalid/browse/CART-084)
- **Record Type**: Sprint Planning Update

#### Context & Technical Objective
During iteration delivery on [CART-084] (Bundle product component price breakdown in cart session - Phase 7), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260914-14] Cart & Promotions: Feature Rollout Milestone #14 (2026-09-14)
<a id="doc-cart-20260914-14"></a>

- **Document ID**: `DOC-CART-20260914-14`
- **Date**: 2026-09-14
- **Author**: Jordan Lee (`M-002`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-100`](https://jira.northstar.invalid/browse/CART-100)
- **Record Type**: Feature Rollout Milestone

#### Context & Technical Objective
During iteration delivery on [CART-100] (Order line total recalculation after real-time inventory adjustments - Phase 9), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260915-15] Cart & Promotions: Performance Benchmark Report #15 (2026-09-15)
<a id="doc-cart-20260915-15"></a>

- **Document ID**: `DOC-CART-20260915-15`
- **Date**: 2026-09-15
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-101`](https://jira.northstar.invalid/browse/CART-101)
- **Record Type**: Performance Benchmark Report

#### Context & Technical Objective
During iteration delivery on [CART-101] (Idempotent cart item updates during concurrent requests - Phase 9), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260916-16] Cart & Promotions: Sprint Planning Update #16 (2026-09-16)
<a id="doc-cart-20260916-16"></a>

- **Document ID**: `DOC-CART-20260916-16`
- **Date**: 2026-09-16
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-098`](https://jira.northstar.invalid/browse/CART-098)
- **Record Type**: Sprint Planning Update

#### Context & Technical Objective
During iteration delivery on [CART-098] (Promotion stacking hierarchy and discount evaluation engine - Phase 9), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260917-17] Cart & Promotions: Security Review Note #17 (2026-09-17)
<a id="doc-cart-20260917-17"></a>

- **Document ID**: `DOC-CART-20260917-17`
- **Date**: 2026-09-17
- **Author**: Owen Garcia (`M-010`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-094`](https://jira.northstar.invalid/browse/CART-094)
- **Record Type**: Security Review Note

#### Context & Technical Objective
During iteration delivery on [CART-094] (Cart coupon eligibility against customer group rules - Phase 8), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260917-18] Cart & Promotions: Regression Test Summary #18 (2026-09-17)
<a id="doc-cart-20260917-18"></a>

- **Document ID**: `DOC-CART-20260917-18`
- **Date**: 2026-09-17
- **Author**: Grace Wilson (`M-009`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-110`](https://jira.northstar.invalid/browse/CART-110)
- **Record Type**: Regression Test Summary

#### Context & Technical Objective
During iteration delivery on [CART-110] (Promotion stacking hierarchy and discount evaluation engine - Phase 10), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260918-19] Cart & Promotions: Integration Review Notes #19 (2026-09-18)
<a id="doc-cart-20260918-19"></a>

- **Document ID**: `DOC-CART-20260918-19`
- **Date**: 2026-09-18
- **Author**: Jordan Lee (`M-002`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-107`](https://jira.northstar.invalid/browse/CART-107)
- **Record Type**: Integration Review Notes

#### Context & Technical Objective
During iteration delivery on [CART-107] (Cart session TTL extension on user checkout interaction - Phase 9), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260921-20] Cart & Promotions: Security Review Note #20 (2026-09-21)
<a id="doc-cart-20260921-20"></a>

- **Document ID**: `DOC-CART-20260921-20`
- **Date**: 2026-09-21
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-092`](https://jira.northstar.invalid/browse/CART-092)
- **Record Type**: Security Review Note

#### Context & Technical Objective
During iteration delivery on [CART-092] (Merchant cart item maximum quantity limit constraints - Phase 8), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260921-21] Cart & Promotions: Regression Test Summary #21 (2026-09-21)
<a id="doc-cart-20260921-21"></a>

- **Document ID**: `DOC-CART-20260921-21`
- **Date**: 2026-09-21
- **Author**: Lily Perez (`M-059`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-108`](https://jira.northstar.invalid/browse/CART-108)
- **Record Type**: Regression Test Summary

#### Context & Technical Objective
During iteration delivery on [CART-108] (Bundle product component price breakdown in cart session - Phase 9), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260922-22] Cart & Promotions: Integration Review Notes #22 (2026-09-22)
<a id="doc-cart-20260922-22"></a>

- **Document ID**: `DOC-CART-20260922-22`
- **Date**: 2026-09-22
- **Author**: William Miller (`M-023`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-105`](https://jira.northstar.invalid/browse/CART-105)
- **Record Type**: Integration Review Notes

#### Context & Technical Objective
During iteration delivery on [CART-105] (Cart currency conversion with cached FX exchange rates - Phase 9), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260923-23] Cart & Promotions: Daily Standup & Blocker Log #23 (2026-09-23)
<a id="doc-cart-20260923-23"></a>

- **Document ID**: `DOC-CART-20260923-23`
- **Date**: 2026-09-23
- **Author**: Grace Wilson (`M-009`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-105`](https://jira.northstar.invalid/browse/CART-105)
- **Record Type**: Daily Standup & Blocker Log

#### Context & Technical Objective
During iteration delivery on [CART-105] (Cart currency conversion with cached FX exchange rates - Phase 9), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260924-24] Cart & Promotions: API Contract Revision #24 (2026-09-24)
<a id="doc-cart-20260924-24"></a>

- **Document ID**: `DOC-CART-20260924-24`
- **Date**: 2026-09-24
- **Author**: Jordan Lee (`M-002`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-102`](https://jira.northstar.invalid/browse/CART-102)
- **Record Type**: API Contract Revision

#### Context & Technical Objective
During iteration delivery on [CART-102] (Immutable cart audit transition event logging - Phase 9), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260924-25] Cart & Promotions: Database Migration Checklist #25 (2026-09-24)
<a id="doc-cart-20260924-25"></a>

- **Document ID**: `DOC-CART-20260924-25`
- **Date**: 2026-09-24
- **Author**: Owen Garcia (`M-010`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-118`](https://jira.northstar.invalid/browse/CART-118)
- **Record Type**: Database Migration Checklist

#### Context & Technical Objective
During iteration delivery on [CART-118] (Cart coupon eligibility against customer group rules - Phase 10), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260925-26] Cart & Promotions: Daily Standup & Blocker Log #26 (2026-09-25)
<a id="doc-cart-20260925-26"></a>

- **Document ID**: `DOC-CART-20260925-26`
- **Date**: 2026-09-25
- **Author**: Lily Perez (`M-059`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-115`](https://jira.northstar.invalid/browse/CART-115)
- **Record Type**: Daily Standup & Blocker Log

#### Context & Technical Objective
During iteration delivery on [CART-115] (Fixed-amount and percentage tier coupon discounts - Phase 10), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260928-27] Cart & Promotions: API Contract Revision #27 (2026-09-28)
<a id="doc-cart-20260928-27"></a>

- **Document ID**: `DOC-CART-20260928-27`
- **Date**: 2026-09-28
- **Author**: William Miller (`M-023`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-100`](https://jira.northstar.invalid/browse/CART-100)
- **Record Type**: API Contract Revision

#### Context & Technical Objective
During iteration delivery on [CART-100] (Order line total recalculation after real-time inventory adjustments - Phase 9), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260929-28] Cart & Promotions: Incident Post-Mortem Action #28 (2026-09-29)
<a id="doc-cart-20260929-28"></a>

- **Document ID**: `DOC-CART-20260929-28`
- **Date**: 2026-09-29
- **Author**: Grace Wilson (`M-009`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-096`](https://jira.northstar.invalid/browse/CART-096)
- **Record Type**: Incident Post-Mortem Action

#### Context & Technical Objective
During iteration delivery on [CART-096] (Bundle product component price breakdown in cart session - Phase 8), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260929-29] Cart & Promotions: Merchant Sync Decision #29 (2026-09-29)
<a id="doc-cart-20260929-29"></a>

- **Document ID**: `DOC-CART-20260929-29`
- **Date**: 2026-09-29
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-112`](https://jira.northstar.invalid/browse/CART-112)
- **Record Type**: Merchant Sync Decision

#### Context & Technical Objective
During iteration delivery on [CART-112] (Order line total recalculation after real-time inventory adjustments - Phase 10), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260930-30] Cart & Promotions: Architecture Decision Note #30 (2026-09-30)
<a id="doc-cart-20260930-30"></a>

- **Document ID**: `DOC-CART-20260930-30`
- **Date**: 2026-09-30
- **Author**: Owen Garcia (`M-010`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-109`](https://jira.northstar.invalid/browse/CART-109)
- **Record Type**: Architecture Decision Note

#### Context & Technical Objective
During iteration delivery on [CART-109] (Guest cart merging into customer account upon login - Phase 10), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---
