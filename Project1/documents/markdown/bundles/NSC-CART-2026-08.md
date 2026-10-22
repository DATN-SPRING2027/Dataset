---
bundle_id: "BUNDLE-NSC-CART-2026-08"
project_id: "NSC-CART"
project_name: "Cart & Promotions"
period: "2026-08"
classification: "Internal"
access_groups: ["GRP-CART"]
logical_document_count: 29
synthetic: true
---

# Cart & Promotions — Monthly Engineering Records (2026-08)

This Markdown bundle organizes 29 verified logical project records, decisions, meeting outcomes, and technical milestone updates for NSC-CART during 2026-08.

### [DOC-CART-20260803-01] Cart & Promotions: Merchant Sync Decision #1 (2026-08-03)
<a id="doc-cart-20260803-01"></a>

- **Document ID**: `DOC-CART-20260803-01`
- **Date**: 2026-08-03 (`2026-08-03T09:13:20+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-062`](https://jira.northstar.invalid/browse/CART-062) (`Done`)
- **Record Type**: Merchant Sync Decision

#### Context & Technical Objective
Reviewed Meridian Outfitters pilot integration requirements for [CART-062] (Promotion stacking hierarchy and discount evaluation engine — Role-based access control policy enforcement) with Cart & Promotions engineering and merchant support.

#### Technical Decision & Invariants
Confirmed tenant-isolated configuration rules, CSV batch error reporting, and SFTP nightly sync schedule at 02:00+07:00.

#### Verification & Evidence
Action items logged with merchant onboarding specialists and verified against tenant boundary checks.

---

### [DOC-CART-20260804-02] Cart & Promotions: Architecture Decision Note #2 (2026-08-04)
<a id="doc-cart-20260804-02"></a>

- **Document ID**: `DOC-CART-20260804-02`
- **Date**: 2026-08-04 (`2026-08-04T11:20:35+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-057`](https://jira.northstar.invalid/browse/CART-057) (`Done`)
- **Record Type**: Architecture Decision Note

#### Context & Technical Objective
Architectural review for [CART-057] (Cart currency conversion with cached FX exchange rates — Timeout fallback & circuit breaker logic) within Cart & Promotions, focusing on service ownership boundaries, failure compensation, and multi-tenant isolation.

#### Technical Decision & Invariants
Enforced strict tenant_id scoping at the repository layer and durable 72-hour idempotency keys for mutating operations.

#### Verification & Evidence
Design aligns with DOC-ORG-SDS-001; contract tests and sequence diagrams validated by the tech lead.

---

### [DOC-CART-20260804-03] Cart & Promotions: Incident Post-Mortem Action #3 (2026-08-04)
<a id="doc-cart-20260804-03"></a>

- **Document ID**: `DOC-CART-20260804-03`
- **Date**: 2026-08-04 (`2026-08-04T11:36:19+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-073`](https://jira.northstar.invalid/browse/CART-073) (`In Review`)
- **Record Type**: Incident Post-Mortem Action

#### Context & Technical Objective
Follow-up remediation tracking for [CART-073] (Guest cart merging into customer account upon login — Edge-case race condition remediation) in Cart & Promotions after staging fault-injection and replay testing.

#### Technical Decision & Invariants
Added transactional outbox and unique inbox constraints so worker restarts or network retries cannot duplicate side effects.

#### Verification & Evidence
Crash-replay simulation added to continuous integration to prevent regression.

---

### [DOC-CART-20260805-04] Cart & Promotions: Merchant Sync Decision #4 (2026-08-05)
<a id="doc-cart-20260805-04"></a>

- **Document ID**: `DOC-CART-20260805-04`
- **Date**: 2026-08-05 (`2026-08-05T14:43:34+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-066`](https://jira.northstar.invalid/browse/CART-066) (`Done`)
- **Record Type**: Merchant Sync Decision

#### Context & Technical Objective
Reviewed Meridian Outfitters pilot integration requirements for [CART-066] (Immutable cart audit transition event logging — PostgreSQL indexing & tenant query guard) with Cart & Promotions engineering and merchant support.

#### Technical Decision & Invariants
Confirmed tenant-isolated configuration rules, CSV batch error reporting, and SFTP nightly sync schedule at 02:00+07:00.

#### Verification & Evidence
Action items logged with merchant onboarding specialists and verified against tenant boundary checks.

---

### [DOC-CART-20260806-05] Cart & Promotions: Architecture Decision Note #5 (2026-08-06)
<a id="doc-cart-20260806-05"></a>

- **Document ID**: `DOC-CART-20260806-05`
- **Date**: 2026-08-06 (`2026-08-06T16:50:49+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-063`](https://jira.northstar.invalid/browse/CART-063) (`Done`)
- **Record Type**: Architecture Decision Note

#### Context & Technical Objective
Architectural review for [CART-063] (Abandoned cart expiration workflow with automated stock release — Event outbox deduplication & ordering) within Cart & Promotions, focusing on service ownership boundaries, failure compensation, and multi-tenant isolation.

#### Technical Decision & Invariants
Enforced strict tenant_id scoping at the repository layer and durable 72-hour idempotency keys for mutating operations.

#### Verification & Evidence
Design aligns with DOC-ORG-SDS-001; contract tests and sequence diagrams validated by the tech lead.

---

### [DOC-CART-20260807-06] Cart & Promotions: Incident Post-Mortem Action #6 (2026-08-07)
<a id="doc-cart-20260807-06"></a>

- **Document ID**: `DOC-CART-20260807-06`
- **Date**: 2026-08-07 (`2026-08-07T09:01:04+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-056`](https://jira.northstar.invalid/browse/CART-056) (`To Do`)
- **Record Type**: Incident Post-Mortem Action

#### Context & Technical Objective
Follow-up remediation tracking for [CART-056] (Merchant cart item maximum quantity limit constraints — Rate limiting & audit trail emission) in Cart & Promotions after staging fault-injection and replay testing.

#### Technical Decision & Invariants
Added transactional outbox and unique inbox constraints so worker restarts or network retries cannot duplicate side effects.

#### Verification & Evidence
Crash-replay simulation added to continuous integration to prevent regression.

---

### [DOC-CART-20260807-07] Cart & Promotions: Merchant Sync Decision #7 (2026-08-07)
<a id="doc-cart-20260807-07"></a>

- **Document ID**: `DOC-CART-20260807-07`
- **Date**: 2026-08-07 (`2026-08-07T09:17:48+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-072`](https://jira.northstar.invalid/browse/CART-072) (`Done`)
- **Record Type**: Merchant Sync Decision

#### Context & Technical Objective
Reviewed Meridian Outfitters pilot integration requirements for [CART-072] (Bundle product component price breakdown in cart session — Boundary value & currency minor-unit validation) with Cart & Promotions engineering and merchant support.

#### Technical Decision & Invariants
Confirmed tenant-isolated configuration rules, CSV batch error reporting, and SFTP nightly sync schedule at 02:00+07:00.

#### Verification & Evidence
Action items logged with merchant onboarding specialists and verified against tenant boundary checks.

---

### [DOC-CART-20260810-08] Cart & Promotions: Architecture Decision Note #8 (2026-08-10)
<a id="doc-cart-20260810-08"></a>

- **Document ID**: `DOC-CART-20260810-08`
- **Date**: 2026-08-10 (`2026-08-10T11:24:03+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-065`](https://jira.northstar.invalid/browse/CART-065) (`Done`)
- **Record Type**: Architecture Decision Note

#### Context & Technical Objective
Architectural review for [CART-065] (Idempotent cart item updates during concurrent requests — Data retention & privacy masking compliance) within Cart & Promotions, focusing on service ownership boundaries, failure compensation, and multi-tenant isolation.

#### Technical Decision & Invariants
Enforced strict tenant_id scoping at the repository layer and durable 72-hour idempotency keys for mutating operations.

#### Verification & Evidence
Design aligns with DOC-ORG-SDS-001; contract tests and sequence diagrams validated by the tech lead.

---

### [DOC-CART-20260811-09] Cart & Promotions: Database Migration Checklist #9 (2026-08-11)
<a id="doc-cart-20260811-09"></a>

- **Document ID**: `DOC-CART-20260811-09`
- **Date**: 2026-08-11 (`2026-08-11T15:36:27+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
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

### [DOC-CART-20260811-10] Cart & Promotions: Daily Standup & Blocker Log #10 (2026-08-11)
<a id="doc-cart-20260811-10"></a>

- **Document ID**: `DOC-CART-20260811-10`
- **Date**: 2026-08-11 (`2026-08-11T18:37:59+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-079`](https://jira.northstar.invalid/browse/CART-079) (`Blocked`)
- **Record Type**: Daily Standup & Blocker Log

#### Context & Technical Objective
Daily engineering standup checkpoint for Cart & Promotions covering active work on [CART-079] (Fixed-amount and percentage tier coupon discounts — Merchant admin UI state & error boundary) (current ticket status: `Blocked`).

#### Technical Decision & Invariants
Reviewed upstream sandbox dependencies, PR review queue, and evening overtime (17:00–22:00+07:00) handoffs during sprint crunch.

#### Verification & Evidence
Updated Jira status transitions, blocker owners, and same-day escalation checkpoints.

---

### [DOC-CART-20260812-11] Cart & Promotions: API Contract Revision #11 (2026-08-12)
<a id="doc-cart-20260812-11"></a>

- **Document ID**: `DOC-CART-20260812-11`
- **Date**: 2026-08-12 (`2026-08-12T08:03:26+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-072`](https://jira.northstar.invalid/browse/CART-072) (`Done`)
- **Record Type**: API Contract Revision

#### Context & Technical Objective
Evaluated HTTP request/response payload schemas for [CART-072] (Bundle product component price breakdown in cart session — Boundary value & currency minor-unit validation) in Cart & Promotions to ensure backward compatibility and deterministic error codes.

#### Technical Decision & Invariants
Standardized monetary fields to integer minor currency units alongside ISO 4217 currency codes; added explicit HTTP 409 conflict and HTTP 422 field validation responses.

#### Verification & Evidence
API schema snapshot tested against staging-sim consumer stubs with zero breaking changes.

---

### [DOC-CART-20260813-12] Cart & Promotions: Database Migration Checklist #12 (2026-08-13)
<a id="doc-cart-20260813-12"></a>

- **Document ID**: `DOC-CART-20260813-12`
- **Date**: 2026-08-13 (`2026-08-13T10:10:41+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-068`](https://jira.northstar.invalid/browse/CART-068) (`Done`)
- **Record Type**: Database Migration Checklist

#### Context & Technical Objective
Database schema change verification for [CART-068] (Merchant cart item maximum quantity limit constraints — Backfill worker & batch memory tuning) managed by Cart & Promotions.

#### Technical Decision & Invariants
Applied expand/contract migration sequencing: nullable/default columns and concurrent indexes deployed ahead of application readers/writers.

#### Verification & Evidence
Forward/down recovery notes and row-count reconciliation verified against isolated backup snapshot.

---

### [DOC-CART-20260814-13] Cart & Promotions: Daily Standup & Blocker Log #13 (2026-08-14)
<a id="doc-cart-20260814-13"></a>

- **Document ID**: `DOC-CART-20260814-13`
- **Date**: 2026-08-14 (`2026-08-14T13:17:56+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-061`](https://jira.northstar.invalid/browse/CART-061) (`Done`)
- **Record Type**: Daily Standup & Blocker Log

#### Context & Technical Objective
Daily engineering standup checkpoint for Cart & Promotions covering active work on [CART-061] (Guest cart merging into customer account upon login — Load test benchmark & p95 latency profiling) (current ticket status: `Done`).

#### Technical Decision & Invariants
Reviewed upstream sandbox dependencies, PR review queue, and evening overtime (17:00–22:00+07:00) handoffs during sprint crunch.

#### Verification & Evidence
Updated Jira status transitions, blocker owners, and same-day escalation checkpoints.

---

### [DOC-CART-20260814-14] Cart & Promotions: API Contract Revision #14 (2026-08-14)
<a id="doc-cart-20260814-14"></a>

- **Document ID**: `DOC-CART-20260814-14`
- **Date**: 2026-08-14 (`2026-08-14T13:33:40+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-078`](https://jira.northstar.invalid/browse/CART-078) (`Done`)
- **Record Type**: API Contract Revision

#### Context & Technical Objective
Evaluated HTTP request/response payload schemas for [CART-078] (Immutable cart audit transition event logging — Redis distributed lock & concurrency handling) in Cart & Promotions to ensure backward compatibility and deterministic error codes.

#### Technical Decision & Invariants
Standardized monetary fields to integer minor currency units alongside ISO 4217 currency codes; added explicit HTTP 409 conflict and HTTP 422 field validation responses.

#### Verification & Evidence
API schema snapshot tested against staging-sim consumer stubs with zero breaking changes.

---

### [DOC-CART-20260817-15] Cart & Promotions: Database Migration Checklist #15 (2026-08-17)
<a id="doc-cart-20260817-15"></a>

- **Document ID**: `DOC-CART-20260817-15`
- **Date**: 2026-08-17 (`2026-08-17T15:40:55+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-071`](https://jira.northstar.invalid/browse/CART-071) (`Done`)
- **Record Type**: Database Migration Checklist

#### Context & Technical Objective
Database schema change verification for [CART-071] (Cart session TTL extension on user checkout interaction — Partner sandbox contract reconciliation) managed by Cart & Promotions.

#### Technical Decision & Invariants
Applied expand/contract migration sequencing: nullable/default columns and concurrent indexes deployed ahead of application readers/writers.

#### Verification & Evidence
Forward/down recovery notes and row-count reconciliation verified against isolated backup snapshot.

---

### [DOC-CART-20260818-16] Cart & Promotions: Daily Standup & Blocker Log #16 (2026-08-18)
<a id="doc-cart-20260818-16"></a>

- **Document ID**: `DOC-CART-20260818-16`
- **Date**: 2026-08-18 (`2026-08-18T08:47:10+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-070`](https://jira.northstar.invalid/browse/CART-070) (`In Review`)
- **Record Type**: Daily Standup & Blocker Log

#### Context & Technical Objective
Daily engineering standup checkpoint for Cart & Promotions covering active work on [CART-070] (Cart coupon eligibility against customer group rules — Cache invalidation & version lineage check) (current ticket status: `In Review`).

#### Technical Decision & Invariants
Reviewed upstream sandbox dependencies, PR review queue, and evening overtime (17:00–22:00+07:00) handoffs during sprint crunch.

#### Verification & Evidence
Updated Jira status transitions, blocker owners, and same-day escalation checkpoints.

---

### [DOC-CART-20260819-17] Cart & Promotions: API Contract Revision #17 (2026-08-19)
<a id="doc-cart-20260819-17"></a>

- **Document ID**: `DOC-CART-20260819-17`
- **Date**: 2026-08-19 (`2026-08-19T10:54:25+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-060`](https://jira.northstar.invalid/browse/CART-060) (`Done`)
- **Record Type**: API Contract Revision

#### Context & Technical Objective
Evaluated HTTP request/response payload schemas for [CART-060] (Bundle product component price breakdown in cart session — Automated recovery & rollback verification) in Cart & Promotions to ensure backward compatibility and deterministic error codes.

#### Technical Decision & Invariants
Standardized monetary fields to integer minor currency units alongside ISO 4217 currency codes; added explicit HTTP 409 conflict and HTTP 422 field validation responses.

#### Verification & Evidence
API schema snapshot tested against staging-sim consumer stubs with zero breaking changes.

---

### [DOC-CART-20260819-18] Cart & Promotions: Database Migration Checklist #18 (2026-08-19)
<a id="doc-cart-20260819-18"></a>

- **Document ID**: `DOC-CART-20260819-18`
- **Date**: 2026-08-19 (`2026-08-19T10:14:09+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-077`](https://jira.northstar.invalid/browse/CART-077) (`Done`)
- **Record Type**: Database Migration Checklist

#### Context & Technical Objective
Database schema change verification for [CART-077] (Idempotent cart item updates during concurrent requests — Cross-service correlation ID propagation) managed by Cart & Promotions.

#### Technical Decision & Invariants
Applied expand/contract migration sequencing: nullable/default columns and concurrent indexes deployed ahead of application readers/writers.

#### Verification & Evidence
Forward/down recovery notes and row-count reconciliation verified against isolated backup snapshot.

---

### [DOC-CART-20260820-19] Cart & Promotions: Security Review Note #19 (2026-08-20)
<a id="doc-cart-20260820-19"></a>

- **Document ID**: `DOC-CART-20260820-19`
- **Date**: 2026-08-20 (`2026-08-20T14:26:33+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-075`](https://jira.northstar.invalid/browse/CART-075) (`Done`)
- **Record Type**: Security Review Note

#### Context & Technical Objective
Application security and access-control assessment for [CART-075] (Abandoned cart expiration workflow with automated stock release — Quarantine workflow for malformed inputs) in Cart & Promotions.

#### Technical Decision & Invariants
Validated deny-by-default authorization, pre-retrieval ACL filtering, secret externalization, and zero persistence of PAN/CVV or raw credentials.

#### Verification & Evidence
AppSec sign-off recorded; negative cross-tenant and revoked-user probes passed in CI.

---

### [DOC-CART-20260821-20] Cart & Promotions: Regression Test Summary #20 (2026-08-21)
<a id="doc-cart-20260821-20"></a>

- **Document ID**: `DOC-CART-20260821-20`
- **Date**: 2026-08-21 (`2026-08-21T21:52:34+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-070`](https://jira.northstar.invalid/browse/CART-070) (`In Review`)
- **Record Type**: Regression Test Summary

#### Context & Technical Objective
Executed automated regression and negative boundary suite for [CART-070] (Cart coupon eligibility against customer group rules — Cache invalidation & version lineage check) across Cart & Promotions staging fixtures.

#### Technical Decision & Invariants
Verified idempotent replay, duplicate event suppression, and cross-tenant HTTP 403 rejection before snippet or count generation.

#### Verification & Evidence
All regression assertions recorded with deterministic seed=42 and correlation trace evidence attached.

---

### [DOC-CART-20260821-21] Cart & Promotions: Integration Review Notes #21 (2026-08-21)
<a id="doc-cart-20260821-21"></a>

- **Document ID**: `DOC-CART-20260821-21`
- **Date**: 2026-08-21 (`2026-08-21T17:44:18+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-084`](https://jira.northstar.invalid/browse/CART-084) (`In Progress`)
- **Record Type**: Integration Review Notes

#### Context & Technical Objective
Cross-service and partner integration sync for [CART-084] (Bundle product component price breakdown in cart session — Event outbox deduplication & ordering) in Cart & Promotions.

#### Technical Decision & Invariants
Verified HMAC-SHA256 webhook signature validation, bounded exponential backoff with jitter, and correlation ID propagation across service hops.

#### Verification & Evidence
Sandbox integration trace captured and linked to the requirement traceability matrix.

---

### [DOC-CART-20260824-22] Cart & Promotions: Security Review Note #22 (2026-08-24)
<a id="doc-cart-20260824-22"></a>

- **Document ID**: `DOC-CART-20260824-22`
- **Date**: 2026-08-24 (`2026-08-24T09:00:47+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-081`](https://jira.northstar.invalid/browse/CART-081) (`Done`)
- **Record Type**: Security Review Note

#### Context & Technical Objective
Application security and access-control assessment for [CART-081] (Cart currency conversion with cached FX exchange rates — Observability spans & SLO alert thresholds) in Cart & Promotions.

#### Technical Decision & Invariants
Validated deny-by-default authorization, pre-retrieval ACL filtering, secret externalization, and zero persistence of PAN/CVV or raw credentials.

#### Verification & Evidence
AppSec sign-off recorded; negative cross-tenant and revoked-user probes passed in CI.

---

### [DOC-CART-20260825-23] Cart & Promotions: Regression Test Summary #23 (2026-08-25)
<a id="doc-cart-20260825-23"></a>

- **Document ID**: `DOC-CART-20260825-23`
- **Date**: 2026-08-25 (`2026-08-25T11:07:02+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-074`](https://jira.northstar.invalid/browse/CART-074) (`Done`)
- **Record Type**: Regression Test Summary

#### Context & Technical Objective
Executed automated regression and negative boundary suite for [CART-074] (Promotion stacking hierarchy and discount evaluation engine — Automated recovery & rollback verification) across Cart & Promotions staging fixtures.

#### Technical Decision & Invariants
Verified idempotent replay, duplicate event suppression, and cross-tenant HTTP 403 rejection before snippet or count generation.

#### Verification & Evidence
All regression assertions recorded with deterministic seed=42 and correlation trace evidence attached.

---

### [DOC-CART-20260826-24] Cart & Promotions: Integration Review Notes #24 (2026-08-26)
<a id="doc-cart-20260826-24"></a>

- **Document ID**: `DOC-CART-20260826-24`
- **Date**: 2026-08-26 (`2026-08-26T14:14:17+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-067`](https://jira.northstar.invalid/browse/CART-067) (`In Progress`)
- **Record Type**: Integration Review Notes

#### Context & Technical Objective
Cross-service and partner integration sync for [CART-067] (Fixed-amount and percentage tier coupon discounts — Integration test suite & staging replay) in Cart & Promotions.

#### Technical Decision & Invariants
Verified HMAC-SHA256 webhook signature validation, bounded exponential backoff with jitter, and correlation ID propagation across service hops.

#### Verification & Evidence
Sandbox integration trace captured and linked to the requirement traceability matrix.

---

### [DOC-CART-20260826-25] Cart & Promotions: Security Review Note #25 (2026-08-26)
<a id="doc-cart-20260826-25"></a>

- **Document ID**: `DOC-CART-20260826-25`
- **Date**: 2026-08-26 (`2026-08-26T18:31:53+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-083`](https://jira.northstar.invalid/browse/CART-083) (`Done`)
- **Record Type**: Security Review Note

#### Context & Technical Objective
Application security and access-control assessment for [CART-083] (Cart session TTL extension on user checkout interaction — Role-based access control policy enforcement) in Cart & Promotions.

#### Technical Decision & Invariants
Validated deny-by-default authorization, pre-retrieval ACL filtering, secret externalization, and zero persistence of PAN/CVV or raw credentials.

#### Verification & Evidence
AppSec sign-off recorded; negative cross-tenant and revoked-user probes passed in CI.

---

### [DOC-CART-20260827-26] Cart & Promotions: Regression Test Summary #26 (2026-08-27)
<a id="doc-cart-20260827-26"></a>

- **Document ID**: `DOC-CART-20260827-26`
- **Date**: 2026-08-27 (`2026-08-27T16:37:16+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-080`](https://jira.northstar.invalid/browse/CART-080) (`Done`)
- **Record Type**: Regression Test Summary

#### Context & Technical Objective
Executed automated regression and negative boundary suite for [CART-080] (Merchant cart item maximum quantity limit constraints — Webhook signature & payload verification) across Cart & Promotions staging fixtures.

#### Technical Decision & Invariants
Verified idempotent replay, duplicate event suppression, and cross-tenant HTTP 403 rejection before snippet or count generation.

#### Verification & Evidence
All regression assertions recorded with deterministic seed=42 and correlation trace evidence attached.

---

### [DOC-CART-20260828-27] Cart & Promotions: Sprint Planning Update #27 (2026-08-28)
<a id="doc-cart-20260828-27"></a>

- **Document ID**: `DOC-CART-20260828-27`
- **Date**: 2026-08-28 (`2026-08-28T10:49:40+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-074`](https://jira.northstar.invalid/browse/CART-074) (`Done`)
- **Record Type**: Sprint Planning Update

#### Context & Technical Objective
During sprint backlog commitment on [CART-074] (Promotion stacking hierarchy and discount evaluation engine — Automated recovery & rollback verification), the Cart & Promotions squad decomposed acceptance criteria, story point capacity, and cross-service dependencies.

#### Technical Decision & Invariants
Confirmed sprint scope and velocity guardrails. Unfinished items from prior closed iterations are formally tracked via sprint spillover transitions into the active sprint.

#### Verification & Evidence
Backlog readiness verified with product owner and QA lead; test fixtures and correlation IDs linked in Jira.

---

### [DOC-CART-20260831-28] Cart & Promotions: Feature Rollout Milestone #28 (2026-08-31)
<a id="doc-cart-20260831-28"></a>

- **Document ID**: `DOC-CART-20260831-28`
- **Date**: 2026-08-31 (`2026-08-31T13:00:55+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-071`](https://jira.northstar.invalid/browse/CART-071) (`Done`)
- **Record Type**: Feature Rollout Milestone

#### Context & Technical Objective
Staged canary rollout readiness check for [CART-071] (Cart session TTL extension on user checkout interaction — Partner sandbox contract reconciliation) in Cart & Promotions.

#### Technical Decision & Invariants
Configured feature flag toggle and progressive traffic gates (0% synthetic -> 5% -> 25% -> 50% -> 100%) with automated rollback triggers.

#### Verification & Evidence
On-call SRE and workstream owner verified rollback runbook steps and alert routing.

---

### [DOC-CART-20260831-29] Cart & Promotions: Performance Benchmark Report #29 (2026-08-31)
<a id="doc-cart-20260831-29"></a>

- **Document ID**: `DOC-CART-20260831-29`
- **Date**: 2026-08-31 (`2026-08-31T20:25:39+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-087`](https://jira.northstar.invalid/browse/CART-087) (`In Progress`)
- **Record Type**: Performance Benchmark Report

#### Context & Technical Objective
Conducted load and latency profiling for [CART-087] (Abandoned cart expiration workflow with automated stock release — Storefront response serialization & pagination) in Cart & Promotions under the pilot reference workload.

#### Technical Decision & Invariants
Tuned PostgreSQL composite indexes and Redis lock TTLs to keep p95 latency within the approved service-level objective.

#### Verification & Evidence
Measured p95 response times, connection pool saturation, and queue lag metrics on the staging telemetry dashboard.

---
