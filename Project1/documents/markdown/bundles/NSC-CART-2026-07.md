---
bundle_id: "BUNDLE-NSC-CART-2026-07"
project_id: "NSC-CART"
project_name: "Cart & Promotions"
period: "2026-07"
classification: "Internal"
access_groups: ["GRP-CART"]
logical_document_count: 33
synthetic: true
---

# Cart & Promotions — Monthly Engineering Records (2026-07)

This Markdown bundle organizes 33 verified logical project records, decisions, meeting outcomes, and technical milestone updates for NSC-CART during 2026-07.

### [DOC-CART-20260701-01] Cart & Promotions: Incident Post-Mortem Action #1 (2026-07-01)
<a id="doc-cart-20260701-01"></a>

- **Document ID**: `DOC-CART-20260701-01`
- **Date**: 2026-07-01 (`2026-07-01T16:24:23+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-038`](https://jira.northstar.invalid/browse/CART-038) (`Done`)
- **Record Type**: Incident Post-Mortem Action

#### Context & Technical Objective
Follow-up remediation tracking for [CART-038] (Promotion stacking hierarchy and discount evaluation engine — Edge-case race condition remediation) in Cart & Promotions after staging fault-injection and replay testing.

#### Technical Decision & Invariants
Added transactional outbox and unique inbox constraints so worker restarts or network retries cannot duplicate side effects.

#### Verification & Evidence
Crash-replay simulation added to continuous integration to prevent regression.

---

### [DOC-CART-20260701-02] Cart & Promotions: Merchant Sync Decision #2 (2026-07-01)
<a id="doc-cart-20260701-02"></a>

- **Document ID**: `DOC-CART-20260701-02`
- **Date**: 2026-07-01 (`2026-07-01T16:40:07+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-053`](https://jira.northstar.invalid/browse/CART-053) (`To Do`)
- **Record Type**: Merchant Sync Decision

#### Context & Technical Objective
Reviewed Meridian Outfitters pilot integration requirements for [CART-053] (Idempotent cart item updates during concurrent requests — Operational runbook & support diagnostics) with Cart & Promotions engineering and merchant support.

#### Technical Decision & Invariants
Confirmed tenant-isolated configuration rules, CSV batch error reporting, and SFTP nightly sync schedule at 02:00+07:00.

#### Verification & Evidence
Action items logged with merchant onboarding specialists and verified against tenant boundary checks.

---

### [DOC-CART-20260702-03] Cart & Promotions: Architecture Decision Note #3 (2026-07-02)
<a id="doc-cart-20260702-03"></a>

- **Document ID**: `DOC-CART-20260702-03`
- **Date**: 2026-07-02 (`2026-07-02T09:47:22+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-046`](https://jira.northstar.invalid/browse/CART-046) (`Done`)
- **Record Type**: Architecture Decision Note

#### Context & Technical Objective
Architectural review for [CART-046] (Cart coupon eligibility against customer group rules — Observability spans & SLO alert thresholds) within Cart & Promotions, focusing on service ownership boundaries, failure compensation, and multi-tenant isolation.

#### Technical Decision & Invariants
Enforced strict tenant_id scoping at the repository layer and durable 72-hour idempotency keys for mutating operations.

#### Verification & Evidence
Design aligns with DOC-ORG-SDS-001; contract tests and sequence diagrams validated by the tech lead.

---

### [DOC-CART-20260703-04] Cart & Promotions: Incident Post-Mortem Action #4 (2026-07-03)
<a id="doc-cart-20260703-04"></a>

- **Document ID**: `DOC-CART-20260703-04`
- **Date**: 2026-07-03 (`2026-07-03T11:54:37+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-044`](https://jira.northstar.invalid/browse/CART-044) (`To Do`)
- **Record Type**: Incident Post-Mortem Action

#### Context & Technical Objective
Follow-up remediation tracking for [CART-044] (Merchant cart item maximum quantity limit constraints — Merchant admin UI state & error boundary) in Cart & Promotions after staging fault-injection and replay testing.

#### Technical Decision & Invariants
Added transactional outbox and unique inbox constraints so worker restarts or network retries cannot duplicate side effects.

#### Verification & Evidence
Crash-replay simulation added to continuous integration to prevent regression.

---

### [DOC-CART-20260706-05] Cart & Promotions: Merchant Sync Decision #5 (2026-07-06)
<a id="doc-cart-20260706-05"></a>

- **Document ID**: `DOC-CART-20260706-05`
- **Date**: 2026-07-06 (`2026-07-06T14:05:52+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-036`](https://jira.northstar.invalid/browse/CART-036) (`To Do`)
- **Record Type**: Merchant Sync Decision

#### Context & Technical Objective
Reviewed Meridian Outfitters pilot integration requirements for [CART-036] (Bundle product component price breakdown in cart session — Partner sandbox contract reconciliation) with Cart & Promotions engineering and merchant support.

#### Technical Decision & Invariants
Confirmed tenant-isolated configuration rules, CSV batch error reporting, and SFTP nightly sync schedule at 02:00+07:00.

#### Verification & Evidence
Action items logged with merchant onboarding specialists and verified against tenant boundary checks.

---

### [DOC-CART-20260706-06] Cart & Promotions: Architecture Decision Note #6 (2026-07-06)
<a id="doc-cart-20260706-06"></a>

- **Document ID**: `DOC-CART-20260706-06`
- **Date**: 2026-07-06 (`2026-07-06T14:21:36+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-051`](https://jira.northstar.invalid/browse/CART-051) (`Done`)
- **Record Type**: Architecture Decision Note

#### Context & Technical Objective
Architectural review for [CART-051] (Abandoned cart expiration workflow with automated stock release — Boundary value & currency minor-unit validation) within Cart & Promotions, focusing on service ownership boundaries, failure compensation, and multi-tenant isolation.

#### Technical Decision & Invariants
Enforced strict tenant_id scoping at the repository layer and durable 72-hour idempotency keys for mutating operations.

#### Verification & Evidence
Design aligns with DOC-ORG-SDS-001; contract tests and sequence diagrams validated by the tech lead.

---

### [DOC-CART-20260707-07] Cart & Promotions: Incident Post-Mortem Action #7 (2026-07-07)
<a id="doc-cart-20260707-07"></a>

- **Document ID**: `DOC-CART-20260707-07`
- **Date**: 2026-07-07 (`2026-07-07T16:28:51+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-045`](https://jira.northstar.invalid/browse/CART-045) (`Done`)
- **Record Type**: Incident Post-Mortem Action

#### Context & Technical Objective
Follow-up remediation tracking for [CART-045] (Cart currency conversion with cached FX exchange rates — Webhook signature & payload verification) in Cart & Promotions after staging fault-injection and replay testing.

#### Technical Decision & Invariants
Added transactional outbox and unique inbox constraints so worker restarts or network retries cannot duplicate side effects.

#### Verification & Evidence
Crash-replay simulation added to continuous integration to prevent regression.

---

### [DOC-CART-20260708-08] Cart & Promotions: Daily Standup & Blocker Log #8 (2026-07-08)
<a id="doc-cart-20260708-08"></a>

- **Document ID**: `DOC-CART-20260708-08`
- **Date**: 2026-07-08 (`2026-07-08T10:40:15+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-044`](https://jira.northstar.invalid/browse/CART-044) (`To Do`)
- **Record Type**: Daily Standup & Blocker Log

#### Context & Technical Objective
Daily engineering standup checkpoint for Cart & Promotions covering active work on [CART-044] (Merchant cart item maximum quantity limit constraints — Merchant admin UI state & error boundary) (current ticket status: `To Do`).

#### Technical Decision & Invariants
Reviewed upstream sandbox dependencies, PR review queue, and evening overtime (17:00–22:00+07:00) handoffs during sprint crunch.

#### Verification & Evidence
Updated Jira status transitions, blocker owners, and same-day escalation checkpoints.

---

### [DOC-CART-20260708-09] Cart & Promotions: API Contract Revision #9 (2026-07-08)
<a id="doc-cart-20260708-09"></a>

- **Document ID**: `DOC-CART-20260708-09`
- **Date**: 2026-07-08 (`2026-07-08T20:09:51+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-059`](https://jira.northstar.invalid/browse/CART-059) (`In Progress`)
- **Record Type**: API Contract Revision

#### Context & Technical Objective
Evaluated HTTP request/response payload schemas for [CART-059] (Cart session TTL extension on user checkout interaction — Edge-case race condition remediation) in Cart & Promotions to ensure backward compatibility and deterministic error codes.

#### Technical Decision & Invariants
Standardized monetary fields to integer minor currency units alongside ISO 4217 currency codes; added explicit HTTP 409 conflict and HTTP 422 field validation responses.

#### Verification & Evidence
API schema snapshot tested against staging-sim consumer stubs with zero breaking changes.

---

### [DOC-CART-20260709-10] Cart & Promotions: Database Migration Checklist #10 (2026-07-09)
<a id="doc-cart-20260709-10"></a>

- **Document ID**: `DOC-CART-20260709-10`
- **Date**: 2026-07-09 (`2026-07-09T13:07:14+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-051`](https://jira.northstar.invalid/browse/CART-051) (`Done`)
- **Record Type**: Database Migration Checklist

#### Context & Technical Objective
Database schema change verification for [CART-051] (Abandoned cart expiration workflow with automated stock release — Boundary value & currency minor-unit validation) managed by Cart & Promotions.

#### Technical Decision & Invariants
Applied expand/contract migration sequencing: nullable/default columns and concurrent indexes deployed ahead of application readers/writers.

#### Verification & Evidence
Forward/down recovery notes and row-count reconciliation verified against isolated backup snapshot.

---

### [DOC-CART-20260710-11] Cart & Promotions: Daily Standup & Blocker Log #11 (2026-07-10)
<a id="doc-cart-20260710-11"></a>

- **Document ID**: `DOC-CART-20260710-11`
- **Date**: 2026-07-10 (`2026-07-10T15:14:29+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-049`](https://jira.northstar.invalid/browse/CART-049) (`Done`)
- **Record Type**: Daily Standup & Blocker Log

#### Context & Technical Objective
Daily engineering standup checkpoint for Cart & Promotions covering active work on [CART-049] (Guest cart merging into customer account upon login — Cache invalidation & version lineage check) (current ticket status: `Done`).

#### Technical Decision & Invariants
Reviewed upstream sandbox dependencies, PR review queue, and evening overtime (17:00–22:00+07:00) handoffs during sprint crunch.

#### Verification & Evidence
Updated Jira status transitions, blocker owners, and same-day escalation checkpoints.

---

### [DOC-CART-20260713-12] Cart & Promotions: API Contract Revision #12 (2026-07-13)
<a id="doc-cart-20260713-12"></a>

- **Document ID**: `DOC-CART-20260713-12`
- **Date**: 2026-07-13 (`2026-07-13T08:21:44+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-043`](https://jira.northstar.invalid/browse/CART-043) (`Done`)
- **Record Type**: API Contract Revision

#### Context & Technical Objective
Evaluated HTTP request/response payload schemas for [CART-043] (Fixed-amount and percentage tier coupon discounts — Redis distributed lock & concurrency handling) in Cart & Promotions to ensure backward compatibility and deterministic error codes.

#### Technical Decision & Invariants
Standardized monetary fields to integer minor currency units alongside ISO 4217 currency codes; added explicit HTTP 409 conflict and HTTP 422 field validation responses.

#### Verification & Evidence
API schema snapshot tested against staging-sim consumer stubs with zero breaking changes.

---

### [DOC-CART-20260713-13] Cart & Promotions: Database Migration Checklist #13 (2026-07-13)
<a id="doc-cart-20260713-13"></a>

- **Document ID**: `DOC-CART-20260713-13`
- **Date**: 2026-07-13 (`2026-07-13T08:37:28+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-058`](https://jira.northstar.invalid/browse/CART-058) (`Done`)
- **Record Type**: Database Migration Checklist

#### Context & Technical Objective
Database schema change verification for [CART-058] (Cart coupon eligibility against customer group rules — Database expand-contract migration script) managed by Cart & Promotions.

#### Technical Decision & Invariants
Applied expand/contract migration sequencing: nullable/default columns and concurrent indexes deployed ahead of application readers/writers.

#### Verification & Evidence
Forward/down recovery notes and row-count reconciliation verified against isolated backup snapshot.

---

### [DOC-CART-20260714-14] Cart & Promotions: Daily Standup & Blocker Log #14 (2026-07-14)
<a id="doc-cart-20260714-14"></a>

- **Document ID**: `DOC-CART-20260714-14`
- **Date**: 2026-07-14 (`2026-07-14T10:44:43+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-050`](https://jira.northstar.invalid/browse/CART-050) (`In Progress`)
- **Record Type**: Daily Standup & Blocker Log

#### Context & Technical Objective
Daily engineering standup checkpoint for Cart & Promotions covering active work on [CART-050] (Promotion stacking hierarchy and discount evaluation engine — Partner sandbox contract reconciliation) (current ticket status: `In Progress`).

#### Technical Decision & Invariants
Reviewed upstream sandbox dependencies, PR review queue, and evening overtime (17:00–22:00+07:00) handoffs during sprint crunch.

#### Verification & Evidence
Updated Jira status transitions, blocker owners, and same-day escalation checkpoints.

---

### [DOC-CART-20260715-15] Cart & Promotions: API Contract Revision #15 (2026-07-15)
<a id="doc-cart-20260715-15"></a>

- **Document ID**: `DOC-CART-20260715-15`
- **Date**: 2026-07-15 (`2026-07-15T13:51:58+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-048`](https://jira.northstar.invalid/browse/CART-048) (`Done`)
- **Record Type**: API Contract Revision

#### Context & Technical Objective
Evaluated HTTP request/response payload schemas for [CART-048] (Bundle product component price breakdown in cart session — Role-based access control policy enforcement) in Cart & Promotions to ensure backward compatibility and deterministic error codes.

#### Technical Decision & Invariants
Standardized monetary fields to integer minor currency units alongside ISO 4217 currency codes; added explicit HTTP 409 conflict and HTTP 422 field validation responses.

#### Verification & Evidence
API schema snapshot tested against staging-sim consumer stubs with zero breaking changes.

---

### [DOC-CART-20260715-16] Cart & Promotions: Database Migration Checklist #16 (2026-07-15)
<a id="doc-cart-20260715-16"></a>

- **Document ID**: `DOC-CART-20260715-16`
- **Date**: 2026-07-15 (`2026-07-15T17:22:24+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-063`](https://jira.northstar.invalid/browse/CART-063) (`Done`)
- **Record Type**: Database Migration Checklist

#### Context & Technical Objective
Database schema change verification for [CART-063] (Abandoned cart expiration workflow with automated stock release — Event outbox deduplication & ordering) managed by Cart & Promotions.

#### Technical Decision & Invariants
Applied expand/contract migration sequencing: nullable/default columns and concurrent indexes deployed ahead of application readers/writers.

#### Verification & Evidence
Forward/down recovery notes and row-count reconciliation verified against isolated backup snapshot.

---

### [DOC-CART-20260716-17] Cart & Promotions: Integration Review Notes #17 (2026-07-16)
<a id="doc-cart-20260716-17"></a>

- **Document ID**: `DOC-CART-20260716-17`
- **Date**: 2026-07-16 (`2026-07-16T16:07:22+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-043`](https://jira.northstar.invalid/browse/CART-043) (`Done`)
- **Record Type**: Integration Review Notes

#### Context & Technical Objective
Cross-service and partner integration sync for [CART-043] (Fixed-amount and percentage tier coupon discounts — Redis distributed lock & concurrency handling) in Cart & Promotions.

#### Technical Decision & Invariants
Verified HMAC-SHA256 webhook signature validation, bounded exponential backoff with jitter, and correlation ID propagation across service hops.

#### Verification & Evidence
Sandbox integration trace captured and linked to the requirement traceability matrix.

---

### [DOC-CART-20260716-18] Cart & Promotions: Security Review Note #18 (2026-07-16)
<a id="doc-cart-20260716-18"></a>

- **Document ID**: `DOC-CART-20260716-18`
- **Date**: 2026-07-16 (`2026-07-16T16:23:06+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-058`](https://jira.northstar.invalid/browse/CART-058) (`Done`)
- **Record Type**: Security Review Note

#### Context & Technical Objective
Application security and access-control assessment for [CART-058] (Cart coupon eligibility against customer group rules — Database expand-contract migration script) in Cart & Promotions.

#### Technical Decision & Invariants
Validated deny-by-default authorization, pre-retrieval ACL filtering, secret externalization, and zero persistence of PAN/CVV or raw credentials.

#### Verification & Evidence
AppSec sign-off recorded; negative cross-tenant and revoked-user probes passed in CI.

---

### [DOC-CART-20260717-19] Cart & Promotions: Regression Test Summary #19 (2026-07-17)
<a id="doc-cart-20260717-19"></a>

- **Document ID**: `DOC-CART-20260717-19`
- **Date**: 2026-07-17 (`2026-07-17T09:30:21+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-056`](https://jira.northstar.invalid/browse/CART-056) (`To Do`)
- **Record Type**: Regression Test Summary

#### Context & Technical Objective
Executed automated regression and negative boundary suite for [CART-056] (Merchant cart item maximum quantity limit constraints — Rate limiting & audit trail emission) across Cart & Promotions staging fixtures.

#### Technical Decision & Invariants
Verified idempotent replay, duplicate event suppression, and cross-tenant HTTP 403 rejection before snippet or count generation.

#### Verification & Evidence
All regression assertions recorded with deterministic seed=42 and correlation trace evidence attached.

---

### [DOC-CART-20260720-20] Cart & Promotions: Integration Review Notes #20 (2026-07-20)
<a id="doc-cart-20260720-20"></a>

- **Document ID**: `DOC-CART-20260720-20`
- **Date**: 2026-07-20 (`2026-07-20T11:37:36+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-048`](https://jira.northstar.invalid/browse/CART-048) (`Done`)
- **Record Type**: Integration Review Notes

#### Context & Technical Objective
Cross-service and partner integration sync for [CART-048] (Bundle product component price breakdown in cart session — Role-based access control policy enforcement) in Cart & Promotions.

#### Technical Decision & Invariants
Verified HMAC-SHA256 webhook signature validation, bounded exponential backoff with jitter, and correlation ID propagation across service hops.

#### Verification & Evidence
Sandbox integration trace captured and linked to the requirement traceability matrix.

---

### [DOC-CART-20260720-21] Cart & Promotions: Security Review Note #21 (2026-07-20)
<a id="doc-cart-20260720-21"></a>

- **Document ID**: `DOC-CART-20260720-21`
- **Date**: 2026-07-20 (`2026-07-20T19:16:10+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-063`](https://jira.northstar.invalid/browse/CART-063) (`Done`)
- **Record Type**: Security Review Note

#### Context & Technical Objective
Application security and access-control assessment for [CART-063] (Abandoned cart expiration workflow with automated stock release — Event outbox deduplication & ordering) in Cart & Promotions.

#### Technical Decision & Invariants
Validated deny-by-default authorization, pre-retrieval ACL filtering, secret externalization, and zero persistence of PAN/CVV or raw credentials.

#### Verification & Evidence
AppSec sign-off recorded; negative cross-tenant and revoked-user probes passed in CI.

---

### [DOC-CART-20260721-22] Cart & Promotions: Regression Test Summary #22 (2026-07-21)
<a id="doc-cart-20260721-22"></a>

- **Document ID**: `DOC-CART-20260721-22`
- **Date**: 2026-07-21 (`2026-07-21T14:04:35+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-061`](https://jira.northstar.invalid/browse/CART-061) (`Done`)
- **Record Type**: Regression Test Summary

#### Context & Technical Objective
Executed automated regression and negative boundary suite for [CART-061] (Guest cart merging into customer account upon login — Load test benchmark & p95 latency profiling) across Cart & Promotions staging fixtures.

#### Technical Decision & Invariants
Verified idempotent replay, duplicate event suppression, and cross-tenant HTTP 403 rejection before snippet or count generation.

#### Verification & Evidence
All regression assertions recorded with deterministic seed=42 and correlation trace evidence attached.

---

### [DOC-CART-20260722-23] Cart & Promotions: Integration Review Notes #23 (2026-07-22)
<a id="doc-cart-20260722-23"></a>

- **Document ID**: `DOC-CART-20260722-23`
- **Date**: 2026-07-22 (`2026-07-22T16:11:50+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-054`](https://jira.northstar.invalid/browse/CART-054) (`Done`)
- **Record Type**: Integration Review Notes

#### Context & Technical Objective
Cross-service and partner integration sync for [CART-054] (Immutable cart audit transition event logging — API contract & schema validation) in Cart & Promotions.

#### Technical Decision & Invariants
Verified HMAC-SHA256 webhook signature validation, bounded exponential backoff with jitter, and correlation ID propagation across service hops.

#### Verification & Evidence
Sandbox integration trace captured and linked to the requirement traceability matrix.

---

### [DOC-CART-20260723-24] Cart & Promotions: Security Review Note #24 (2026-07-23)
<a id="doc-cart-20260723-24"></a>

- **Document ID**: `DOC-CART-20260723-24`
- **Date**: 2026-07-23 (`2026-07-23T09:18:05+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-047`](https://jira.northstar.invalid/browse/CART-047) (`To Do`)
- **Record Type**: Security Review Note

#### Context & Technical Objective
Application security and access-control assessment for [CART-047] (Cart session TTL extension on user checkout interaction — Load test benchmark & p95 latency profiling) in Cart & Promotions.

#### Technical Decision & Invariants
Validated deny-by-default authorization, pre-retrieval ACL filtering, secret externalization, and zero persistence of PAN/CVV or raw credentials.

#### Verification & Evidence
AppSec sign-off recorded; negative cross-tenant and revoked-user probes passed in CI.

---

### [DOC-CART-20260723-25] Cart & Promotions: Regression Test Summary #25 (2026-07-23)
<a id="doc-cart-20260723-25"></a>

- **Document ID**: `DOC-CART-20260723-25`
- **Date**: 2026-07-23 (`2026-07-23T09:34:49+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-065`](https://jira.northstar.invalid/browse/CART-065) (`Done`)
- **Record Type**: Regression Test Summary

#### Context & Technical Objective
Executed automated regression and negative boundary suite for [CART-065] (Idempotent cart item updates during concurrent requests — Data retention & privacy masking compliance) across Cart & Promotions staging fixtures.

#### Technical Decision & Invariants
Verified idempotent replay, duplicate event suppression, and cross-tenant HTTP 403 rejection before snippet or count generation.

#### Verification & Evidence
All regression assertions recorded with deterministic seed=42 and correlation trace evidence attached.

---

### [DOC-CART-20260724-26] Cart & Promotions: Sprint Planning Update #26 (2026-07-24)
<a id="doc-cart-20260724-26"></a>

- **Document ID**: `DOC-CART-20260724-26`
- **Date**: 2026-07-24 (`2026-07-24T13:46:13+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-061`](https://jira.northstar.invalid/browse/CART-061) (`Done`)
- **Record Type**: Sprint Planning Update

#### Context & Technical Objective
During sprint backlog commitment on [CART-061] (Guest cart merging into customer account upon login — Load test benchmark & p95 latency profiling), the Cart & Promotions squad decomposed acceptance criteria, story point capacity, and cross-service dependencies.

#### Technical Decision & Invariants
Confirmed sprint scope and velocity guardrails. Unfinished items from prior closed iterations are formally tracked via sprint spillover transitions into the active sprint.

#### Verification & Evidence
Backlog readiness verified with product owner and QA lead; test fixtures and correlation IDs linked in Jira.

---

### [DOC-CART-20260727-27] Cart & Promotions: Feature Rollout Milestone #27 (2026-07-27)
<a id="doc-cart-20260727-27"></a>

- **Document ID**: `DOC-CART-20260727-27`
- **Date**: 2026-07-27 (`2026-07-27T15:53:28+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-054`](https://jira.northstar.invalid/browse/CART-054) (`Done`)
- **Record Type**: Feature Rollout Milestone

#### Context & Technical Objective
Staged canary rollout readiness check for [CART-054] (Immutable cart audit transition event logging — API contract & schema validation) in Cart & Promotions.

#### Technical Decision & Invariants
Configured feature flag toggle and progressive traffic gates (0% synthetic -> 5% -> 25% -> 50% -> 100%) with automated rollback triggers.

#### Verification & Evidence
On-call SRE and workstream owner verified rollback runbook steps and alert routing.

---

### [DOC-CART-20260728-28] Cart & Promotions: Performance Benchmark Report #28 (2026-07-28)
<a id="doc-cart-20260728-28"></a>

- **Document ID**: `DOC-CART-20260728-28`
- **Date**: 2026-07-28 (`2026-07-28T08:04:43+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-050`](https://jira.northstar.invalid/browse/CART-050) (`In Progress`)
- **Record Type**: Performance Benchmark Report

#### Context & Technical Objective
Conducted load and latency profiling for [CART-050] (Promotion stacking hierarchy and discount evaluation engine — Partner sandbox contract reconciliation) in Cart & Promotions under the pilot reference workload.

#### Technical Decision & Invariants
Tuned PostgreSQL composite indexes and Redis lock TTLs to keep p95 latency within the approved service-level objective.

#### Verification & Evidence
Measured p95 response times, connection pool saturation, and queue lag metrics on the staging telemetry dashboard.

---

### [DOC-CART-20260728-29] Cart & Promotions: Sprint Planning Update #29 (2026-07-28)
<a id="doc-cart-20260728-29"></a>

- **Document ID**: `DOC-CART-20260728-29`
- **Date**: 2026-07-28 (`2026-07-28T08:20:27+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-067`](https://jira.northstar.invalid/browse/CART-067) (`To Do`)
- **Record Type**: Sprint Planning Update

#### Context & Technical Objective
During sprint backlog commitment on [CART-067] (Fixed-amount and percentage tier coupon discounts — Integration test suite & staging replay), the Cart & Promotions squad decomposed acceptance criteria, story point capacity, and cross-service dependencies.

#### Technical Decision & Invariants
Confirmed sprint scope and velocity guardrails. Unfinished items from prior closed iterations are formally tracked via sprint spillover transitions into the active sprint.

#### Verification & Evidence
Backlog readiness verified with product owner and QA lead; test fixtures and correlation IDs linked in Jira.

---

### [DOC-CART-20260729-30] Cart & Promotions: Feature Rollout Milestone #30 (2026-07-29)
<a id="doc-cart-20260729-30"></a>

- **Document ID**: `DOC-CART-20260729-30`
- **Date**: 2026-07-29 (`2026-07-29T17:14:08+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-060`](https://jira.northstar.invalid/browse/CART-060) (`Done`)
- **Record Type**: Feature Rollout Milestone

#### Context & Technical Objective
Staged canary rollout readiness check for [CART-060] (Bundle product component price breakdown in cart session — Automated recovery & rollback verification) in Cart & Promotions.

#### Technical Decision & Invariants
Configured feature flag toggle and progressive traffic gates (0% synthetic -> 5% -> 25% -> 50% -> 100%) with automated rollback triggers.

#### Verification & Evidence
On-call SRE and workstream owner verified rollback runbook steps and alert routing.

---

### [DOC-CART-20260730-31] Cart & Promotions: Performance Benchmark Report #31 (2026-07-30)
<a id="doc-cart-20260730-31"></a>

- **Document ID**: `DOC-CART-20260730-31`
- **Date**: 2026-07-30 (`2026-07-30T13:34:57+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-053`](https://jira.northstar.invalid/browse/CART-053) (`In Progress`)
- **Record Type**: Performance Benchmark Report

#### Context & Technical Objective
Conducted load and latency profiling for [CART-053] (Idempotent cart item updates during concurrent requests — Operational runbook & support diagnostics) in Cart & Promotions under the pilot reference workload.

#### Technical Decision & Invariants
Tuned PostgreSQL composite indexes and Redis lock TTLs to keep p95 latency within the approved service-level objective.

#### Verification & Evidence
Measured p95 response times, connection pool saturation, and queue lag metrics on the staging telemetry dashboard.

---

### [DOC-CART-20260730-32] Cart & Promotions: Sprint Planning Update #32 (2026-07-30)
<a id="doc-cart-20260730-32"></a>

- **Document ID**: `DOC-CART-20260730-32`
- **Date**: 2026-07-30 (`2026-07-30T18:23:29+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-070`](https://jira.northstar.invalid/browse/CART-070) (`In Progress`)
- **Record Type**: Sprint Planning Update

#### Context & Technical Objective
During sprint backlog commitment on [CART-070] (Cart coupon eligibility against customer group rules — Cache invalidation & version lineage check), the Cart & Promotions squad decomposed acceptance criteria, story point capacity, and cross-service dependencies.

#### Technical Decision & Invariants
Confirmed sprint scope and velocity guardrails. Unfinished items from prior closed iterations are formally tracked via sprint spillover transitions into the active sprint.

#### Verification & Evidence
Backlog readiness verified with product owner and QA lead; test fixtures and correlation IDs linked in Jira.

---

### [DOC-CART-20260731-33] Cart & Promotions: Feature Rollout Milestone #33 (2026-07-31)
<a id="doc-cart-20260731-33"></a>

- **Document ID**: `DOC-CART-20260731-33`
- **Date**: 2026-07-31 (`2026-07-31T15:01:56+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-066`](https://jira.northstar.invalid/browse/CART-066) (`Done`)
- **Record Type**: Feature Rollout Milestone

#### Context & Technical Objective
Staged canary rollout readiness check for [CART-066] (Immutable cart audit transition event logging — PostgreSQL indexing & tenant query guard) in Cart & Promotions.

#### Technical Decision & Invariants
Configured feature flag toggle and progressive traffic gates (0% synthetic -> 5% -> 25% -> 50% -> 100%) with automated rollback triggers.

#### Verification & Evidence
On-call SRE and workstream owner verified rollback runbook steps and alert routing.

---
