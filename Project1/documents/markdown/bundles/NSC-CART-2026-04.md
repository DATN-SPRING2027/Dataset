---
bundle_id: "BUNDLE-NSC-CART-2026-04"
project_id: "NSC-CART"
project_name: "Cart & Promotions"
period: "2026-04"
classification: "Internal"
access_groups: ["GRP-CART"]
logical_document_count: 15
synthetic: true
---

# Cart & Promotions — Monthly Engineering Records (2026-04)

This Markdown bundle organizes 15 verified logical project records, decisions, meeting outcomes, and technical milestone updates for NSC-CART during 2026-04.

### [DOC-CART-20260416-01] Cart & Promotions: Merchant Sync Decision #1 (2026-04-16)
<a id="doc-cart-20260416-01"></a>

- **Document ID**: `DOC-CART-20260416-01`
- **Date**: 2026-04-16
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-002`](https://jira.northstar.invalid/browse/CART-002)
- **Record Type**: Merchant Sync Decision

#### Context & Technical Objective
During iteration delivery on [CART-002] (Promotion stacking hierarchy and discount evaluation engine), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260416-02] Cart & Promotions: Architecture Decision Note #2 (2026-04-16)
<a id="doc-cart-20260416-02"></a>

- **Document ID**: `DOC-CART-20260416-02`
- **Date**: 2026-04-16
- **Author**: Lily Perez (`M-059`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-002`](https://jira.northstar.invalid/browse/CART-002)
- **Record Type**: Architecture Decision Note

#### Context & Technical Objective
During iteration delivery on [CART-002] (Promotion stacking hierarchy and discount evaluation engine), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260417-03] Cart & Promotions: Incident Post-Mortem Action #3 (2026-04-17)
<a id="doc-cart-20260417-03"></a>

- **Document ID**: `DOC-CART-20260417-03`
- **Date**: 2026-04-17
- **Author**: William Miller (`M-023`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-003`](https://jira.northstar.invalid/browse/CART-003)
- **Record Type**: Incident Post-Mortem Action

#### Context & Technical Objective
During iteration delivery on [CART-003] (Abandoned cart expiration workflow with automated stock release), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260420-04] Cart & Promotions: Merchant Sync Decision #4 (2026-04-20)
<a id="doc-cart-20260420-04"></a>

- **Document ID**: `DOC-CART-20260420-04`
- **Date**: 2026-04-20
- **Author**: Grace Wilson (`M-009`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-002`](https://jira.northstar.invalid/browse/CART-002)
- **Record Type**: Merchant Sync Decision

#### Context & Technical Objective
During iteration delivery on [CART-002] (Promotion stacking hierarchy and discount evaluation engine), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260421-05] Cart & Promotions: Architecture Decision Note #5 (2026-04-21)
<a id="doc-cart-20260421-05"></a>

- **Document ID**: `DOC-CART-20260421-05`
- **Date**: 2026-04-21
- **Author**: Jordan Lee (`M-002`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-001`](https://jira.northstar.invalid/browse/CART-001)
- **Record Type**: Architecture Decision Note

#### Context & Technical Objective
During iteration delivery on [CART-001] (Guest cart merging into customer account upon login), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260421-06] Cart & Promotions: Incident Post-Mortem Action #6 (2026-04-21)
<a id="doc-cart-20260421-06"></a>

- **Document ID**: `DOC-CART-20260421-06`
- **Date**: 2026-04-21
- **Author**: Owen Garcia (`M-010`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-005`](https://jira.northstar.invalid/browse/CART-005)
- **Record Type**: Incident Post-Mortem Action

#### Context & Technical Objective
During iteration delivery on [CART-005] (Idempotent cart item updates during concurrent requests), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260422-07] Cart & Promotions: Performance Benchmark Report #7 (2026-04-22)
<a id="doc-cart-20260422-07"></a>

- **Document ID**: `DOC-CART-20260422-07`
- **Date**: 2026-04-22
- **Author**: Lily Perez (`M-059`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-001`](https://jira.northstar.invalid/browse/CART-001)
- **Record Type**: Performance Benchmark Report

#### Context & Technical Objective
During iteration delivery on [CART-001] (Guest cart merging into customer account upon login), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260423-08] Cart & Promotions: Sprint Planning Update #8 (2026-04-23)
<a id="doc-cart-20260423-08"></a>

- **Document ID**: `DOC-CART-20260423-08`
- **Date**: 2026-04-23
- **Author**: William Miller (`M-023`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-002`](https://jira.northstar.invalid/browse/CART-002)
- **Record Type**: Sprint Planning Update

#### Context & Technical Objective
During iteration delivery on [CART-002] (Promotion stacking hierarchy and discount evaluation engine), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260424-09] Cart & Promotions: Feature Rollout Milestone #9 (2026-04-24)
<a id="doc-cart-20260424-09"></a>

- **Document ID**: `DOC-CART-20260424-09`
- **Date**: 2026-04-24
- **Author**: Grace Wilson (`M-009`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-007`](https://jira.northstar.invalid/browse/CART-007)
- **Record Type**: Feature Rollout Milestone

#### Context & Technical Objective
During iteration delivery on [CART-007] (Fixed-amount and percentage tier coupon discounts), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260424-10] Cart & Promotions: Performance Benchmark Report #10 (2026-04-24)
<a id="doc-cart-20260424-10"></a>

- **Document ID**: `DOC-CART-20260424-10`
- **Date**: 2026-04-24
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-008`](https://jira.northstar.invalid/browse/CART-008)
- **Record Type**: Performance Benchmark Report

#### Context & Technical Objective
During iteration delivery on [CART-008] (Merchant cart item maximum quantity limit constraints), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260427-11] Cart & Promotions: Sprint Planning Update #11 (2026-04-27)
<a id="doc-cart-20260427-11"></a>

- **Document ID**: `DOC-CART-20260427-11`
- **Date**: 2026-04-27
- **Author**: Owen Garcia (`M-010`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-012`](https://jira.northstar.invalid/browse/CART-012)
- **Record Type**: Sprint Planning Update

#### Context & Technical Objective
During iteration delivery on [CART-012] (Bundle product component price breakdown in cart session), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260428-12] Cart & Promotions: Security Review Note #12 (2026-04-28)
<a id="doc-cart-20260428-12"></a>

- **Document ID**: `DOC-CART-20260428-12`
- **Date**: 2026-04-28
- **Author**: Lily Perez (`M-059`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-008`](https://jira.northstar.invalid/browse/CART-008)
- **Record Type**: Security Review Note

#### Context & Technical Objective
During iteration delivery on [CART-008] (Merchant cart item maximum quantity limit constraints), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260428-13] Cart & Promotions: Regression Test Summary #13 (2026-04-28)
<a id="doc-cart-20260428-13"></a>

- **Document ID**: `DOC-CART-20260428-13`
- **Date**: 2026-04-28
- **Author**: Jordan Lee (`M-002`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-003`](https://jira.northstar.invalid/browse/CART-003)
- **Record Type**: Regression Test Summary

#### Context & Technical Objective
During iteration delivery on [CART-003] (Abandoned cart expiration workflow with automated stock release), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260429-14] Cart & Promotions: Integration Review Notes #14 (2026-04-29)
<a id="doc-cart-20260429-14"></a>

- **Document ID**: `DOC-CART-20260429-14`
- **Date**: 2026-04-29
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-021`](https://jira.northstar.invalid/browse/CART-021)
- **Record Type**: Integration Review Notes

#### Context & Technical Objective
During iteration delivery on [CART-021] (Cart currency conversion with cached FX exchange rates - Phase 2), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260430-15] Cart & Promotions: Security Review Note #15 (2026-04-30)
<a id="doc-cart-20260430-15"></a>

- **Document ID**: `DOC-CART-20260430-15`
- **Date**: 2026-04-30
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-022`](https://jira.northstar.invalid/browse/CART-022)
- **Record Type**: Security Review Note

#### Context & Technical Objective
During iteration delivery on [CART-022] (Cart coupon eligibility against customer group rules - Phase 2), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---
