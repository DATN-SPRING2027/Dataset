---
bundle_id: "BUNDLE-NSC-CART-2026-08"
project_id: "NSC-CART"
project_name: "Cart & Promotions"
period: "2026-08"
classification: "Internal"
access_groups: ["GRP-CART"]
logical_document_count: 28
synthetic: true
---

# Cart & Promotions — Monthly Engineering Records (2026-08)

This Markdown bundle organizes 28 verified logical project records, decisions, meeting outcomes, and technical milestone updates for NSC-CART during 2026-08.

### [DOC-CART-20260803-01] Cart & Promotions: Performance Benchmark Report #1 (2026-08-03)
<a id="doc-cart-20260803-01"></a>

- **Document ID**: `DOC-CART-20260803-01`
- **Date**: 2026-08-03
- **Author**: Lily Perez (`M-059`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-066`](https://jira.northstar.invalid/browse/CART-066)
- **Record Type**: Performance Benchmark Report

#### Context & Technical Objective
During iteration delivery on [CART-066] (Immutable cart audit transition event logging - Phase 6), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260804-02] Cart & Promotions: Sprint Planning Update #2 (2026-08-04)
<a id="doc-cart-20260804-02"></a>

- **Document ID**: `DOC-CART-20260804-02`
- **Date**: 2026-08-04
- **Author**: William Miller (`M-023`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-063`](https://jira.northstar.invalid/browse/CART-063)
- **Record Type**: Sprint Planning Update

#### Context & Technical Objective
During iteration delivery on [CART-063] (Abandoned cart expiration workflow with automated stock release - Phase 6), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260804-03] Cart & Promotions: Feature Rollout Milestone #3 (2026-08-04)
<a id="doc-cart-20260804-03"></a>

- **Document ID**: `DOC-CART-20260804-03`
- **Date**: 2026-08-04
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-079`](https://jira.northstar.invalid/browse/CART-079)
- **Record Type**: Feature Rollout Milestone

#### Context & Technical Objective
During iteration delivery on [CART-079] (Fixed-amount and percentage tier coupon discounts - Phase 7), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260805-04] Cart & Promotions: Performance Benchmark Report #4 (2026-08-05)
<a id="doc-cart-20260805-04"></a>

- **Document ID**: `DOC-CART-20260805-04`
- **Date**: 2026-08-05
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-076`](https://jira.northstar.invalid/browse/CART-076)
- **Record Type**: Performance Benchmark Report

#### Context & Technical Objective
During iteration delivery on [CART-076] (Order line total recalculation after real-time inventory adjustments - Phase 7), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260806-05] Cart & Promotions: Sprint Planning Update #5 (2026-08-06)
<a id="doc-cart-20260806-05"></a>

- **Document ID**: `DOC-CART-20260806-05`
- **Date**: 2026-08-06
- **Author**: Owen Garcia (`M-010`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-073`](https://jira.northstar.invalid/browse/CART-073)
- **Record Type**: Sprint Planning Update

#### Context & Technical Objective
During iteration delivery on [CART-073] (Guest cart merging into customer account upon login - Phase 7), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260807-06] Cart & Promotions: Regression Test Summary #6 (2026-08-07)
<a id="doc-cart-20260807-06"></a>

- **Document ID**: `DOC-CART-20260807-06`
- **Date**: 2026-08-07
- **Author**: Jordan Lee (`M-002`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-089`](https://jira.northstar.invalid/browse/CART-089)
- **Record Type**: Regression Test Summary

#### Context & Technical Objective
During iteration delivery on [CART-089] (Idempotent cart item updates during concurrent requests - Phase 8), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260810-07] Cart & Promotions: Integration Review Notes #7 (2026-08-10)
<a id="doc-cart-20260810-07"></a>

- **Document ID**: `DOC-CART-20260810-07`
- **Date**: 2026-08-10
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-070`](https://jira.northstar.invalid/browse/CART-070)
- **Record Type**: Integration Review Notes

#### Context & Technical Objective
During iteration delivery on [CART-070] (Cart coupon eligibility against customer group rules - Phase 6), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260811-08] Cart & Promotions: Security Review Note #8 (2026-08-11)
<a id="doc-cart-20260811-08"></a>

- **Document ID**: `DOC-CART-20260811-08`
- **Date**: 2026-08-11
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-071`](https://jira.northstar.invalid/browse/CART-071)
- **Record Type**: Security Review Note

#### Context & Technical Objective
During iteration delivery on [CART-071] (Cart session TTL extension on user checkout interaction - Phase 6), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260811-09] Cart & Promotions: Regression Test Summary #9 (2026-08-11)
<a id="doc-cart-20260811-09"></a>

- **Document ID**: `DOC-CART-20260811-09`
- **Date**: 2026-08-11
- **Author**: William Miller (`M-023`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-087`](https://jira.northstar.invalid/browse/CART-087)
- **Record Type**: Regression Test Summary

#### Context & Technical Objective
During iteration delivery on [CART-087] (Abandoned cart expiration workflow with automated stock release - Phase 8), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260812-10] Cart & Promotions: Integration Review Notes #10 (2026-08-12)
<a id="doc-cart-20260812-10"></a>

- **Document ID**: `DOC-CART-20260812-10`
- **Date**: 2026-08-12
- **Author**: Grace Wilson (`M-009`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-084`](https://jira.northstar.invalid/browse/CART-084)
- **Record Type**: Integration Review Notes

#### Context & Technical Objective
During iteration delivery on [CART-084] (Bundle product component price breakdown in cart session - Phase 7), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260813-11] Cart & Promotions: Daily Standup & Blocker Log #11 (2026-08-13)
<a id="doc-cart-20260813-11"></a>

- **Document ID**: `DOC-CART-20260813-11`
- **Date**: 2026-08-13
- **Author**: Jordan Lee (`M-002`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-080`](https://jira.northstar.invalid/browse/CART-080)
- **Record Type**: Daily Standup & Blocker Log

#### Context & Technical Objective
During iteration delivery on [CART-080] (Merchant cart item maximum quantity limit constraints - Phase 7), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260814-12] Cart & Promotions: API Contract Revision #12 (2026-08-14)
<a id="doc-cart-20260814-12"></a>

- **Document ID**: `DOC-CART-20260814-12`
- **Date**: 2026-08-14
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-077`](https://jira.northstar.invalid/browse/CART-077)
- **Record Type**: API Contract Revision

#### Context & Technical Objective
During iteration delivery on [CART-077] (Idempotent cart item updates during concurrent requests - Phase 7), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260814-13] Cart & Promotions: Database Migration Checklist #13 (2026-08-14)
<a id="doc-cart-20260814-13"></a>

- **Document ID**: `DOC-CART-20260814-13`
- **Date**: 2026-08-14
- **Author**: Lily Perez (`M-059`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-093`](https://jira.northstar.invalid/browse/CART-093)
- **Record Type**: Database Migration Checklist

#### Context & Technical Objective
During iteration delivery on [CART-093] (Cart currency conversion with cached FX exchange rates - Phase 8), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260817-14] Cart & Promotions: Daily Standup & Blocker Log #14 (2026-08-17)
<a id="doc-cart-20260817-14"></a>

- **Document ID**: `DOC-CART-20260817-14`
- **Date**: 2026-08-17
- **Author**: William Miller (`M-023`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-078`](https://jira.northstar.invalid/browse/CART-078)
- **Record Type**: Daily Standup & Blocker Log

#### Context & Technical Objective
During iteration delivery on [CART-078] (Immutable cart audit transition event logging - Phase 7), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260818-15] Cart & Promotions: Architecture Decision Note #15 (2026-08-18)
<a id="doc-cart-20260818-15"></a>

- **Document ID**: `DOC-CART-20260818-15`
- **Date**: 2026-08-18
- **Author**: Grace Wilson (`M-009`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-074`](https://jira.northstar.invalid/browse/CART-074)
- **Record Type**: Architecture Decision Note

#### Context & Technical Objective
During iteration delivery on [CART-074] (Promotion stacking hierarchy and discount evaluation engine - Phase 7), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260818-16] Cart & Promotions: Incident Post-Mortem Action #16 (2026-08-18)
<a id="doc-cart-20260818-16"></a>

- **Document ID**: `DOC-CART-20260818-16`
- **Date**: 2026-08-18
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-090`](https://jira.northstar.invalid/browse/CART-090)
- **Record Type**: Incident Post-Mortem Action

#### Context & Technical Objective
During iteration delivery on [CART-090] (Immutable cart audit transition event logging - Phase 8), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260819-17] Cart & Promotions: Merchant Sync Decision #17 (2026-08-19)
<a id="doc-cart-20260819-17"></a>

- **Document ID**: `DOC-CART-20260819-17`
- **Date**: 2026-08-19
- **Author**: Owen Garcia (`M-010`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-087`](https://jira.northstar.invalid/browse/CART-087)
- **Record Type**: Merchant Sync Decision

#### Context & Technical Objective
During iteration delivery on [CART-087] (Abandoned cart expiration workflow with automated stock release - Phase 8), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260820-18] Cart & Promotions: Architecture Decision Note #18 (2026-08-20)
<a id="doc-cart-20260820-18"></a>

- **Document ID**: `DOC-CART-20260820-18`
- **Date**: 2026-08-20
- **Author**: Lily Perez (`M-059`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-088`](https://jira.northstar.invalid/browse/CART-088)
- **Record Type**: Architecture Decision Note

#### Context & Technical Objective
During iteration delivery on [CART-088] (Order line total recalculation after real-time inventory adjustments - Phase 8), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260821-19] Cart & Promotions: Incident Post-Mortem Action #19 (2026-08-21)
<a id="doc-cart-20260821-19"></a>

- **Document ID**: `DOC-CART-20260821-19`
- **Date**: 2026-08-21
- **Author**: William Miller (`M-023`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-085`](https://jira.northstar.invalid/browse/CART-085)
- **Record Type**: Incident Post-Mortem Action

#### Context & Technical Objective
During iteration delivery on [CART-085] (Guest cart merging into customer account upon login - Phase 8), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260821-20] Cart & Promotions: Merchant Sync Decision #20 (2026-08-21)
<a id="doc-cart-20260821-20"></a>

- **Document ID**: `DOC-CART-20260821-20`
- **Date**: 2026-08-21
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-101`](https://jira.northstar.invalid/browse/CART-101)
- **Record Type**: Merchant Sync Decision

#### Context & Technical Objective
During iteration delivery on [CART-101] (Idempotent cart item updates during concurrent requests - Phase 9), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260824-21] Cart & Promotions: Sprint Planning Update #21 (2026-08-24)
<a id="doc-cart-20260824-21"></a>

- **Document ID**: `DOC-CART-20260824-21`
- **Date**: 2026-08-24
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-085`](https://jira.northstar.invalid/browse/CART-085)
- **Record Type**: Sprint Planning Update

#### Context & Technical Objective
During iteration delivery on [CART-085] (Guest cart merging into customer account upon login - Phase 8), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260825-22] Cart & Promotions: Feature Rollout Milestone #22 (2026-08-25)
<a id="doc-cart-20260825-22"></a>

- **Document ID**: `DOC-CART-20260825-22`
- **Date**: 2026-08-25
- **Author**: Owen Garcia (`M-010`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-082`](https://jira.northstar.invalid/browse/CART-082)
- **Record Type**: Feature Rollout Milestone

#### Context & Technical Objective
During iteration delivery on [CART-082] (Cart coupon eligibility against customer group rules - Phase 7), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260826-23] Cart & Promotions: Performance Benchmark Report #23 (2026-08-26)
<a id="doc-cart-20260826-23"></a>

- **Document ID**: `DOC-CART-20260826-23`
- **Date**: 2026-08-26
- **Author**: Lily Perez (`M-059`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-079`](https://jira.northstar.invalid/browse/CART-079)
- **Record Type**: Performance Benchmark Report

#### Context & Technical Objective
During iteration delivery on [CART-079] (Fixed-amount and percentage tier coupon discounts - Phase 7), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260826-24] Cart & Promotions: Sprint Planning Update #24 (2026-08-26)
<a id="doc-cart-20260826-24"></a>

- **Document ID**: `DOC-CART-20260826-24`
- **Date**: 2026-08-26
- **Author**: Jordan Lee (`M-002`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-095`](https://jira.northstar.invalid/browse/CART-095)
- **Record Type**: Sprint Planning Update

#### Context & Technical Objective
During iteration delivery on [CART-095] (Cart session TTL extension on user checkout interaction - Phase 8), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260827-25] Cart & Promotions: Feature Rollout Milestone #25 (2026-08-27)
<a id="doc-cart-20260827-25"></a>

- **Document ID**: `DOC-CART-20260827-25`
- **Date**: 2026-08-27
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-092`](https://jira.northstar.invalid/browse/CART-092)
- **Record Type**: Feature Rollout Milestone

#### Context & Technical Objective
During iteration delivery on [CART-092] (Merchant cart item maximum quantity limit constraints - Phase 8), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260828-26] Cart & Promotions: Regression Test Summary #26 (2026-08-28)
<a id="doc-cart-20260828-26"></a>

- **Document ID**: `DOC-CART-20260828-26`
- **Date**: 2026-08-28
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-092`](https://jira.northstar.invalid/browse/CART-092)
- **Record Type**: Regression Test Summary

#### Context & Technical Objective
During iteration delivery on [CART-092] (Merchant cart item maximum quantity limit constraints - Phase 8), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260828-27] Cart & Promotions: Integration Review Notes #27 (2026-08-28)
<a id="doc-cart-20260828-27"></a>

- **Document ID**: `DOC-CART-20260828-27`
- **Date**: 2026-08-28
- **Author**: William Miller (`M-023`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-108`](https://jira.northstar.invalid/browse/CART-108)
- **Record Type**: Integration Review Notes

#### Context & Technical Objective
During iteration delivery on [CART-108] (Bundle product component price breakdown in cart session - Phase 9), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260831-28] Cart & Promotions: Security Review Note #28 (2026-08-31)
<a id="doc-cart-20260831-28"></a>

- **Document ID**: `DOC-CART-20260831-28`
- **Date**: 2026-08-31
- **Author**: Grace Wilson (`M-009`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-089`](https://jira.northstar.invalid/browse/CART-089)
- **Record Type**: Security Review Note

#### Context & Technical Objective
During iteration delivery on [CART-089] (Idempotent cart item updates during concurrent requests - Phase 8), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---
