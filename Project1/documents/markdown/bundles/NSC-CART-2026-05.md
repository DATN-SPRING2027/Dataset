---
bundle_id: "BUNDLE-NSC-CART-2026-05"
project_id: "NSC-CART"
project_name: "Cart & Promotions"
period: "2026-05"
classification: "Internal"
access_groups: ["GRP-CART"]
logical_document_count: 27
synthetic: true
---

# Cart & Promotions — Monthly Engineering Records (2026-05)

This Markdown bundle organizes 27 verified logical project records, decisions, meeting outcomes, and technical milestone updates for NSC-CART during 2026-05.

### [DOC-CART-20260504-01] Cart & Promotions: API Contract Revision #1 (2026-05-04)
<a id="doc-cart-20260504-01"></a>

- **Document ID**: `DOC-CART-20260504-01`
- **Date**: 2026-05-04 (`2026-05-04T13:15:50+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-012`](https://jira.northstar.invalid/browse/CART-012) (`Done`)
- **Record Type**: API Contract Revision

#### Context & Technical Objective
Evaluated HTTP request/response payload schemas for [CART-012] (Bundle product component price breakdown in cart session) in Cart & Promotions to ensure backward compatibility and deterministic error codes.

#### Technical Decision & Invariants
Standardized monetary fields to integer minor currency units alongside ISO 4217 currency codes; added explicit HTTP 409 conflict and HTTP 422 field validation responses.

#### Verification & Evidence
API schema snapshot tested against staging-sim consumer stubs with zero breaking changes.

---

### [DOC-CART-20260505-02] Cart & Promotions: Database Migration Checklist #2 (2026-05-05)
<a id="doc-cart-20260505-02"></a>

- **Document ID**: `DOC-CART-20260505-02`
- **Date**: 2026-05-05 (`2026-05-05T15:22:05+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-009`](https://jira.northstar.invalid/browse/CART-009) (`Done`)
- **Record Type**: Database Migration Checklist

#### Context & Technical Objective
Database schema change verification for [CART-009] (Cart currency conversion with cached FX exchange rates) managed by Cart & Promotions.

#### Technical Decision & Invariants
Applied expand/contract migration sequencing: nullable/default columns and concurrent indexes deployed ahead of application readers/writers.

#### Verification & Evidence
Forward/down recovery notes and row-count reconciliation verified against isolated backup snapshot.

---

### [DOC-CART-20260506-03] Cart & Promotions: Daily Standup & Blocker Log #3 (2026-05-06)
<a id="doc-cart-20260506-03"></a>

- **Document ID**: `DOC-CART-20260506-03`
- **Date**: 2026-05-06 (`2026-05-06T08:29:20+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-002`](https://jira.northstar.invalid/browse/CART-002) (`Done`)
- **Record Type**: Daily Standup & Blocker Log

#### Context & Technical Objective
Daily engineering standup checkpoint for Cart & Promotions covering active work on [CART-002] (Promotion stacking hierarchy and discount evaluation engine) (current ticket status: `Done`).

#### Technical Decision & Invariants
Reviewed upstream sandbox dependencies, PR review queue, and evening overtime (17:00–22:00+07:00) handoffs during sprint crunch.

#### Verification & Evidence
Updated Jira status transitions, blocker owners, and same-day escalation checkpoints.

---

### [DOC-CART-20260506-04] Cart & Promotions: API Contract Revision #4 (2026-05-06)
<a id="doc-cart-20260506-04"></a>

- **Document ID**: `DOC-CART-20260506-04`
- **Date**: 2026-05-06 (`2026-05-06T08:45:04+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-018`](https://jira.northstar.invalid/browse/CART-018) (`Done`)
- **Record Type**: API Contract Revision

#### Context & Technical Objective
Evaluated HTTP request/response payload schemas for [CART-018] (Immutable cart audit transition event logging — Operational runbook & support diagnostics) in Cart & Promotions to ensure backward compatibility and deterministic error codes.

#### Technical Decision & Invariants
Standardized monetary fields to integer minor currency units alongside ISO 4217 currency codes; added explicit HTTP 409 conflict and HTTP 422 field validation responses.

#### Verification & Evidence
API schema snapshot tested against staging-sim consumer stubs with zero breaking changes.

---

### [DOC-CART-20260507-05] Cart & Promotions: Database Migration Checklist #5 (2026-05-07)
<a id="doc-cart-20260507-05"></a>

- **Document ID**: `DOC-CART-20260507-05`
- **Date**: 2026-05-07 (`2026-05-07T10:52:19+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-011`](https://jira.northstar.invalid/browse/CART-011) (`Done`)
- **Record Type**: Database Migration Checklist

#### Context & Technical Objective
Database schema change verification for [CART-011] (Cart session TTL extension on user checkout interaction) managed by Cart & Promotions.

#### Technical Decision & Invariants
Applied expand/contract migration sequencing: nullable/default columns and concurrent indexes deployed ahead of application readers/writers.

#### Verification & Evidence
Forward/down recovery notes and row-count reconciliation verified against isolated backup snapshot.

---

### [DOC-CART-20260508-06] Cart & Promotions: Security Review Note #6 (2026-05-08)
<a id="doc-cart-20260508-06"></a>

- **Document ID**: `DOC-CART-20260508-06`
- **Date**: 2026-05-08 (`2026-05-08T14:08:43+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-009`](https://jira.northstar.invalid/browse/CART-009) (`Done`)
- **Record Type**: Security Review Note

#### Context & Technical Objective
Application security and access-control assessment for [CART-009] (Cart currency conversion with cached FX exchange rates) in Cart & Promotions.

#### Technical Decision & Invariants
Validated deny-by-default authorization, pre-retrieval ACL filtering, secret externalization, and zero persistence of PAN/CVV or raw credentials.

#### Verification & Evidence
AppSec sign-off recorded; negative cross-tenant and revoked-user probes passed in CI.

---

### [DOC-CART-20260511-07] Cart & Promotions: Regression Test Summary #7 (2026-05-11)
<a id="doc-cart-20260511-07"></a>

- **Document ID**: `DOC-CART-20260511-07`
- **Date**: 2026-05-11 (`2026-05-11T16:15:58+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-002`](https://jira.northstar.invalid/browse/CART-002) (`Done`)
- **Record Type**: Regression Test Summary

#### Context & Technical Objective
Executed automated regression and negative boundary suite for [CART-002] (Promotion stacking hierarchy and discount evaluation engine) across Cart & Promotions staging fixtures.

#### Technical Decision & Invariants
Verified idempotent replay, duplicate event suppression, and cross-tenant HTTP 403 rejection before snippet or count generation.

#### Verification & Evidence
All regression assertions recorded with deterministic seed=42 and correlation trace evidence attached.

---

### [DOC-CART-20260511-08] Cart & Promotions: Integration Review Notes #8 (2026-05-11)
<a id="doc-cart-20260511-08"></a>

- **Document ID**: `DOC-CART-20260511-08`
- **Date**: 2026-05-11 (`2026-05-11T17:46:56+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-018`](https://jira.northstar.invalid/browse/CART-018) (`Done`)
- **Record Type**: Integration Review Notes

#### Context & Technical Objective
Cross-service and partner integration sync for [CART-018] (Immutable cart audit transition event logging — Operational runbook & support diagnostics) in Cart & Promotions.

#### Technical Decision & Invariants
Verified HMAC-SHA256 webhook signature validation, bounded exponential backoff with jitter, and correlation ID propagation across service hops.

#### Verification & Evidence
Sandbox integration trace captured and linked to the requirement traceability matrix.

---

### [DOC-CART-20260512-09] Cart & Promotions: Security Review Note #9 (2026-05-12)
<a id="doc-cart-20260512-09"></a>

- **Document ID**: `DOC-CART-20260512-09`
- **Date**: 2026-05-12 (`2026-05-12T09:38:57+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-013`](https://jira.northstar.invalid/browse/CART-013) (`In Review`)
- **Record Type**: Security Review Note

#### Context & Technical Objective
Application security and access-control assessment for [CART-013] (Guest cart merging into customer account upon login — Multi-tenant isolation & negative permission checks) in Cart & Promotions.

#### Technical Decision & Invariants
Validated deny-by-default authorization, pre-retrieval ACL filtering, secret externalization, and zero persistence of PAN/CVV or raw credentials.

#### Verification & Evidence
AppSec sign-off recorded; negative cross-tenant and revoked-user probes passed in CI.

---

### [DOC-CART-20260513-10] Cart & Promotions: Regression Test Summary #10 (2026-05-13)
<a id="doc-cart-20260513-10"></a>

- **Document ID**: `DOC-CART-20260513-10`
- **Date**: 2026-05-13 (`2026-05-13T11:45:12+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-008`](https://jira.northstar.invalid/browse/CART-008) (`Done`)
- **Record Type**: Regression Test Summary

#### Context & Technical Objective
Executed automated regression and negative boundary suite for [CART-008] (Merchant cart item maximum quantity limit constraints) across Cart & Promotions staging fixtures.

#### Technical Decision & Invariants
Verified idempotent replay, duplicate event suppression, and cross-tenant HTTP 403 rejection before snippet or count generation.

#### Verification & Evidence
All regression assertions recorded with deterministic seed=42 and correlation trace evidence attached.

---

### [DOC-CART-20260513-11] Cart & Promotions: Integration Review Notes #11 (2026-05-13)
<a id="doc-cart-20260513-11"></a>

- **Document ID**: `DOC-CART-20260513-11`
- **Date**: 2026-05-13 (`2026-05-13T18:16:54+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-024`](https://jira.northstar.invalid/browse/CART-024) (`In Progress`)
- **Record Type**: Integration Review Notes

#### Context & Technical Objective
Cross-service and partner integration sync for [CART-024] (Bundle product component price breakdown in cart session — Edge-case race condition remediation) in Cart & Promotions.

#### Technical Decision & Invariants
Verified HMAC-SHA256 webhook signature validation, bounded exponential backoff with jitter, and correlation ID propagation across service hops.

#### Verification & Evidence
Sandbox integration trace captured and linked to the requirement traceability matrix.

---

### [DOC-CART-20260514-12] Cart & Promotions: Security Review Note #12 (2026-05-14)
<a id="doc-cart-20260514-12"></a>

- **Document ID**: `DOC-CART-20260514-12`
- **Date**: 2026-05-14 (`2026-05-14T14:12:11+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-021`](https://jira.northstar.invalid/browse/CART-021) (`Done`)
- **Record Type**: Security Review Note

#### Context & Technical Objective
Application security and access-control assessment for [CART-021] (Cart currency conversion with cached FX exchange rates — Rate limiting & audit trail emission) in Cart & Promotions.

#### Technical Decision & Invariants
Validated deny-by-default authorization, pre-retrieval ACL filtering, secret externalization, and zero persistence of PAN/CVV or raw credentials.

#### Verification & Evidence
AppSec sign-off recorded; negative cross-tenant and revoked-user probes passed in CI.

---

### [DOC-CART-20260515-13] Cart & Promotions: Regression Test Summary #13 (2026-05-15)
<a id="doc-cart-20260515-13"></a>

- **Document ID**: `DOC-CART-20260515-13`
- **Date**: 2026-05-15 (`2026-05-15T18:50:08+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-015`](https://jira.northstar.invalid/browse/CART-015) (`Done`)
- **Record Type**: Regression Test Summary

#### Context & Technical Objective
Executed automated regression and negative boundary suite for [CART-015] (Abandoned cart expiration workflow with automated stock release — Partner sandbox contract reconciliation) across Cart & Promotions staging fixtures.

#### Technical Decision & Invariants
Verified idempotent replay, duplicate event suppression, and cross-tenant HTTP 403 rejection before snippet or count generation.

#### Verification & Evidence
All regression assertions recorded with deterministic seed=42 and correlation trace evidence attached.

---

### [DOC-CART-20260518-14] Cart & Promotions: Sprint Planning Update #14 (2026-05-18)
<a id="doc-cart-20260518-14"></a>

- **Document ID**: `DOC-CART-20260518-14`
- **Date**: 2026-05-18 (`2026-05-18T10:31:50+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-008`](https://jira.northstar.invalid/browse/CART-008) (`Done`)
- **Record Type**: Sprint Planning Update

#### Context & Technical Objective
During sprint backlog commitment on [CART-008] (Merchant cart item maximum quantity limit constraints), the Cart & Promotions squad decomposed acceptance criteria, story point capacity, and cross-service dependencies.

#### Technical Decision & Invariants
Confirmed sprint scope and velocity guardrails. Unfinished items from prior closed iterations are formally tracked via sprint spillover transitions into the active sprint.

#### Verification & Evidence
Backlog readiness verified with product owner and QA lead; test fixtures and correlation IDs linked in Jira.

---

### [DOC-CART-20260518-15] Cart & Promotions: Feature Rollout Milestone #15 (2026-05-18)
<a id="doc-cart-20260518-15"></a>

- **Document ID**: `DOC-CART-20260518-15`
- **Date**: 2026-05-18 (`2026-05-18T10:47:34+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-024`](https://jira.northstar.invalid/browse/CART-024) (`In Progress`)
- **Record Type**: Feature Rollout Milestone

#### Context & Technical Objective
Staged canary rollout readiness check for [CART-024] (Bundle product component price breakdown in cart session — Edge-case race condition remediation) in Cart & Promotions.

#### Technical Decision & Invariants
Configured feature flag toggle and progressive traffic gates (0% synthetic -> 5% -> 25% -> 50% -> 100%) with automated rollback triggers.

#### Verification & Evidence
On-call SRE and workstream owner verified rollback runbook steps and alert routing.

---

### [DOC-CART-20260519-16] Cart & Promotions: Performance Benchmark Report #16 (2026-05-19)
<a id="doc-cart-20260519-16"></a>

- **Document ID**: `DOC-CART-20260519-16`
- **Date**: 2026-05-19 (`2026-05-19T13:54:49+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-021`](https://jira.northstar.invalid/browse/CART-021) (`Done`)
- **Record Type**: Performance Benchmark Report

#### Context & Technical Objective
Conducted load and latency profiling for [CART-021] (Cart currency conversion with cached FX exchange rates — Rate limiting & audit trail emission) in Cart & Promotions under the pilot reference workload.

#### Technical Decision & Invariants
Tuned PostgreSQL composite indexes and Redis lock TTLs to keep p95 latency within the approved service-level objective.

#### Verification & Evidence
Measured p95 response times, connection pool saturation, and queue lag metrics on the staging telemetry dashboard.

---

### [DOC-CART-20260520-17] Cart & Promotions: Sprint Planning Update #17 (2026-05-20)
<a id="doc-cart-20260520-17"></a>

- **Document ID**: `DOC-CART-20260520-17`
- **Date**: 2026-05-20 (`2026-05-20T20:44:54+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-015`](https://jira.northstar.invalid/browse/CART-015) (`Done`)
- **Record Type**: Sprint Planning Update

#### Context & Technical Objective
During sprint backlog commitment on [CART-015] (Abandoned cart expiration workflow with automated stock release — Partner sandbox contract reconciliation), the Cart & Promotions squad decomposed acceptance criteria, story point capacity, and cross-service dependencies.

#### Technical Decision & Invariants
Confirmed sprint scope and velocity guardrails. Unfinished items from prior closed iterations are formally tracked via sprint spillover transitions into the active sprint.

#### Verification & Evidence
Backlog readiness verified with product owner and QA lead; test fixtures and correlation IDs linked in Jira.

---

### [DOC-CART-20260521-18] Cart & Promotions: Feature Rollout Milestone #18 (2026-05-21)
<a id="doc-cart-20260521-18"></a>

- **Document ID**: `DOC-CART-20260521-18`
- **Date**: 2026-05-21 (`2026-05-21T08:12:19+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-011`](https://jira.northstar.invalid/browse/CART-011) (`Done`)
- **Record Type**: Feature Rollout Milestone

#### Context & Technical Objective
Staged canary rollout readiness check for [CART-011] (Cart session TTL extension on user checkout interaction) in Cart & Promotions.

#### Technical Decision & Invariants
Configured feature flag toggle and progressive traffic gates (0% synthetic -> 5% -> 25% -> 50% -> 100%) with automated rollback triggers.

#### Verification & Evidence
On-call SRE and workstream owner verified rollback runbook steps and alert routing.

---

### [DOC-CART-20260521-19] Cart & Promotions: Performance Benchmark Report #19 (2026-05-21)
<a id="doc-cart-20260521-19"></a>

- **Document ID**: `DOC-CART-20260521-19`
- **Date**: 2026-05-21 (`2026-05-21T08:28:03+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-027`](https://jira.northstar.invalid/browse/CART-027) (`In Progress`)
- **Record Type**: Performance Benchmark Report

#### Context & Technical Objective
Conducted load and latency profiling for [CART-027] (Abandoned cart expiration workflow with automated stock release — Role-based access control policy enforcement) in Cart & Promotions under the pilot reference workload.

#### Technical Decision & Invariants
Tuned PostgreSQL composite indexes and Redis lock TTLs to keep p95 latency within the approved service-level objective.

#### Verification & Evidence
Measured p95 response times, connection pool saturation, and queue lag metrics on the staging telemetry dashboard.

---

### [DOC-CART-20260522-20] Cart & Promotions: Sprint Planning Update #20 (2026-05-22)
<a id="doc-cart-20260522-20"></a>

- **Document ID**: `DOC-CART-20260522-20`
- **Date**: 2026-05-22 (`2026-05-22T10:35:18+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-020`](https://jira.northstar.invalid/browse/CART-020) (`Done`)
- **Record Type**: Sprint Planning Update

#### Context & Technical Objective
During sprint backlog commitment on [CART-020] (Merchant cart item maximum quantity limit constraints — Idempotent retry & dead-letter telemetry), the Cart & Promotions squad decomposed acceptance criteria, story point capacity, and cross-service dependencies.

#### Technical Decision & Invariants
Confirmed sprint scope and velocity guardrails. Unfinished items from prior closed iterations are formally tracked via sprint spillover transitions into the active sprint.

#### Verification & Evidence
Backlog readiness verified with product owner and QA lead; test fixtures and correlation IDs linked in Jira.

---

### [DOC-CART-20260525-21] Cart & Promotions: Feature Rollout Milestone #21 (2026-05-25)
<a id="doc-cart-20260525-21"></a>

- **Document ID**: `DOC-CART-20260525-21`
- **Date**: 2026-05-25 (`2026-05-25T13:42:33+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-014`](https://jira.northstar.invalid/browse/CART-014) (`Done`)
- **Record Type**: Feature Rollout Milestone

#### Context & Technical Objective
Staged canary rollout readiness check for [CART-014] (Promotion stacking hierarchy and discount evaluation engine — Cache invalidation & version lineage check) in Cart & Promotions.

#### Technical Decision & Invariants
Configured feature flag toggle and progressive traffic gates (0% synthetic -> 5% -> 25% -> 50% -> 100%) with automated rollback triggers.

#### Verification & Evidence
On-call SRE and workstream owner verified rollback runbook steps and alert routing.

---

### [DOC-CART-20260525-22] Cart & Promotions: Performance Benchmark Report #22 (2026-05-25)
<a id="doc-cart-20260525-22"></a>

- **Document ID**: `DOC-CART-20260525-22`
- **Date**: 2026-05-25 (`2026-05-25T17:23:13+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-030`](https://jira.northstar.invalid/browse/CART-030) (`In Review`)
- **Record Type**: Performance Benchmark Report

#### Context & Technical Objective
Conducted load and latency profiling for [CART-030] (Immutable cart audit transition event logging — Data retention & privacy masking compliance) in Cart & Promotions under the pilot reference workload.

#### Technical Decision & Invariants
Tuned PostgreSQL composite indexes and Redis lock TTLs to keep p95 latency within the approved service-level objective.

#### Verification & Evidence
Measured p95 response times, connection pool saturation, and queue lag metrics on the staging telemetry dashboard.

---

### [DOC-CART-20260526-23] Cart & Promotions: Architecture Decision Note #23 (2026-05-26)
<a id="doc-cart-20260526-23"></a>

- **Document ID**: `DOC-CART-20260526-23`
- **Date**: 2026-05-26 (`2026-05-26T16:14:41+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-027`](https://jira.northstar.invalid/browse/CART-027) (`In Progress`)
- **Record Type**: Architecture Decision Note

#### Context & Technical Objective
Architectural review for [CART-027] (Abandoned cart expiration workflow with automated stock release — Role-based access control policy enforcement) within Cart & Promotions, focusing on service ownership boundaries, failure compensation, and multi-tenant isolation.

#### Technical Decision & Invariants
Enforced strict tenant_id scoping at the repository layer and durable 72-hour idempotency keys for mutating operations.

#### Verification & Evidence
Design aligns with DOC-ORG-SDS-001; contract tests and sequence diagrams validated by the tech lead.

---

### [DOC-CART-20260527-24] Cart & Promotions: Incident Post-Mortem Action #24 (2026-05-27)
<a id="doc-cart-20260527-24"></a>

- **Document ID**: `DOC-CART-20260527-24`
- **Date**: 2026-05-27 (`2026-05-27T09:21:56+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-020`](https://jira.northstar.invalid/browse/CART-020) (`Done`)
- **Record Type**: Incident Post-Mortem Action

#### Context & Technical Objective
Follow-up remediation tracking for [CART-020] (Merchant cart item maximum quantity limit constraints — Idempotent retry & dead-letter telemetry) in Cart & Promotions after staging fault-injection and replay testing.

#### Technical Decision & Invariants
Added transactional outbox and unique inbox constraints so worker restarts or network retries cannot duplicate side effects.

#### Verification & Evidence
Crash-replay simulation added to continuous integration to prevent regression.

---

### [DOC-CART-20260528-25] Cart & Promotions: Merchant Sync Decision #25 (2026-05-28)
<a id="doc-cart-20260528-25"></a>

- **Document ID**: `DOC-CART-20260528-25`
- **Date**: 2026-05-28 (`2026-05-28T11:28:11+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-017`](https://jira.northstar.invalid/browse/CART-017) (`Done`)
- **Record Type**: Merchant Sync Decision

#### Context & Technical Objective
Reviewed Meridian Outfitters pilot integration requirements for [CART-017] (Idempotent cart item updates during concurrent requests — Storefront response serialization & pagination) with Cart & Promotions engineering and merchant support.

#### Technical Decision & Invariants
Confirmed tenant-isolated configuration rules, CSV batch error reporting, and SFTP nightly sync schedule at 02:00+07:00.

#### Verification & Evidence
Action items logged with merchant onboarding specialists and verified against tenant boundary checks.

---

### [DOC-CART-20260528-26] Cart & Promotions: Architecture Decision Note #26 (2026-05-28)
<a id="doc-cart-20260528-26"></a>

- **Document ID**: `DOC-CART-20260528-26`
- **Date**: 2026-05-28 (`2026-05-28T11:44:55+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-033`](https://jira.northstar.invalid/browse/CART-033) (`In Review`)
- **Record Type**: Architecture Decision Note

#### Context & Technical Objective
Architectural review for [CART-033] (Cart currency conversion with cached FX exchange rates — Backfill worker & batch memory tuning) within Cart & Promotions, focusing on service ownership boundaries, failure compensation, and multi-tenant isolation.

#### Technical Decision & Invariants
Enforced strict tenant_id scoping at the repository layer and durable 72-hour idempotency keys for mutating operations.

#### Verification & Evidence
Design aligns with DOC-ORG-SDS-001; contract tests and sequence diagrams validated by the tech lead.

---

### [DOC-CART-20260529-27] Cart & Promotions: Incident Post-Mortem Action #27 (2026-05-29)
<a id="doc-cart-20260529-27"></a>

- **Document ID**: `DOC-CART-20260529-27`
- **Date**: 2026-05-29 (`2026-05-29T14:51:10+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-026`](https://jira.northstar.invalid/browse/CART-026) (`Done`)
- **Record Type**: Incident Post-Mortem Action

#### Context & Technical Objective
Follow-up remediation tracking for [CART-026] (Promotion stacking hierarchy and discount evaluation engine — Load test benchmark & p95 latency profiling) in Cart & Promotions after staging fault-injection and replay testing.

#### Technical Decision & Invariants
Added transactional outbox and unique inbox constraints so worker restarts or network retries cannot duplicate side effects.

#### Verification & Evidence
Crash-replay simulation added to continuous integration to prevent regression.

---
