---
bundle_id: "BUNDLE-NSC-CART-2026-06"
project_id: "NSC-CART"
project_name: "Cart & Promotions"
period: "2026-06"
classification: "Internal"
access_groups: ["GRP-CART"]
logical_document_count: 30
synthetic: true
---

# Cart & Promotions — Monthly Engineering Records (2026-06)

This Markdown bundle organizes 30 verified logical project records, decisions, meeting outcomes, and technical milestone updates for NSC-CART during 2026-06.

### [DOC-CART-20260601-01] Cart & Promotions: Merchant Sync Decision #1 (2026-06-01)
<a id="doc-cart-20260601-01"></a>

- **Document ID**: `DOC-CART-20260601-01`
- **Date**: 2026-06-01 (`2026-06-01T16:02:25+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-023`](https://jira.northstar.invalid/browse/CART-023) (`Done`)
- **Record Type**: Merchant Sync Decision

#### Context & Technical Objective
Reviewed Meridian Outfitters pilot integration requirements for [CART-023] (Cart session TTL extension on user checkout interaction — Database expand-contract migration script) with Cart & Promotions engineering and merchant support.

#### Technical Decision & Invariants
Confirmed tenant-isolated configuration rules, CSV batch error reporting, and SFTP nightly sync schedule at 02:00+07:00.

#### Verification & Evidence
Action items logged with merchant onboarding specialists and verified against tenant boundary checks.

---

### [DOC-CART-20260602-02] Cart & Promotions: Architecture Decision Note #2 (2026-06-02)
<a id="doc-cart-20260602-02"></a>

- **Document ID**: `DOC-CART-20260602-02`
- **Date**: 2026-06-02 (`2026-06-02T09:09:40+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-016`](https://jira.northstar.invalid/browse/CART-016) (`To Do`)
- **Record Type**: Architecture Decision Note

#### Context & Technical Objective
Architectural review for [CART-016] (Order line total recalculation after real-time inventory adjustments — Boundary value & currency minor-unit validation) within Cart & Promotions, focusing on service ownership boundaries, failure compensation, and multi-tenant isolation.

#### Technical Decision & Invariants
Enforced strict tenant_id scoping at the repository layer and durable 72-hour idempotency keys for mutating operations.

#### Verification & Evidence
Design aligns with DOC-ORG-SDS-001; contract tests and sequence diagrams validated by the tech lead.

---

### [DOC-CART-20260602-03] Cart & Promotions: Incident Post-Mortem Action #3 (2026-06-02)
<a id="doc-cart-20260602-03"></a>

- **Document ID**: `DOC-CART-20260602-03`
- **Date**: 2026-06-02 (`2026-06-02T09:25:24+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-032`](https://jira.northstar.invalid/browse/CART-032) (`Done`)
- **Record Type**: Incident Post-Mortem Action

#### Context & Technical Objective
Follow-up remediation tracking for [CART-032] (Merchant cart item maximum quantity limit constraints — Integration test suite & staging replay) in Cart & Promotions after staging fault-injection and replay testing.

#### Technical Decision & Invariants
Added transactional outbox and unique inbox constraints so worker restarts or network retries cannot duplicate side effects.

#### Verification & Evidence
Crash-replay simulation added to continuous integration to prevent regression.

---

### [DOC-CART-20260603-04] Cart & Promotions: Daily Standup & Blocker Log #4 (2026-06-03)
<a id="doc-cart-20260603-04"></a>

- **Document ID**: `DOC-CART-20260603-04`
- **Date**: 2026-06-03 (`2026-06-03T13:37:48+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-026`](https://jira.northstar.invalid/browse/CART-026) (`Done`)
- **Record Type**: Daily Standup & Blocker Log

#### Context & Technical Objective
Daily engineering standup checkpoint for Cart & Promotions covering active work on [CART-026] (Promotion stacking hierarchy and discount evaluation engine — Load test benchmark & p95 latency profiling) (current ticket status: `Done`).

#### Technical Decision & Invariants
Reviewed upstream sandbox dependencies, PR review queue, and evening overtime (17:00–22:00+07:00) handoffs during sprint crunch.

#### Verification & Evidence
Updated Jira status transitions, blocker owners, and same-day escalation checkpoints.

---

### [DOC-CART-20260604-05] Cart & Promotions: API Contract Revision #5 (2026-06-04)
<a id="doc-cart-20260604-05"></a>

- **Document ID**: `DOC-CART-20260604-05`
- **Date**: 2026-06-04 (`2026-06-04T15:44:03+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-023`](https://jira.northstar.invalid/browse/CART-023) (`Done`)
- **Record Type**: API Contract Revision

#### Context & Technical Objective
Evaluated HTTP request/response payload schemas for [CART-023] (Cart session TTL extension on user checkout interaction — Database expand-contract migration script) in Cart & Promotions to ensure backward compatibility and deterministic error codes.

#### Technical Decision & Invariants
Standardized monetary fields to integer minor currency units alongside ISO 4217 currency codes; added explicit HTTP 409 conflict and HTTP 422 field validation responses.

#### Verification & Evidence
API schema snapshot tested against staging-sim consumer stubs with zero breaking changes.

---

### [DOC-CART-20260604-06] Cart & Promotions: Database Migration Checklist #6 (2026-06-04)
<a id="doc-cart-20260604-06"></a>

- **Document ID**: `DOC-CART-20260604-06`
- **Date**: 2026-06-04 (`2026-06-04T17:37:43+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-037`](https://jira.northstar.invalid/browse/CART-037) (`Done`)
- **Record Type**: Database Migration Checklist

#### Context & Technical Objective
Database schema change verification for [CART-037] (Guest cart merging into customer account upon login — Database expand-contract migration script) managed by Cart & Promotions.

#### Technical Decision & Invariants
Applied expand/contract migration sequencing: nullable/default columns and concurrent indexes deployed ahead of application readers/writers.

#### Verification & Evidence
Forward/down recovery notes and row-count reconciliation verified against isolated backup snapshot.

---

### [DOC-CART-20260605-07] Cart & Promotions: Daily Standup & Blocker Log #7 (2026-06-05)
<a id="doc-cart-20260605-07"></a>

- **Document ID**: `DOC-CART-20260605-07`
- **Date**: 2026-06-05 (`2026-06-05T08:11:02+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-032`](https://jira.northstar.invalid/browse/CART-032) (`Done`)
- **Record Type**: Daily Standup & Blocker Log

#### Context & Technical Objective
Daily engineering standup checkpoint for Cart & Promotions covering active work on [CART-032] (Merchant cart item maximum quantity limit constraints — Integration test suite & staging replay) (current ticket status: `Done`).

#### Technical Decision & Invariants
Reviewed upstream sandbox dependencies, PR review queue, and evening overtime (17:00–22:00+07:00) handoffs during sprint crunch.

#### Verification & Evidence
Updated Jira status transitions, blocker owners, and same-day escalation checkpoints.

---

### [DOC-CART-20260608-08] Cart & Promotions: API Contract Revision #8 (2026-06-08)
<a id="doc-cart-20260608-08"></a>

- **Document ID**: `DOC-CART-20260608-08`
- **Date**: 2026-06-08 (`2026-06-08T10:18:17+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-030`](https://jira.northstar.invalid/browse/CART-030) (`In Review`)
- **Record Type**: API Contract Revision

#### Context & Technical Objective
Evaluated HTTP request/response payload schemas for [CART-030] (Immutable cart audit transition event logging — Data retention & privacy masking compliance) in Cart & Promotions to ensure backward compatibility and deterministic error codes.

#### Technical Decision & Invariants
Standardized monetary fields to integer minor currency units alongside ISO 4217 currency codes; added explicit HTTP 409 conflict and HTTP 422 field validation responses.

#### Verification & Evidence
API schema snapshot tested against staging-sim consumer stubs with zero breaking changes.

---

### [DOC-CART-20260609-09] Cart & Promotions: Database Migration Checklist #9 (2026-06-09)
<a id="doc-cart-20260609-09"></a>

- **Document ID**: `DOC-CART-20260609-09`
- **Date**: 2026-06-09 (`2026-06-09T13:25:32+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-022`](https://jira.northstar.invalid/browse/CART-022) (`Done`)
- **Record Type**: Database Migration Checklist

#### Context & Technical Objective
Database schema change verification for [CART-022] (Cart coupon eligibility against customer group rules — Timeout fallback & circuit breaker logic) managed by Cart & Promotions.

#### Technical Decision & Invariants
Applied expand/contract migration sequencing: nullable/default columns and concurrent indexes deployed ahead of application readers/writers.

#### Verification & Evidence
Forward/down recovery notes and row-count reconciliation verified against isolated backup snapshot.

---

### [DOC-CART-20260609-10] Cart & Promotions: Daily Standup & Blocker Log #10 (2026-06-09)
<a id="doc-cart-20260609-10"></a>

- **Document ID**: `DOC-CART-20260609-10`
- **Date**: 2026-06-09 (`2026-06-09T13:41:16+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-039`](https://jira.northstar.invalid/browse/CART-039) (`Blocked`)
- **Record Type**: Daily Standup & Blocker Log

#### Context & Technical Objective
Daily engineering standup checkpoint for Cart & Promotions covering active work on [CART-039] (Abandoned cart expiration workflow with automated stock release — Automated recovery & rollback verification) (current ticket status: `Blocked`).

#### Technical Decision & Invariants
Reviewed upstream sandbox dependencies, PR review queue, and evening overtime (17:00–22:00+07:00) handoffs during sprint crunch.

#### Verification & Evidence
Updated Jira status transitions, blocker owners, and same-day escalation checkpoints.

---

### [DOC-CART-20260610-11] Cart & Promotions: API Contract Revision #11 (2026-06-10)
<a id="doc-cart-20260610-11"></a>

- **Document ID**: `DOC-CART-20260610-11`
- **Date**: 2026-06-10 (`2026-06-10T15:48:31+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-029`](https://jira.northstar.invalid/browse/CART-029) (`Done`)
- **Record Type**: API Contract Revision

#### Context & Technical Objective
Evaluated HTTP request/response payload schemas for [CART-029] (Idempotent cart item updates during concurrent requests — Zero-downtime deployment readiness gate) in Cart & Promotions to ensure backward compatibility and deterministic error codes.

#### Technical Decision & Invariants
Standardized monetary fields to integer minor currency units alongside ISO 4217 currency codes; added explicit HTTP 409 conflict and HTTP 422 field validation responses.

#### Verification & Evidence
API schema snapshot tested against staging-sim consumer stubs with zero breaking changes.

---

### [DOC-CART-20260611-12] Cart & Promotions: Integration Review Notes #12 (2026-06-11)
<a id="doc-cart-20260611-12"></a>

- **Document ID**: `DOC-CART-20260611-12`
- **Date**: 2026-06-11 (`2026-06-11T09:04:55+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-030`](https://jira.northstar.invalid/browse/CART-030) (`In Review`)
- **Record Type**: Integration Review Notes

#### Context & Technical Objective
Cross-service and partner integration sync for [CART-030] (Immutable cart audit transition event logging — Data retention & privacy masking compliance) in Cart & Promotions.

#### Technical Decision & Invariants
Verified HMAC-SHA256 webhook signature validation, bounded exponential backoff with jitter, and correlation ID propagation across service hops.

#### Verification & Evidence
Sandbox integration trace captured and linked to the requirement traceability matrix.

---

### [DOC-CART-20260612-13] Cart & Promotions: Security Review Note #13 (2026-06-12)
<a id="doc-cart-20260612-13"></a>

- **Document ID**: `DOC-CART-20260612-13`
- **Date**: 2026-06-12 (`2026-06-12T19:26:20+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-022`](https://jira.northstar.invalid/browse/CART-022) (`Done`)
- **Record Type**: Security Review Note

#### Context & Technical Objective
Application security and access-control assessment for [CART-022] (Cart coupon eligibility against customer group rules — Timeout fallback & circuit breaker logic) in Cart & Promotions.

#### Technical Decision & Invariants
Validated deny-by-default authorization, pre-retrieval ACL filtering, secret externalization, and zero persistence of PAN/CVV or raw credentials.

#### Verification & Evidence
AppSec sign-off recorded; negative cross-tenant and revoked-user probes passed in CI.

---

### [DOC-CART-20260612-14] Cart & Promotions: Regression Test Summary #14 (2026-06-12)
<a id="doc-cart-20260612-14"></a>

- **Document ID**: `DOC-CART-20260612-14`
- **Date**: 2026-06-12 (`2026-06-12T11:27:54+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-039`](https://jira.northstar.invalid/browse/CART-039) (`Blocked`)
- **Record Type**: Regression Test Summary

#### Context & Technical Objective
Executed automated regression and negative boundary suite for [CART-039] (Abandoned cart expiration workflow with automated stock release — Automated recovery & rollback verification) across Cart & Promotions staging fixtures.

#### Technical Decision & Invariants
Verified idempotent replay, duplicate event suppression, and cross-tenant HTTP 403 rejection before snippet or count generation.

#### Verification & Evidence
All regression assertions recorded with deterministic seed=42 and correlation trace evidence attached.

---

### [DOC-CART-20260615-15] Cart & Promotions: Integration Review Notes #15 (2026-06-15)
<a id="doc-cart-20260615-15"></a>

- **Document ID**: `DOC-CART-20260615-15`
- **Date**: 2026-06-15 (`2026-06-15T14:34:09+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-035`](https://jira.northstar.invalid/browse/CART-035) (`Done`)
- **Record Type**: Integration Review Notes

#### Context & Technical Objective
Cross-service and partner integration sync for [CART-035] (Cart session TTL extension on user checkout interaction — Cache invalidation & version lineage check) in Cart & Promotions.

#### Technical Decision & Invariants
Verified HMAC-SHA256 webhook signature validation, bounded exponential backoff with jitter, and correlation ID propagation across service hops.

#### Verification & Evidence
Sandbox integration trace captured and linked to the requirement traceability matrix.

---

### [DOC-CART-20260616-16] Cart & Promotions: Security Review Note #16 (2026-06-16)
<a id="doc-cart-20260616-16"></a>

- **Document ID**: `DOC-CART-20260616-16`
- **Date**: 2026-06-16 (`2026-06-16T16:41:24+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-028`](https://jira.northstar.invalid/browse/CART-028) (`Done`)
- **Record Type**: Security Review Note

#### Context & Technical Objective
Application security and access-control assessment for [CART-028] (Order line total recalculation after real-time inventory adjustments — Event outbox deduplication & ordering) in Cart & Promotions.

#### Technical Decision & Invariants
Validated deny-by-default authorization, pre-retrieval ACL filtering, secret externalization, and zero persistence of PAN/CVV or raw credentials.

#### Verification & Evidence
AppSec sign-off recorded; negative cross-tenant and revoked-user probes passed in CI.

---

### [DOC-CART-20260616-17] Cart & Promotions: Regression Test Summary #17 (2026-06-16)
<a id="doc-cart-20260616-17"></a>

- **Document ID**: `DOC-CART-20260616-17`
- **Date**: 2026-06-16 (`2026-06-16T21:44:02+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-044`](https://jira.northstar.invalid/browse/CART-044) (`In Progress`)
- **Record Type**: Regression Test Summary

#### Context & Technical Objective
Executed automated regression and negative boundary suite for [CART-044] (Merchant cart item maximum quantity limit constraints — Merchant admin UI state & error boundary) across Cart & Promotions staging fixtures.

#### Technical Decision & Invariants
Verified idempotent replay, duplicate event suppression, and cross-tenant HTTP 403 rejection before snippet or count generation.

#### Verification & Evidence
All regression assertions recorded with deterministic seed=42 and correlation trace evidence attached.

---

### [DOC-CART-20260617-18] Cart & Promotions: Integration Review Notes #18 (2026-06-17)
<a id="doc-cart-20260617-18"></a>

- **Document ID**: `DOC-CART-20260617-18`
- **Date**: 2026-06-17 (`2026-06-17T21:05:39+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-041`](https://jira.northstar.invalid/browse/CART-041) (`In Progress`)
- **Record Type**: Integration Review Notes

#### Context & Technical Objective
Cross-service and partner integration sync for [CART-041] (Idempotent cart item updates during concurrent requests — Security header & token scope hardening) in Cart & Promotions.

#### Technical Decision & Invariants
Verified HMAC-SHA256 webhook signature validation, bounded exponential backoff with jitter, and correlation ID propagation across service hops.

#### Verification & Evidence
Sandbox integration trace captured and linked to the requirement traceability matrix.

---

### [DOC-CART-20260618-19] Cart & Promotions: Security Review Note #19 (2026-06-18)
<a id="doc-cart-20260618-19"></a>

- **Document ID**: `DOC-CART-20260618-19`
- **Date**: 2026-06-18 (`2026-06-18T11:15:38+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-034`](https://jira.northstar.invalid/browse/CART-034) (`Done`)
- **Record Type**: Security Review Note

#### Context & Technical Objective
Application security and access-control assessment for [CART-034] (Cart coupon eligibility against customer group rules — Multi-tenant isolation & negative permission checks) in Cart & Promotions.

#### Technical Decision & Invariants
Validated deny-by-default authorization, pre-retrieval ACL filtering, secret externalization, and zero persistence of PAN/CVV or raw credentials.

#### Verification & Evidence
AppSec sign-off recorded; negative cross-tenant and revoked-user probes passed in CI.

---

### [DOC-CART-20260619-20] Cart & Promotions: Regression Test Summary #20 (2026-06-19)
<a id="doc-cart-20260619-20"></a>

- **Document ID**: `DOC-CART-20260619-20`
- **Date**: 2026-06-19 (`2026-06-19T14:22:53+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-027`](https://jira.northstar.invalid/browse/CART-027) (`In Progress`)
- **Record Type**: Regression Test Summary

#### Context & Technical Objective
Executed automated regression and negative boundary suite for [CART-027] (Abandoned cart expiration workflow with automated stock release — Role-based access control policy enforcement) across Cart & Promotions staging fixtures.

#### Technical Decision & Invariants
Verified idempotent replay, duplicate event suppression, and cross-tenant HTTP 403 rejection before snippet or count generation.

#### Verification & Evidence
All regression assertions recorded with deterministic seed=42 and correlation trace evidence attached.

---

### [DOC-CART-20260619-21] Cart & Promotions: Integration Review Notes #21 (2026-06-19)
<a id="doc-cart-20260619-21"></a>

- **Document ID**: `DOC-CART-20260619-21`
- **Date**: 2026-06-19 (`2026-06-19T14:38:37+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
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

### [DOC-CART-20260622-22] Cart & Promotions: Feature Rollout Milestone #22 (2026-06-22)
<a id="doc-cart-20260622-22"></a>

- **Document ID**: `DOC-CART-20260622-22`
- **Date**: 2026-06-22 (`2026-06-22T18:55:25+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-041`](https://jira.northstar.invalid/browse/CART-041) (`In Progress`)
- **Record Type**: Feature Rollout Milestone

#### Context & Technical Objective
Staged canary rollout readiness check for [CART-041] (Idempotent cart item updates during concurrent requests — Security header & token scope hardening) in Cart & Promotions.

#### Technical Decision & Invariants
Configured feature flag toggle and progressive traffic gates (0% synthetic -> 5% -> 25% -> 50% -> 100%) with automated rollback triggers.

#### Verification & Evidence
On-call SRE and workstream owner verified rollback runbook steps and alert routing.

---

### [DOC-CART-20260623-23] Cart & Promotions: Performance Benchmark Report #23 (2026-06-23)
<a id="doc-cart-20260623-23"></a>

- **Document ID**: `DOC-CART-20260623-23`
- **Date**: 2026-06-23 (`2026-06-23T10:01:16+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-034`](https://jira.northstar.invalid/browse/CART-034) (`Done`)
- **Record Type**: Performance Benchmark Report

#### Context & Technical Objective
Conducted load and latency profiling for [CART-034] (Cart coupon eligibility against customer group rules — Multi-tenant isolation & negative permission checks) in Cart & Promotions under the pilot reference workload.

#### Technical Decision & Invariants
Tuned PostgreSQL composite indexes and Redis lock TTLs to keep p95 latency within the approved service-level objective.

#### Verification & Evidence
Measured p95 response times, connection pool saturation, and queue lag metrics on the staging telemetry dashboard.

---

### [DOC-CART-20260624-24] Cart & Promotions: Sprint Planning Update #24 (2026-06-24)
<a id="doc-cart-20260624-24"></a>

- **Document ID**: `DOC-CART-20260624-24`
- **Date**: 2026-06-24 (`2026-06-24T13:08:31+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-029`](https://jira.northstar.invalid/browse/CART-029) (`Done`)
- **Record Type**: Sprint Planning Update

#### Context & Technical Objective
During sprint backlog commitment on [CART-029] (Idempotent cart item updates during concurrent requests — Zero-downtime deployment readiness gate), the Cart & Promotions squad decomposed acceptance criteria, story point capacity, and cross-service dependencies.

#### Technical Decision & Invariants
Confirmed sprint scope and velocity guardrails. Unfinished items from prior closed iterations are formally tracked via sprint spillover transitions into the active sprint.

#### Verification & Evidence
Backlog readiness verified with product owner and QA lead; test fixtures and correlation IDs linked in Jira.

---

### [DOC-CART-20260624-25] Cart & Promotions: Feature Rollout Milestone #25 (2026-06-24)
<a id="doc-cart-20260624-25"></a>

- **Document ID**: `DOC-CART-20260624-25`
- **Date**: 2026-06-24 (`2026-06-24T13:24:15+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-047`](https://jira.northstar.invalid/browse/CART-047) (`In Progress`)
- **Record Type**: Feature Rollout Milestone

#### Context & Technical Objective
Staged canary rollout readiness check for [CART-047] (Cart session TTL extension on user checkout interaction — Load test benchmark & p95 latency profiling) in Cart & Promotions.

#### Technical Decision & Invariants
Configured feature flag toggle and progressive traffic gates (0% synthetic -> 5% -> 25% -> 50% -> 100%) with automated rollback triggers.

#### Verification & Evidence
On-call SRE and workstream owner verified rollback runbook steps and alert routing.

---

### [DOC-CART-20260625-26] Cart & Promotions: Performance Benchmark Report #26 (2026-06-25)
<a id="doc-cart-20260625-26"></a>

- **Document ID**: `DOC-CART-20260625-26`
- **Date**: 2026-06-25 (`2026-06-25T15:31:30+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-040`](https://jira.northstar.invalid/browse/CART-040) (`Done`)
- **Record Type**: Performance Benchmark Report

#### Context & Technical Objective
Conducted load and latency profiling for [CART-040] (Order line total recalculation after real-time inventory adjustments — Quarantine workflow for malformed inputs) in Cart & Promotions under the pilot reference workload.

#### Technical Decision & Invariants
Tuned PostgreSQL composite indexes and Redis lock TTLs to keep p95 latency within the approved service-level objective.

#### Verification & Evidence
Measured p95 response times, connection pool saturation, and queue lag metrics on the staging telemetry dashboard.

---

### [DOC-CART-20260626-27] Cart & Promotions: Sprint Planning Update #27 (2026-06-26)
<a id="doc-cart-20260626-27"></a>

- **Document ID**: `DOC-CART-20260626-27`
- **Date**: 2026-06-26 (`2026-06-26T19:03:37+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-033`](https://jira.northstar.invalid/browse/CART-033) (`In Review`)
- **Record Type**: Sprint Planning Update

#### Context & Technical Objective
During sprint backlog commitment on [CART-033] (Cart currency conversion with cached FX exchange rates — Backfill worker & batch memory tuning), the Cart & Promotions squad decomposed acceptance criteria, story point capacity, and cross-service dependencies.

#### Technical Decision & Invariants
Confirmed sprint scope and velocity guardrails. Unfinished items from prior closed iterations are formally tracked via sprint spillover transitions into the active sprint.

#### Verification & Evidence
Backlog readiness verified with product owner and QA lead; test fixtures and correlation IDs linked in Jira.

---

### [DOC-CART-20260626-28] Cart & Promotions: Feature Rollout Milestone #28 (2026-06-26)
<a id="doc-cart-20260626-28"></a>

- **Document ID**: `DOC-CART-20260626-28`
- **Date**: 2026-06-26 (`2026-06-26T20:51:21+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-049`](https://jira.northstar.invalid/browse/CART-049) (`Done`)
- **Record Type**: Feature Rollout Milestone

#### Context & Technical Objective
Staged canary rollout readiness check for [CART-049] (Guest cart merging into customer account upon login — Cache invalidation & version lineage check) in Cart & Promotions.

#### Technical Decision & Invariants
Configured feature flag toggle and progressive traffic gates (0% synthetic -> 5% -> 25% -> 50% -> 100%) with automated rollback triggers.

#### Verification & Evidence
On-call SRE and workstream owner verified rollback runbook steps and alert routing.

---

### [DOC-CART-20260629-29] Cart & Promotions: Performance Benchmark Report #29 (2026-06-29)
<a id="doc-cart-20260629-29"></a>

- **Document ID**: `DOC-CART-20260629-29`
- **Date**: 2026-06-29 (`2026-06-29T10:05:44+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-045`](https://jira.northstar.invalid/browse/CART-045) (`Done`)
- **Record Type**: Performance Benchmark Report

#### Context & Technical Objective
Conducted load and latency profiling for [CART-045] (Cart currency conversion with cached FX exchange rates — Webhook signature & payload verification) in Cart & Promotions under the pilot reference workload.

#### Technical Decision & Invariants
Tuned PostgreSQL composite indexes and Redis lock TTLs to keep p95 latency within the approved service-level objective.

#### Verification & Evidence
Measured p95 response times, connection pool saturation, and queue lag metrics on the staging telemetry dashboard.

---

### [DOC-CART-20260630-30] Cart & Promotions: Architecture Decision Note #30 (2026-06-30)
<a id="doc-cart-20260630-30"></a>

- **Document ID**: `DOC-CART-20260630-30`
- **Date**: 2026-06-30 (`2026-06-30T14:17:08+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-040`](https://jira.northstar.invalid/browse/CART-040) (`Done`)
- **Record Type**: Architecture Decision Note

#### Context & Technical Objective
Architectural review for [CART-040] (Order line total recalculation after real-time inventory adjustments — Quarantine workflow for malformed inputs) within Cart & Promotions, focusing on service ownership boundaries, failure compensation, and multi-tenant isolation.

#### Technical Decision & Invariants
Enforced strict tenant_id scoping at the repository layer and durable 72-hour idempotency keys for mutating operations.

#### Verification & Evidence
Design aligns with DOC-ORG-SDS-001; contract tests and sequence diagrams validated by the tech lead.

---
