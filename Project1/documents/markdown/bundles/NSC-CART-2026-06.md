---
bundle_id: "BUNDLE-NSC-CART-2026-06"
project_id: "NSC-CART"
project_name: "Cart & Promotions"
period: "2026-06"
classification: "Internal"
access_groups: ["GRP-ALL-STAFF"]
logical_document_count: 28
synthetic: true
---

# Cart & Promotions — Monthly Engineering Records (2026-06)

This Markdown bundle organizes 28 verified logical project records, decisions, meeting outcomes, and technical milestone updates for NSC-CART during 2026-06.

### [DOC-CART-20260601-01] Cart & Promotions: Architecture Decision Note #1 (2026-06-01)
<a id="doc-cart-20260601-01"></a>

- **Document ID**: `DOC-CART-20260601-01`
- **Date**: 2026-06-01
- **Author**: Grace Wilson (`M-009`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-026`](https://jira.northstar.invalid/browse/CART-026)
- **Record Type**: Architecture Decision Note

#### Context & Technical Objective
During iteration delivery on [CART-026] (Promotion stacking hierarchy and discount evaluation engine - Phase 3), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260602-02] Cart & Promotions: Performance Benchmark Report #2 (2026-06-02)
<a id="doc-cart-20260602-02"></a>

- **Document ID**: `DOC-CART-20260602-02`
- **Date**: 2026-06-02
- **Author**: Owen Garcia (`M-010`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-038`](https://jira.northstar.invalid/browse/CART-038)
- **Record Type**: Performance Benchmark Report

#### Context & Technical Objective
During iteration delivery on [CART-038] (Promotion stacking hierarchy and discount evaluation engine - Phase 4), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260603-03] Cart & Promotions: Sprint Planning Update #3 (2026-06-03)
<a id="doc-cart-20260603-03"></a>

- **Document ID**: `DOC-CART-20260603-03`
- **Date**: 2026-06-03
- **Author**: Lily Perez (`M-059`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-039`](https://jira.northstar.invalid/browse/CART-039)
- **Record Type**: Sprint Planning Update

#### Context & Technical Objective
During iteration delivery on [CART-039] (Abandoned cart expiration workflow with automated stock release - Phase 4), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260604-04] Cart & Promotions: Feature Rollout Milestone #4 (2026-06-04)
<a id="doc-cart-20260604-04"></a>

- **Document ID**: `DOC-CART-20260604-04`
- **Date**: 2026-06-04
- **Author**: William Miller (`M-023`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-036`](https://jira.northstar.invalid/browse/CART-036)
- **Record Type**: Feature Rollout Milestone

#### Context & Technical Objective
During iteration delivery on [CART-036] (Bundle product component price breakdown in cart session - Phase 3), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260604-05] Cart & Promotions: Performance Benchmark Report #5 (2026-06-04)
<a id="doc-cart-20260604-05"></a>

- **Document ID**: `DOC-CART-20260604-05`
- **Date**: 2026-06-04
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-052`](https://jira.northstar.invalid/browse/CART-052)
- **Record Type**: Performance Benchmark Report

#### Context & Technical Objective
During iteration delivery on [CART-052] (Order line total recalculation after real-time inventory adjustments - Phase 5), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260605-06] Cart & Promotions: Sprint Planning Update #6 (2026-06-05)
<a id="doc-cart-20260605-06"></a>

- **Document ID**: `DOC-CART-20260605-06`
- **Date**: 2026-06-05
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-049`](https://jira.northstar.invalid/browse/CART-049)
- **Record Type**: Sprint Planning Update

#### Context & Technical Objective
During iteration delivery on [CART-049] (Guest cart merging into customer account upon login - Phase 5), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260608-07] Cart & Promotions: Security Review Note #7 (2026-06-08)
<a id="doc-cart-20260608-07"></a>

- **Document ID**: `DOC-CART-20260608-07`
- **Date**: 2026-06-08
- **Author**: Owen Garcia (`M-010`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-033`](https://jira.northstar.invalid/browse/CART-033)
- **Record Type**: Security Review Note

#### Context & Technical Objective
During iteration delivery on [CART-033] (Cart currency conversion with cached FX exchange rates - Phase 3), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260609-08] Cart & Promotions: Regression Test Summary #8 (2026-06-09)
<a id="doc-cart-20260609-08"></a>

- **Document ID**: `DOC-CART-20260609-08`
- **Date**: 2026-06-09
- **Author**: Lily Perez (`M-059`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-030`](https://jira.northstar.invalid/browse/CART-030)
- **Record Type**: Regression Test Summary

#### Context & Technical Objective
During iteration delivery on [CART-030] (Immutable cart audit transition event logging - Phase 3), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260609-09] Cart & Promotions: Integration Review Notes #9 (2026-06-09)
<a id="doc-cart-20260609-09"></a>

- **Document ID**: `DOC-CART-20260609-09`
- **Date**: 2026-06-09
- **Author**: Jordan Lee (`M-002`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-046`](https://jira.northstar.invalid/browse/CART-046)
- **Record Type**: Integration Review Notes

#### Context & Technical Objective
During iteration delivery on [CART-046] (Cart coupon eligibility against customer group rules - Phase 4), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260610-10] Cart & Promotions: Security Review Note #10 (2026-06-10)
<a id="doc-cart-20260610-10"></a>

- **Document ID**: `DOC-CART-20260610-10`
- **Date**: 2026-06-10
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-043`](https://jira.northstar.invalid/browse/CART-043)
- **Record Type**: Security Review Note

#### Context & Technical Objective
During iteration delivery on [CART-043] (Fixed-amount and percentage tier coupon discounts - Phase 4), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260611-11] Cart & Promotions: Regression Test Summary #11 (2026-06-11)
<a id="doc-cart-20260611-11"></a>

- **Document ID**: `DOC-CART-20260611-11`
- **Date**: 2026-06-11
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-040`](https://jira.northstar.invalid/browse/CART-040)
- **Record Type**: Regression Test Summary

#### Context & Technical Objective
During iteration delivery on [CART-040] (Order line total recalculation after real-time inventory adjustments - Phase 4), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260612-12] Cart & Promotions: Daily Standup & Blocker Log #12 (2026-06-12)
<a id="doc-cart-20260612-12"></a>

- **Document ID**: `DOC-CART-20260612-12`
- **Date**: 2026-06-12
- **Author**: Grace Wilson (`M-009`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-056`](https://jira.northstar.invalid/browse/CART-056)
- **Record Type**: Daily Standup & Blocker Log

#### Context & Technical Objective
During iteration delivery on [CART-056] (Merchant cart item maximum quantity limit constraints - Phase 5), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260615-13] Cart & Promotions: API Contract Revision #13 (2026-06-15)
<a id="doc-cart-20260615-13"></a>

- **Document ID**: `DOC-CART-20260615-13`
- **Date**: 2026-06-15
- **Author**: Jordan Lee (`M-002`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-037`](https://jira.northstar.invalid/browse/CART-037)
- **Record Type**: API Contract Revision

#### Context & Technical Objective
During iteration delivery on [CART-037] (Guest cart merging into customer account upon login - Phase 4), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260616-14] Cart & Promotions: Database Migration Checklist #14 (2026-06-16)
<a id="doc-cart-20260616-14"></a>

- **Document ID**: `DOC-CART-20260616-14`
- **Date**: 2026-06-16
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-038`](https://jira.northstar.invalid/browse/CART-038)
- **Record Type**: Database Migration Checklist

#### Context & Technical Objective
During iteration delivery on [CART-038] (Promotion stacking hierarchy and discount evaluation engine - Phase 4), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260616-15] Cart & Promotions: Daily Standup & Blocker Log #15 (2026-06-16)
<a id="doc-cart-20260616-15"></a>

- **Document ID**: `DOC-CART-20260616-15`
- **Date**: 2026-06-16
- **Author**: Lily Perez (`M-059`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-054`](https://jira.northstar.invalid/browse/CART-054)
- **Record Type**: Daily Standup & Blocker Log

#### Context & Technical Objective
During iteration delivery on [CART-054] (Immutable cart audit transition event logging - Phase 5), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260617-16] Cart & Promotions: Architecture Decision Note #16 (2026-06-17)
<a id="doc-cart-20260617-16"></a>

- **Document ID**: `DOC-CART-20260617-16`
- **Date**: 2026-06-17
- **Author**: William Miller (`M-023`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-050`](https://jira.northstar.invalid/browse/CART-050)
- **Record Type**: Architecture Decision Note

#### Context & Technical Objective
During iteration delivery on [CART-050] (Promotion stacking hierarchy and discount evaluation engine - Phase 5), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260618-17] Cart & Promotions: Incident Post-Mortem Action #17 (2026-06-18)
<a id="doc-cart-20260618-17"></a>

- **Document ID**: `DOC-CART-20260618-17`
- **Date**: 2026-06-18
- **Author**: Grace Wilson (`M-009`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-047`](https://jira.northstar.invalid/browse/CART-047)
- **Record Type**: Incident Post-Mortem Action

#### Context & Technical Objective
During iteration delivery on [CART-047] (Cart session TTL extension on user checkout interaction - Phase 4), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260619-18] Cart & Promotions: Merchant Sync Decision #18 (2026-06-19)
<a id="doc-cart-20260619-18"></a>

- **Document ID**: `DOC-CART-20260619-18`
- **Date**: 2026-06-19
- **Author**: Jordan Lee (`M-002`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-044`](https://jira.northstar.invalid/browse/CART-044)
- **Record Type**: Merchant Sync Decision

#### Context & Technical Objective
During iteration delivery on [CART-044] (Merchant cart item maximum quantity limit constraints - Phase 4), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260619-19] Cart & Promotions: Architecture Decision Note #19 (2026-06-19)
<a id="doc-cart-20260619-19"></a>

- **Document ID**: `DOC-CART-20260619-19`
- **Date**: 2026-06-19
- **Author**: Owen Garcia (`M-010`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-060`](https://jira.northstar.invalid/browse/CART-060)
- **Record Type**: Architecture Decision Note

#### Context & Technical Objective
During iteration delivery on [CART-060] (Bundle product component price breakdown in cart session - Phase 5), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260622-20] Cart & Promotions: Incident Post-Mortem Action #20 (2026-06-22)
<a id="doc-cart-20260622-20"></a>

- **Document ID**: `DOC-CART-20260622-20`
- **Date**: 2026-06-22
- **Author**: Lily Perez (`M-059`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-045`](https://jira.northstar.invalid/browse/CART-045)
- **Record Type**: Incident Post-Mortem Action

#### Context & Technical Objective
During iteration delivery on [CART-045] (Cart currency conversion with cached FX exchange rates - Phase 4), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260623-21] Cart & Promotions: Performance Benchmark Report #21 (2026-06-23)
<a id="doc-cart-20260623-21"></a>

- **Document ID**: `DOC-CART-20260623-21`
- **Date**: 2026-06-23
- **Author**: William Miller (`M-023`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-041`](https://jira.northstar.invalid/browse/CART-041)
- **Record Type**: Performance Benchmark Report

#### Context & Technical Objective
During iteration delivery on [CART-041] (Idempotent cart item updates during concurrent requests - Phase 4), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260623-22] Cart & Promotions: Sprint Planning Update #22 (2026-06-23)
<a id="doc-cart-20260623-22"></a>

- **Document ID**: `DOC-CART-20260623-22`
- **Date**: 2026-06-23
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-057`](https://jira.northstar.invalid/browse/CART-057)
- **Record Type**: Sprint Planning Update

#### Context & Technical Objective
During iteration delivery on [CART-057] (Cart currency conversion with cached FX exchange rates - Phase 5), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260624-23] Cart & Promotions: Feature Rollout Milestone #23 (2026-06-24)
<a id="doc-cart-20260624-23"></a>

- **Document ID**: `DOC-CART-20260624-23`
- **Date**: 2026-06-24
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-054`](https://jira.northstar.invalid/browse/CART-054)
- **Record Type**: Feature Rollout Milestone

#### Context & Technical Objective
During iteration delivery on [CART-054] (Immutable cart audit transition event logging - Phase 5), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260625-24] Cart & Promotions: Performance Benchmark Report #24 (2026-06-25)
<a id="doc-cart-20260625-24"></a>

- **Document ID**: `DOC-CART-20260625-24`
- **Date**: 2026-06-25
- **Author**: Owen Garcia (`M-010`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-055`](https://jira.northstar.invalid/browse/CART-055)
- **Record Type**: Performance Benchmark Report

#### Context & Technical Objective
During iteration delivery on [CART-055] (Fixed-amount and percentage tier coupon discounts - Phase 5), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260626-25] Cart & Promotions: Sprint Planning Update #25 (2026-06-26)
<a id="doc-cart-20260626-25"></a>

- **Document ID**: `DOC-CART-20260626-25`
- **Date**: 2026-06-26
- **Author**: Lily Perez (`M-059`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-052`](https://jira.northstar.invalid/browse/CART-052)
- **Record Type**: Sprint Planning Update

#### Context & Technical Objective
During iteration delivery on [CART-052] (Order line total recalculation after real-time inventory adjustments - Phase 5), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260626-26] Cart & Promotions: Feature Rollout Milestone #26 (2026-06-26)
<a id="doc-cart-20260626-26"></a>

- **Document ID**: `DOC-CART-20260626-26`
- **Date**: 2026-06-26
- **Author**: Jordan Lee (`M-002`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-068`](https://jira.northstar.invalid/browse/CART-068)
- **Record Type**: Feature Rollout Milestone

#### Context & Technical Objective
During iteration delivery on [CART-068] (Merchant cart item maximum quantity limit constraints - Phase 6), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260629-27] Cart & Promotions: Regression Test Summary #27 (2026-06-29)
<a id="doc-cart-20260629-27"></a>

- **Document ID**: `DOC-CART-20260629-27`
- **Date**: 2026-06-29
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-052`](https://jira.northstar.invalid/browse/CART-052)
- **Record Type**: Regression Test Summary

#### Context & Technical Objective
During iteration delivery on [CART-052] (Order line total recalculation after real-time inventory adjustments - Phase 5), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---

### [DOC-CART-20260630-28] Cart & Promotions: Integration Review Notes #28 (2026-06-30)
<a id="doc-cart-20260630-28"></a>

- **Document ID**: `DOC-CART-20260630-28`
- **Date**: 2026-06-30
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-ALL-STAFF`
- **Linked Issue**: [`CART-049`](https://jira.northstar.invalid/browse/CART-049)
- **Record Type**: Integration Review Notes

#### Context & Technical Objective
During iteration delivery on [CART-049] (Guest cart merging into customer account upon login - Phase 5), the Cart & Promotions engineering team evaluated operational telemetry, merchant workflow constraints, and data integrity guarantees. Work focused on preventing regressions under multi-tenant isolation.

#### Technical Decision & Invariants
The team approved architecture changes aligning with platform standards. All data mutations enforce row-level tenant filters, and asynchronous event workers maintain exactly-once idempotency semantics. Storage interactions preserve backward compatibility with active database partitions.

#### Verification & Evidence
Automated test suites passed in CI against synthetic test fixtures. Metric spans and correlation headers are emitted for all endpoints, confirming zero tenant leakage and stable p95 response latencies.

---
