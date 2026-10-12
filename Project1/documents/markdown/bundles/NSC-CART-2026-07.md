---
bundle_id: "BUNDLE-NSC-CART-2026-07"
project_id: "NSC-CART"
project_name: "Cart & Promotions"
period: "2026-07"
classification: "Internal"
access_groups: ["GRP-ALL-STAFF"]
logical_document_count: 32
synthetic: true
---

# Cart & Promotions — Monthly Engineering Records (2026-07)

This Markdown bundle organizes 32 verified logical project records, decisions, meeting outcomes, and technical milestone updates for NSC-CART during 2026-07.

### [DOC-CART-20260701-01] Cart & Promotions: Security Review Note #1 (2026-07-01)
<a id="doc-cart-20260701-01"></a>

- **Document ID**: `DOC-CART-20260701-01`
- **Date**: 2026-07-01
- **Author**: Owen Garcia (`M-010`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-046`](https://jira.northstar.invalid/browse/CART-046)
- **Record Type**: Security Review Note

#### Context & Technical Objective
During iteration delivery on [CART-046] (Cart coupon eligibility against customer group rules - Phase 4), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260701-02] Cart & Promotions: Regression Test Summary #2 (2026-07-01)
<a id="doc-cart-20260701-02"></a>

- **Document ID**: `DOC-CART-20260701-02`
- **Date**: 2026-07-01
- **Author**: Grace Wilson (`M-009`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-062`](https://jira.northstar.invalid/browse/CART-062)
- **Record Type**: Regression Test Summary

#### Context & Technical Objective
During iteration delivery on [CART-062] (Promotion stacking hierarchy and discount evaluation engine - Phase 6), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260702-03] Cart & Promotions: Database Migration Checklist #3 (2026-07-02)
<a id="doc-cart-20260702-03"></a>

- **Document ID**: `DOC-CART-20260702-03`
- **Date**: 2026-07-02
- **Author**: Jordan Lee (`M-002`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-058`](https://jira.northstar.invalid/browse/CART-058)
- **Record Type**: Database Migration Checklist

#### Context & Technical Objective
During iteration delivery on [CART-058] (Cart coupon eligibility against customer group rules - Phase 5), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260703-04] Cart & Promotions: Daily Standup & Blocker Log #4 (2026-07-03)
<a id="doc-cart-20260703-04"></a>

- **Document ID**: `DOC-CART-20260703-04`
- **Date**: 2026-07-03
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-059`](https://jira.northstar.invalid/browse/CART-059)
- **Record Type**: Daily Standup & Blocker Log

#### Context & Technical Objective
During iteration delivery on [CART-059] (Cart session TTL extension on user checkout interaction - Phase 5), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260703-05] Cart & Promotions: API Contract Revision #5 (2026-07-03)
<a id="doc-cart-20260703-05"></a>

- **Document ID**: `DOC-CART-20260703-05`
- **Date**: 2026-07-03
- **Author**: Lily Perez (`M-059`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-075`](https://jira.northstar.invalid/browse/CART-075)
- **Record Type**: API Contract Revision

#### Context & Technical Objective
During iteration delivery on [CART-075] (Abandoned cart expiration workflow with automated stock release - Phase 7), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260706-06] Cart & Promotions: Database Migration Checklist #6 (2026-07-06)
<a id="doc-cart-20260706-06"></a>

- **Document ID**: `DOC-CART-20260706-06`
- **Date**: 2026-07-06
- **Author**: William Miller (`M-023`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-056`](https://jira.northstar.invalid/browse/CART-056)
- **Record Type**: Database Migration Checklist

#### Context & Technical Objective
During iteration delivery on [CART-056] (Merchant cart item maximum quantity limit constraints - Phase 5), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260707-07] Cart & Promotions: Daily Standup & Blocker Log #7 (2026-07-07)
<a id="doc-cart-20260707-07"></a>

- **Document ID**: `DOC-CART-20260707-07`
- **Date**: 2026-07-07
- **Author**: Grace Wilson (`M-009`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-053`](https://jira.northstar.invalid/browse/CART-053)
- **Record Type**: Daily Standup & Blocker Log

#### Context & Technical Objective
During iteration delivery on [CART-053] (Idempotent cart item updates during concurrent requests - Phase 5), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260708-08] Cart & Promotions: Architecture Decision Note #8 (2026-07-08)
<a id="doc-cart-20260708-08"></a>

- **Document ID**: `DOC-CART-20260708-08`
- **Date**: 2026-07-08
- **Author**: Jordan Lee (`M-002`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-053`](https://jira.northstar.invalid/browse/CART-053)
- **Record Type**: Architecture Decision Note

#### Context & Technical Objective
During iteration delivery on [CART-053] (Idempotent cart item updates during concurrent requests - Phase 5), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260708-09] Cart & Promotions: Incident Post-Mortem Action #9 (2026-07-08)
<a id="doc-cart-20260708-09"></a>

- **Document ID**: `DOC-CART-20260708-09`
- **Date**: 2026-07-08
- **Author**: Owen Garcia (`M-010`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-069`](https://jira.northstar.invalid/browse/CART-069)
- **Record Type**: Incident Post-Mortem Action

#### Context & Technical Objective
During iteration delivery on [CART-069] (Cart currency conversion with cached FX exchange rates - Phase 6), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260709-10] Cart & Promotions: Merchant Sync Decision #10 (2026-07-09)
<a id="doc-cart-20260709-10"></a>

- **Document ID**: `DOC-CART-20260709-10`
- **Date**: 2026-07-09
- **Author**: Lily Perez (`M-059`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-066`](https://jira.northstar.invalid/browse/CART-066)
- **Record Type**: Merchant Sync Decision

#### Context & Technical Objective
During iteration delivery on [CART-066] (Immutable cart audit transition event logging - Phase 6), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260710-11] Cart & Promotions: Architecture Decision Note #11 (2026-07-10)
<a id="doc-cart-20260710-11"></a>

- **Document ID**: `DOC-CART-20260710-11`
- **Date**: 2026-07-10
- **Author**: William Miller (`M-023`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-063`](https://jira.northstar.invalid/browse/CART-063)
- **Record Type**: Architecture Decision Note

#### Context & Technical Objective
During iteration delivery on [CART-063] (Abandoned cart expiration workflow with automated stock release - Phase 6), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260713-12] Cart & Promotions: Incident Post-Mortem Action #12 (2026-07-13)
<a id="doc-cart-20260713-12"></a>

- **Document ID**: `DOC-CART-20260713-12`
- **Date**: 2026-07-13
- **Author**: Grace Wilson (`M-009`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-048`](https://jira.northstar.invalid/browse/CART-048)
- **Record Type**: Incident Post-Mortem Action

#### Context & Technical Objective
During iteration delivery on [CART-048] (Bundle product component price breakdown in cart session - Phase 4), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260713-13] Cart & Promotions: Merchant Sync Decision #13 (2026-07-13)
<a id="doc-cart-20260713-13"></a>

- **Document ID**: `DOC-CART-20260713-13`
- **Date**: 2026-07-13
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-064`](https://jira.northstar.invalid/browse/CART-064)
- **Record Type**: Merchant Sync Decision

#### Context & Technical Objective
During iteration delivery on [CART-064] (Order line total recalculation after real-time inventory adjustments - Phase 6), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260714-14] Cart & Promotions: Sprint Planning Update #14 (2026-07-14)
<a id="doc-cart-20260714-14"></a>

- **Document ID**: `DOC-CART-20260714-14`
- **Date**: 2026-07-14
- **Author**: Owen Garcia (`M-010`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-060`](https://jira.northstar.invalid/browse/CART-060)
- **Record Type**: Sprint Planning Update

#### Context & Technical Objective
During iteration delivery on [CART-060] (Bundle product component price breakdown in cart session - Phase 5), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260715-15] Cart & Promotions: Feature Rollout Milestone #15 (2026-07-15)
<a id="doc-cart-20260715-15"></a>

- **Document ID**: `DOC-CART-20260715-15`
- **Date**: 2026-07-15
- **Author**: Lily Perez (`M-059`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-057`](https://jira.northstar.invalid/browse/CART-057)
- **Record Type**: Feature Rollout Milestone

#### Context & Technical Objective
During iteration delivery on [CART-057] (Cart currency conversion with cached FX exchange rates - Phase 5), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260715-16] Cart & Promotions: Performance Benchmark Report #16 (2026-07-15)
<a id="doc-cart-20260715-16"></a>

- **Document ID**: `DOC-CART-20260715-16`
- **Date**: 2026-07-15
- **Author**: Jordan Lee (`M-002`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-073`](https://jira.northstar.invalid/browse/CART-073)
- **Record Type**: Performance Benchmark Report

#### Context & Technical Objective
During iteration delivery on [CART-073] (Guest cart merging into customer account upon login - Phase 7), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260716-17] Cart & Promotions: Sprint Planning Update #17 (2026-07-16)
<a id="doc-cart-20260716-17"></a>

- **Document ID**: `DOC-CART-20260716-17`
- **Date**: 2026-07-16
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-074`](https://jira.northstar.invalid/browse/CART-074)
- **Record Type**: Sprint Planning Update

#### Context & Technical Objective
During iteration delivery on [CART-074] (Promotion stacking hierarchy and discount evaluation engine - Phase 7), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260717-18] Cart & Promotions: Security Review Note #18 (2026-07-17)
<a id="doc-cart-20260717-18"></a>

- **Document ID**: `DOC-CART-20260717-18`
- **Date**: 2026-07-17
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-070`](https://jira.northstar.invalid/browse/CART-070)
- **Record Type**: Security Review Note

#### Context & Technical Objective
During iteration delivery on [CART-070] (Cart coupon eligibility against customer group rules - Phase 6), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260720-19] Cart & Promotions: Regression Test Summary #19 (2026-07-20)
<a id="doc-cart-20260720-19"></a>

- **Document ID**: `DOC-CART-20260720-19`
- **Date**: 2026-07-20
- **Author**: Owen Garcia (`M-010`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-051`](https://jira.northstar.invalid/browse/CART-051)
- **Record Type**: Regression Test Summary

#### Context & Technical Objective
During iteration delivery on [CART-051] (Abandoned cart expiration workflow with automated stock release - Phase 5), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260720-20] Cart & Promotions: Integration Review Notes #20 (2026-07-20)
<a id="doc-cart-20260720-20"></a>

- **Document ID**: `DOC-CART-20260720-20`
- **Date**: 2026-07-20
- **Author**: Grace Wilson (`M-009`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-067`](https://jira.northstar.invalid/browse/CART-067)
- **Record Type**: Integration Review Notes

#### Context & Technical Objective
During iteration delivery on [CART-067] (Fixed-amount and percentage tier coupon discounts - Phase 6), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260721-21] Cart & Promotions: Security Review Note #21 (2026-07-21)
<a id="doc-cart-20260721-21"></a>

- **Document ID**: `DOC-CART-20260721-21`
- **Date**: 2026-07-21
- **Author**: Jordan Lee (`M-002`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-068`](https://jira.northstar.invalid/browse/CART-068)
- **Record Type**: Security Review Note

#### Context & Technical Objective
During iteration delivery on [CART-068] (Merchant cart item maximum quantity limit constraints - Phase 6), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260722-22] Cart & Promotions: Regression Test Summary #22 (2026-07-22)
<a id="doc-cart-20260722-22"></a>

- **Document ID**: `DOC-CART-20260722-22`
- **Date**: 2026-07-22
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-065`](https://jira.northstar.invalid/browse/CART-065)
- **Record Type**: Regression Test Summary

#### Context & Technical Objective
During iteration delivery on [CART-065] (Idempotent cart item updates during concurrent requests - Phase 6), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260723-23] Cart & Promotions: Database Migration Checklist #23 (2026-07-23)
<a id="doc-cart-20260723-23"></a>

- **Document ID**: `DOC-CART-20260723-23`
- **Date**: 2026-07-23
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-061`](https://jira.northstar.invalid/browse/CART-061)
- **Record Type**: Database Migration Checklist

#### Context & Technical Objective
During iteration delivery on [CART-061] (Guest cart merging into customer account upon login - Phase 6), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260723-24] Cart & Promotions: Daily Standup & Blocker Log #24 (2026-07-23)
<a id="doc-cart-20260723-24"></a>

- **Document ID**: `DOC-CART-20260723-24`
- **Date**: 2026-07-23
- **Author**: William Miller (`M-023`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-077`](https://jira.northstar.invalid/browse/CART-077)
- **Record Type**: Daily Standup & Blocker Log

#### Context & Technical Objective
During iteration delivery on [CART-077] (Idempotent cart item updates during concurrent requests - Phase 7), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260724-25] Cart & Promotions: API Contract Revision #25 (2026-07-24)
<a id="doc-cart-20260724-25"></a>

- **Document ID**: `DOC-CART-20260724-25`
- **Date**: 2026-07-24
- **Author**: Grace Wilson (`M-009`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-074`](https://jira.northstar.invalid/browse/CART-074)
- **Record Type**: API Contract Revision

#### Context & Technical Objective
During iteration delivery on [CART-074] (Promotion stacking hierarchy and discount evaluation engine - Phase 7), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260727-26] Cart & Promotions: Database Migration Checklist #26 (2026-07-27)
<a id="doc-cart-20260727-26"></a>

- **Document ID**: `DOC-CART-20260727-26`
- **Date**: 2026-07-27
- **Author**: Jordan Lee (`M-002`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-059`](https://jira.northstar.invalid/browse/CART-059)
- **Record Type**: Database Migration Checklist

#### Context & Technical Objective
During iteration delivery on [CART-059] (Cart session TTL extension on user checkout interaction - Phase 5), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260727-27] Cart & Promotions: Daily Standup & Blocker Log #27 (2026-07-27)
<a id="doc-cart-20260727-27"></a>

- **Document ID**: `DOC-CART-20260727-27`
- **Date**: 2026-07-27
- **Author**: Owen Garcia (`M-010`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-075`](https://jira.northstar.invalid/browse/CART-075)
- **Record Type**: Daily Standup & Blocker Log

#### Context & Technical Objective
During iteration delivery on [CART-075] (Abandoned cart expiration workflow with automated stock release - Phase 7), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260728-28] Cart & Promotions: API Contract Revision #28 (2026-07-28)
<a id="doc-cart-20260728-28"></a>

- **Document ID**: `DOC-CART-20260728-28`
- **Date**: 2026-07-28
- **Author**: Lily Perez (`M-059`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-072`](https://jira.northstar.invalid/browse/CART-072)
- **Record Type**: API Contract Revision

#### Context & Technical Objective
During iteration delivery on [CART-072] (Bundle product component price breakdown in cart session - Phase 6), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260729-29] Cart & Promotions: Incident Post-Mortem Action #29 (2026-07-29)
<a id="doc-cart-20260729-29"></a>

- **Document ID**: `DOC-CART-20260729-29`
- **Date**: 2026-07-29
- **Author**: William Miller (`M-023`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-072`](https://jira.northstar.invalid/browse/CART-072)
- **Record Type**: Incident Post-Mortem Action

#### Context & Technical Objective
During iteration delivery on [CART-072] (Bundle product component price breakdown in cart session - Phase 6), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260730-30] Cart & Promotions: Merchant Sync Decision #30 (2026-07-30)
<a id="doc-cart-20260730-30"></a>

- **Document ID**: `DOC-CART-20260730-30`
- **Date**: 2026-07-30
- **Author**: Grace Wilson (`M-009`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-069`](https://jira.northstar.invalid/browse/CART-069)
- **Record Type**: Merchant Sync Decision

#### Context & Technical Objective
During iteration delivery on [CART-069] (Cart currency conversion with cached FX exchange rates - Phase 6), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260730-31] Cart & Promotions: Architecture Decision Note #31 (2026-07-30)
<a id="doc-cart-20260730-31"></a>

- **Document ID**: `DOC-CART-20260730-31`
- **Date**: 2026-07-30
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-085`](https://jira.northstar.invalid/browse/CART-085)
- **Record Type**: Architecture Decision Note

#### Context & Technical Objective
During iteration delivery on [CART-085] (Guest cart merging into customer account upon login - Phase 8), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260731-32] Cart & Promotions: Incident Post-Mortem Action #32 (2026-07-31)
<a id="doc-cart-20260731-32"></a>

- **Document ID**: `DOC-CART-20260731-32`
- **Date**: 2026-07-31
- **Author**: Owen Garcia (`M-010`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-082`](https://jira.northstar.invalid/browse/CART-082)
- **Record Type**: Incident Post-Mortem Action

#### Context & Technical Objective
During iteration delivery on [CART-082] (Cart coupon eligibility against customer group rules - Phase 7), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---
