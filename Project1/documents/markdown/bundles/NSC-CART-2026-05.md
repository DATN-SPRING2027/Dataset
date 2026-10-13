---
bundle_id: "BUNDLE-NSC-CART-2026-05"
project_id: "NSC-CART"
project_name: "Cart & Promotions"
period: "2026-05"
classification: "Internal"
access_groups: ["GRP-CART"]
logical_document_count: 29
synthetic: true
---

# Cart & Promotions — Monthly Engineering Records (2026-05)

This Markdown bundle organizes 29 verified logical project records, decisions, meeting outcomes, and technical milestone updates for NSC-CART during 2026-05.

### [DOC-CART-20260501-01] Cart & Promotions: API Contract Revision #1 (2026-05-01)
<a id="doc-cart-20260501-01"></a>

- **Document ID**: `DOC-CART-20260501-01`
- **Date**: 2026-05-01
- **Author**: Owen Garcia (`M-010`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-018`](https://jira.northstar.invalid/browse/CART-018)
- **Record Type**: API Contract Revision

#### Context & Technical Objective
During iteration delivery on [CART-018] (Immutable cart audit transition event logging - Phase 2), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260501-02] Cart & Promotions: Database Migration Checklist #2 (2026-05-01)
<a id="doc-cart-20260501-02"></a>

- **Document ID**: `DOC-CART-20260501-02`
- **Date**: 2026-05-01
- **Author**: Grace Wilson (`M-009`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-008`](https://jira.northstar.invalid/browse/CART-008)
- **Record Type**: Database Migration Checklist

#### Context & Technical Objective
During iteration delivery on [CART-008] (Merchant cart item maximum quantity limit constraints), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260504-03] Cart & Promotions: Daily Standup & Blocker Log #3 (2026-05-04)
<a id="doc-cart-20260504-03"></a>

- **Document ID**: `DOC-CART-20260504-03`
- **Date**: 2026-05-04
- **Author**: Jordan Lee (`M-002`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-019`](https://jira.northstar.invalid/browse/CART-019)
- **Record Type**: Daily Standup & Blocker Log

#### Context & Technical Objective
During iteration delivery on [CART-019] (Fixed-amount and percentage tier coupon discounts - Phase 2), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260505-04] Cart & Promotions: API Contract Revision #4 (2026-05-05)
<a id="doc-cart-20260505-04"></a>

- **Document ID**: `DOC-CART-20260505-04`
- **Date**: 2026-05-05
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-016`](https://jira.northstar.invalid/browse/CART-016)
- **Record Type**: API Contract Revision

#### Context & Technical Objective
During iteration delivery on [CART-016] (Order line total recalculation after real-time inventory adjustments - Phase 2), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260506-05] Cart & Promotions: Database Migration Checklist #5 (2026-05-06)
<a id="doc-cart-20260506-05"></a>

- **Document ID**: `DOC-CART-20260506-05`
- **Date**: 2026-05-06
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-013`](https://jira.northstar.invalid/browse/CART-013)
- **Record Type**: Database Migration Checklist

#### Context & Technical Objective
During iteration delivery on [CART-013] (Guest cart merging into customer account upon login - Phase 2), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260506-06] Cart & Promotions: Daily Standup & Blocker Log #6 (2026-05-06)
<a id="doc-cart-20260506-06"></a>

- **Document ID**: `DOC-CART-20260506-06`
- **Date**: 2026-05-06
- **Author**: William Miller (`M-023`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-029`](https://jira.northstar.invalid/browse/CART-029)
- **Record Type**: Daily Standup & Blocker Log

#### Context & Technical Objective
During iteration delivery on [CART-029] (Idempotent cart item updates during concurrent requests - Phase 3), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260507-07] Cart & Promotions: Architecture Decision Note #7 (2026-05-07)
<a id="doc-cart-20260507-07"></a>

- **Document ID**: `DOC-CART-20260507-07`
- **Date**: 2026-05-07
- **Author**: Grace Wilson (`M-009`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-025`](https://jira.northstar.invalid/browse/CART-025)
- **Record Type**: Architecture Decision Note

#### Context & Technical Objective
During iteration delivery on [CART-025] (Guest cart merging into customer account upon login - Phase 3), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260508-08] Cart & Promotions: Incident Post-Mortem Action #8 (2026-05-08)
<a id="doc-cart-20260508-08"></a>

- **Document ID**: `DOC-CART-20260508-08`
- **Date**: 2026-05-08
- **Author**: Jordan Lee (`M-002`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-026`](https://jira.northstar.invalid/browse/CART-026)
- **Record Type**: Incident Post-Mortem Action

#### Context & Technical Objective
During iteration delivery on [CART-026] (Promotion stacking hierarchy and discount evaluation engine - Phase 3), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260508-09] Cart & Promotions: Merchant Sync Decision #9 (2026-05-08)
<a id="doc-cart-20260508-09"></a>

- **Document ID**: `DOC-CART-20260508-09`
- **Date**: 2026-05-08
- **Author**: Owen Garcia (`M-010`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-004`](https://jira.northstar.invalid/browse/CART-004)
- **Record Type**: Merchant Sync Decision

#### Context & Technical Objective
During iteration delivery on [CART-004] (Order line total recalculation after real-time inventory adjustments), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260511-10] Cart & Promotions: Architecture Decision Note #10 (2026-05-11)
<a id="doc-cart-20260511-10"></a>

- **Document ID**: `DOC-CART-20260511-10`
- **Date**: 2026-05-11
- **Author**: Lily Perez (`M-059`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-023`](https://jira.northstar.invalid/browse/CART-023)
- **Record Type**: Architecture Decision Note

#### Context & Technical Objective
During iteration delivery on [CART-023] (Cart session TTL extension on user checkout interaction - Phase 2), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260512-11] Cart & Promotions: Incident Post-Mortem Action #11 (2026-05-12)
<a id="doc-cart-20260512-11"></a>

- **Document ID**: `DOC-CART-20260512-11`
- **Date**: 2026-05-12
- **Author**: William Miller (`M-023`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-020`](https://jira.northstar.invalid/browse/CART-020)
- **Record Type**: Incident Post-Mortem Action

#### Context & Technical Objective
During iteration delivery on [CART-020] (Merchant cart item maximum quantity limit constraints - Phase 2), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260513-12] Cart & Promotions: Performance Benchmark Report #12 (2026-05-13)
<a id="doc-cart-20260513-12"></a>

- **Document ID**: `DOC-CART-20260513-12`
- **Date**: 2026-05-13
- **Author**: Grace Wilson (`M-009`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-020`](https://jira.northstar.invalid/browse/CART-020)
- **Record Type**: Performance Benchmark Report

#### Context & Technical Objective
During iteration delivery on [CART-020] (Merchant cart item maximum quantity limit constraints - Phase 2), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260513-13] Cart & Promotions: Sprint Planning Update #13 (2026-05-13)
<a id="doc-cart-20260513-13"></a>

- **Document ID**: `DOC-CART-20260513-13`
- **Date**: 2026-05-13
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-036`](https://jira.northstar.invalid/browse/CART-036)
- **Record Type**: Sprint Planning Update

#### Context & Technical Objective
During iteration delivery on [CART-036] (Bundle product component price breakdown in cart session - Phase 3), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260514-14] Cart & Promotions: Feature Rollout Milestone #14 (2026-05-14)
<a id="doc-cart-20260514-14"></a>

- **Document ID**: `DOC-CART-20260514-14`
- **Date**: 2026-05-14
- **Author**: Owen Garcia (`M-010`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-033`](https://jira.northstar.invalid/browse/CART-033)
- **Record Type**: Feature Rollout Milestone

#### Context & Technical Objective
During iteration delivery on [CART-033] (Cart currency conversion with cached FX exchange rates - Phase 3), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260515-15] Cart & Promotions: Performance Benchmark Report #15 (2026-05-15)
<a id="doc-cart-20260515-15"></a>

- **Document ID**: `DOC-CART-20260515-15`
- **Date**: 2026-05-15
- **Author**: Lily Perez (`M-059`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-030`](https://jira.northstar.invalid/browse/CART-030)
- **Record Type**: Performance Benchmark Report

#### Context & Technical Objective
During iteration delivery on [CART-030] (Immutable cart audit transition event logging - Phase 3), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260518-16] Cart & Promotions: Integration Review Notes #16 (2026-05-18)
<a id="doc-cart-20260518-16"></a>

- **Document ID**: `DOC-CART-20260518-16`
- **Date**: 2026-05-18
- **Author**: William Miller (`M-023`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-014`](https://jira.northstar.invalid/browse/CART-014)
- **Record Type**: Integration Review Notes

#### Context & Technical Objective
During iteration delivery on [CART-014] (Promotion stacking hierarchy and discount evaluation engine - Phase 2), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260518-17] Cart & Promotions: Security Review Note #17 (2026-05-18)
<a id="doc-cart-20260518-17"></a>

- **Document ID**: `DOC-CART-20260518-17`
- **Date**: 2026-05-18
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-030`](https://jira.northstar.invalid/browse/CART-030)
- **Record Type**: Security Review Note

#### Context & Technical Objective
During iteration delivery on [CART-030] (Immutable cart audit transition event logging - Phase 3), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260519-18] Cart & Promotions: Regression Test Summary #18 (2026-05-19)
<a id="doc-cart-20260519-18"></a>

- **Document ID**: `DOC-CART-20260519-18`
- **Date**: 2026-05-19
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-027`](https://jira.northstar.invalid/browse/CART-027)
- **Record Type**: Regression Test Summary

#### Context & Technical Objective
During iteration delivery on [CART-027] (Abandoned cart expiration workflow with automated stock release - Phase 3), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260520-19] Cart & Promotions: Integration Review Notes #19 (2026-05-20)
<a id="doc-cart-20260520-19"></a>

- **Document ID**: `DOC-CART-20260520-19`
- **Date**: 2026-05-20
- **Author**: Owen Garcia (`M-010`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-024`](https://jira.northstar.invalid/browse/CART-024)
- **Record Type**: Integration Review Notes

#### Context & Technical Objective
During iteration delivery on [CART-024] (Bundle product component price breakdown in cart session - Phase 2), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260520-20] Cart & Promotions: Security Review Note #20 (2026-05-20)
<a id="doc-cart-20260520-20"></a>

- **Document ID**: `DOC-CART-20260520-20`
- **Date**: 2026-05-20
- **Author**: Grace Wilson (`M-009`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-040`](https://jira.northstar.invalid/browse/CART-040)
- **Record Type**: Security Review Note

#### Context & Technical Objective
During iteration delivery on [CART-040] (Order line total recalculation after real-time inventory adjustments - Phase 4), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260521-21] Cart & Promotions: Regression Test Summary #21 (2026-05-21)
<a id="doc-cart-20260521-21"></a>

- **Document ID**: `DOC-CART-20260521-21`
- **Date**: 2026-05-21
- **Author**: Jordan Lee (`M-002`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-041`](https://jira.northstar.invalid/browse/CART-041)
- **Record Type**: Regression Test Summary

#### Context & Technical Objective
During iteration delivery on [CART-041] (Idempotent cart item updates during concurrent requests - Phase 4), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260522-22] Cart & Promotions: Database Migration Checklist #22 (2026-05-22)
<a id="doc-cart-20260522-22"></a>

- **Document ID**: `DOC-CART-20260522-22`
- **Date**: 2026-05-22
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-037`](https://jira.northstar.invalid/browse/CART-037)
- **Record Type**: Database Migration Checklist

#### Context & Technical Objective
During iteration delivery on [CART-037] (Guest cart merging into customer account upon login - Phase 4), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260525-23] Cart & Promotions: Daily Standup & Blocker Log #23 (2026-05-25)
<a id="doc-cart-20260525-23"></a>

- **Document ID**: `DOC-CART-20260525-23`
- **Date**: 2026-05-25
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-018`](https://jira.northstar.invalid/browse/CART-018)
- **Record Type**: Daily Standup & Blocker Log

#### Context & Technical Objective
During iteration delivery on [CART-018] (Immutable cart audit transition event logging - Phase 2), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260525-24] Cart & Promotions: API Contract Revision #24 (2026-05-25)
<a id="doc-cart-20260525-24"></a>

- **Document ID**: `DOC-CART-20260525-24`
- **Date**: 2026-05-25
- **Author**: William Miller (`M-023`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-034`](https://jira.northstar.invalid/browse/CART-034)
- **Record Type**: API Contract Revision

#### Context & Technical Objective
During iteration delivery on [CART-034] (Cart coupon eligibility against customer group rules - Phase 3), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260526-25] Cart & Promotions: Database Migration Checklist #25 (2026-05-26)
<a id="doc-cart-20260526-25"></a>

- **Document ID**: `DOC-CART-20260526-25`
- **Date**: 2026-05-26
- **Author**: Grace Wilson (`M-009`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-035`](https://jira.northstar.invalid/browse/CART-035)
- **Record Type**: Database Migration Checklist

#### Context & Technical Objective
During iteration delivery on [CART-035] (Cart session TTL extension on user checkout interaction - Phase 3), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260527-26] Cart & Promotions: Daily Standup & Blocker Log #26 (2026-05-27)
<a id="doc-cart-20260527-26"></a>

- **Document ID**: `DOC-CART-20260527-26`
- **Date**: 2026-05-27
- **Author**: Jordan Lee (`M-002`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-032`](https://jira.northstar.invalid/browse/CART-032)
- **Record Type**: Daily Standup & Blocker Log

#### Context & Technical Objective
During iteration delivery on [CART-032] (Merchant cart item maximum quantity limit constraints - Phase 3), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260528-27] Cart & Promotions: Architecture Decision Note #27 (2026-05-28)
<a id="doc-cart-20260528-27"></a>

- **Document ID**: `DOC-CART-20260528-27`
- **Date**: 2026-05-28
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-028`](https://jira.northstar.invalid/browse/CART-028)
- **Record Type**: Architecture Decision Note

#### Context & Technical Objective
During iteration delivery on [CART-028] (Order line total recalculation after real-time inventory adjustments - Phase 3), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260528-28] Cart & Promotions: Incident Post-Mortem Action #28 (2026-05-28)
<a id="doc-cart-20260528-28"></a>

- **Document ID**: `DOC-CART-20260528-28`
- **Date**: 2026-05-28
- **Author**: Lily Perez (`M-059`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-044`](https://jira.northstar.invalid/browse/CART-044)
- **Record Type**: Incident Post-Mortem Action

#### Context & Technical Objective
During iteration delivery on [CART-044] (Merchant cart item maximum quantity limit constraints - Phase 4), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260529-29] Cart & Promotions: Merchant Sync Decision #29 (2026-05-29)
<a id="doc-cart-20260529-29"></a>

- **Document ID**: `DOC-CART-20260529-29`
- **Date**: 2026-05-29
- **Author**: William Miller (`M-023`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-041`](https://jira.northstar.invalid/browse/CART-041)
- **Record Type**: Merchant Sync Decision

#### Context & Technical Objective
During iteration delivery on [CART-041] (Idempotent cart item updates during concurrent requests - Phase 4), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---
