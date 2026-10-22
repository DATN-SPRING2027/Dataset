---
bundle_id: "BUNDLE-NSC-CART-2026-09"
project_id: "NSC-CART"
project_name: "Cart & Promotions"
period: "2026-09"
classification: "Internal"
access_groups: ["GRP-CART"]
logical_document_count: 27
synthetic: true
---

# Cart & Promotions — Monthly Engineering Records (2026-09)

This Markdown bundle organizes 27 verified logical project records, decisions, meeting outcomes, and technical milestone updates for NSC-CART during 2026-09.

### [DOC-CART-20260903-01] Cart & Promotions: Sprint Planning Update #1 (2026-09-03)
<a id="doc-cart-20260903-01"></a>

- **Document ID**: `DOC-CART-20260903-01`
- **Date**: 2026-09-03 (`2026-09-03T15:23:54+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-080`](https://jira.northstar.invalid/browse/CART-080) (`Done`)
- **Record Type**: Sprint Planning Update

#### Context & Technical Objective
During sprint backlog commitment on [CART-080] (Merchant cart item maximum quantity limit constraints — Webhook signature & payload verification), the Cart & Promotions squad decomposed acceptance criteria, story point capacity, and cross-service dependencies.

#### Technical Decision & Invariants
Confirmed sprint scope and velocity guardrails. Unfinished items from prior closed iterations are formally tracked via sprint spillover transitions into the active sprint.

#### Verification & Evidence
Backlog readiness verified with product owner and QA lead; test fixtures and correlation IDs linked in Jira.

---

### [DOC-CART-20260904-02] Cart & Promotions: Feature Rollout Milestone #2 (2026-09-04)
<a id="doc-cart-20260904-02"></a>

- **Document ID**: `DOC-CART-20260904-02`
- **Date**: 2026-09-04 (`2026-09-04T08:30:09+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-073`](https://jira.northstar.invalid/browse/CART-073) (`In Review`)
- **Record Type**: Feature Rollout Milestone

#### Context & Technical Objective
Staged canary rollout readiness check for [CART-073] (Guest cart merging into customer account upon login — Edge-case race condition remediation) in Cart & Promotions.

#### Technical Decision & Invariants
Configured feature flag toggle and progressive traffic gates (0% synthetic -> 5% -> 25% -> 50% -> 100%) with automated rollback triggers.

#### Verification & Evidence
On-call SRE and workstream owner verified rollback runbook steps and alert routing.

---

### [DOC-CART-20260904-03] Cart & Promotions: Performance Benchmark Report #3 (2026-09-04)
<a id="doc-cart-20260904-03"></a>

- **Document ID**: `DOC-CART-20260904-03`
- **Date**: 2026-09-04 (`2026-09-04T21:51:37+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-089`](https://jira.northstar.invalid/browse/CART-089) (`Done`)
- **Record Type**: Performance Benchmark Report

#### Context & Technical Objective
Conducted load and latency profiling for [CART-089] (Idempotent cart item updates during concurrent requests — API contract & schema validation) in Cart & Promotions under the pilot reference workload.

#### Technical Decision & Invariants
Tuned PostgreSQL composite indexes and Redis lock TTLs to keep p95 latency within the approved service-level objective.

#### Verification & Evidence
Measured p95 response times, connection pool saturation, and queue lag metrics on the staging telemetry dashboard.

---

### [DOC-CART-20260907-04] Cart & Promotions: Sprint Planning Update #4 (2026-09-07)
<a id="doc-cart-20260907-04"></a>

- **Document ID**: `DOC-CART-20260907-04`
- **Date**: 2026-09-07 (`2026-09-07T10:53:08+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-086`](https://jira.northstar.invalid/browse/CART-086) (`Done`)
- **Record Type**: Sprint Planning Update

#### Context & Technical Objective
During sprint backlog commitment on [CART-086] (Promotion stacking hierarchy and discount evaluation engine — Boundary value & currency minor-unit validation), the Cart & Promotions squad decomposed acceptance criteria, story point capacity, and cross-service dependencies.

#### Technical Decision & Invariants
Confirmed sprint scope and velocity guardrails. Unfinished items from prior closed iterations are formally tracked via sprint spillover transitions into the active sprint.

#### Verification & Evidence
Backlog readiness verified with product owner and QA lead; test fixtures and correlation IDs linked in Jira.

---

### [DOC-CART-20260908-05] Cart & Promotions: Feature Rollout Milestone #5 (2026-09-08)
<a id="doc-cart-20260908-05"></a>

- **Document ID**: `DOC-CART-20260908-05`
- **Date**: 2026-09-08 (`2026-09-08T21:29:51+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-079`](https://jira.northstar.invalid/browse/CART-079) (`Blocked`)
- **Record Type**: Feature Rollout Milestone

#### Context & Technical Objective
Staged canary rollout readiness check for [CART-079] (Fixed-amount and percentage tier coupon discounts — Merchant admin UI state & error boundary) in Cart & Promotions.

#### Technical Decision & Invariants
Configured feature flag toggle and progressive traffic gates (0% synthetic -> 5% -> 25% -> 50% -> 100%) with automated rollback triggers.

#### Verification & Evidence
On-call SRE and workstream owner verified rollback runbook steps and alert routing.

---

### [DOC-CART-20260909-06] Cart & Promotions: Merchant Sync Decision #6 (2026-09-09)
<a id="doc-cart-20260909-06"></a>

- **Document ID**: `DOC-CART-20260909-06`
- **Date**: 2026-09-09 (`2026-09-09T16:16:47+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-077`](https://jira.northstar.invalid/browse/CART-077) (`Done`)
- **Record Type**: Merchant Sync Decision

#### Context & Technical Objective
Reviewed Meridian Outfitters pilot integration requirements for [CART-077] (Idempotent cart item updates during concurrent requests — Cross-service correlation ID propagation) with Cart & Promotions engineering and merchant support.

#### Technical Decision & Invariants
Confirmed tenant-isolated configuration rules, CSV batch error reporting, and SFTP nightly sync schedule at 02:00+07:00.

#### Verification & Evidence
Action items logged with merchant onboarding specialists and verified against tenant boundary checks.

---

### [DOC-CART-20260909-07] Cart & Promotions: Architecture Decision Note #7 (2026-09-09)
<a id="doc-cart-20260909-07"></a>

- **Document ID**: `DOC-CART-20260909-07`
- **Date**: 2026-09-09 (`2026-09-09T16:32:31+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-093`](https://jira.northstar.invalid/browse/CART-093) (`In Review`)
- **Record Type**: Architecture Decision Note

#### Context & Technical Objective
Architectural review for [CART-093] (Cart currency conversion with cached FX exchange rates — Database expand-contract migration script) within Cart & Promotions, focusing on service ownership boundaries, failure compensation, and multi-tenant isolation.

#### Technical Decision & Invariants
Enforced strict tenant_id scoping at the repository layer and durable 72-hour idempotency keys for mutating operations.

#### Verification & Evidence
Design aligns with DOC-ORG-SDS-001; contract tests and sequence diagrams validated by the tech lead.

---

### [DOC-CART-20260910-08] Cart & Promotions: Incident Post-Mortem Action #8 (2026-09-10)
<a id="doc-cart-20260910-08"></a>

- **Document ID**: `DOC-CART-20260910-08`
- **Date**: 2026-09-10 (`2026-09-10T09:39:46+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-086`](https://jira.northstar.invalid/browse/CART-086) (`Done`)
- **Record Type**: Incident Post-Mortem Action

#### Context & Technical Objective
Follow-up remediation tracking for [CART-086] (Promotion stacking hierarchy and discount evaluation engine — Boundary value & currency minor-unit validation) in Cart & Promotions after staging fault-injection and replay testing.

#### Technical Decision & Invariants
Added transactional outbox and unique inbox constraints so worker restarts or network retries cannot duplicate side effects.

#### Verification & Evidence
Crash-replay simulation added to continuous integration to prevent regression.

---

### [DOC-CART-20260911-09] Cart & Promotions: Merchant Sync Decision #9 (2026-09-11)
<a id="doc-cart-20260911-09"></a>

- **Document ID**: `DOC-CART-20260911-09`
- **Date**: 2026-09-11 (`2026-09-11T11:46:01+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-083`](https://jira.northstar.invalid/browse/CART-083) (`Done`)
- **Record Type**: Merchant Sync Decision

#### Context & Technical Objective
Reviewed Meridian Outfitters pilot integration requirements for [CART-083] (Cart session TTL extension on user checkout interaction — Role-based access control policy enforcement) with Cart & Promotions engineering and merchant support.

#### Technical Decision & Invariants
Confirmed tenant-isolated configuration rules, CSV batch error reporting, and SFTP nightly sync schedule at 02:00+07:00.

#### Verification & Evidence
Action items logged with merchant onboarding specialists and verified against tenant boundary checks.

---

### [DOC-CART-20260914-10] Cart & Promotions: Architecture Decision Note #10 (2026-09-14)
<a id="doc-cart-20260914-10"></a>

- **Document ID**: `DOC-CART-20260914-10`
- **Date**: 2026-09-14 (`2026-09-14T14:53:16+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-076`](https://jira.northstar.invalid/browse/CART-076) (`To Do`)
- **Record Type**: Architecture Decision Note

#### Context & Technical Objective
Architectural review for [CART-076] (Order line total recalculation after real-time inventory adjustments — Security header & token scope hardening) within Cart & Promotions, focusing on service ownership boundaries, failure compensation, and multi-tenant isolation.

#### Technical Decision & Invariants
Enforced strict tenant_id scoping at the repository layer and durable 72-hour idempotency keys for mutating operations.

#### Verification & Evidence
Design aligns with DOC-ORG-SDS-001; contract tests and sequence diagrams validated by the tech lead.

---

### [DOC-CART-20260914-11] Cart & Promotions: Incident Post-Mortem Action #11 (2026-09-14)
<a id="doc-cart-20260914-11"></a>

- **Document ID**: `DOC-CART-20260914-11`
- **Date**: 2026-09-14 (`2026-09-14T14:13:00+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-092`](https://jira.northstar.invalid/browse/CART-092) (`Done`)
- **Record Type**: Incident Post-Mortem Action

#### Context & Technical Objective
Follow-up remediation tracking for [CART-092] (Merchant cart item maximum quantity limit constraints — Timeout fallback & circuit breaker logic) in Cart & Promotions after staging fault-injection and replay testing.

#### Technical Decision & Invariants
Added transactional outbox and unique inbox constraints so worker restarts or network retries cannot duplicate side effects.

#### Verification & Evidence
Crash-replay simulation added to continuous integration to prevent regression.

---

### [DOC-CART-20260915-12] Cart & Promotions: Merchant Sync Decision #12 (2026-09-15)
<a id="doc-cart-20260915-12"></a>

- **Document ID**: `DOC-CART-20260915-12`
- **Date**: 2026-09-15 (`2026-09-15T16:20:15+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-085`](https://jira.northstar.invalid/browse/CART-085) (`Done`)
- **Record Type**: Merchant Sync Decision

#### Context & Technical Objective
Reviewed Meridian Outfitters pilot integration requirements for [CART-085] (Guest cart merging into customer account upon login — Partner sandbox contract reconciliation) with Cart & Promotions engineering and merchant support.

#### Technical Decision & Invariants
Confirmed tenant-isolated configuration rules, CSV batch error reporting, and SFTP nightly sync schedule at 02:00+07:00.

#### Verification & Evidence
Action items logged with merchant onboarding specialists and verified against tenant boundary checks.

---

### [DOC-CART-20260916-13] Cart & Promotions: Architecture Decision Note #13 (2026-09-16)
<a id="doc-cart-20260916-13"></a>

- **Document ID**: `DOC-CART-20260916-13`
- **Date**: 2026-09-16 (`2026-09-16T09:27:30+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-082`](https://jira.northstar.invalid/browse/CART-082) (`Done`)
- **Record Type**: Architecture Decision Note

#### Context & Technical Objective
Architectural review for [CART-082] (Cart coupon eligibility against customer group rules — Load test benchmark & p95 latency profiling) within Cart & Promotions, focusing on service ownership boundaries, failure compensation, and multi-tenant isolation.

#### Technical Decision & Invariants
Enforced strict tenant_id scoping at the repository layer and durable 72-hour idempotency keys for mutating operations.

#### Verification & Evidence
Design aligns with DOC-ORG-SDS-001; contract tests and sequence diagrams validated by the tech lead.

---

### [DOC-CART-20260916-14] Cart & Promotions: Incident Post-Mortem Action #14 (2026-09-16)
<a id="doc-cart-20260916-14"></a>

- **Document ID**: `DOC-CART-20260916-14`
- **Date**: 2026-09-16 (`2026-09-16T20:02:56+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-098`](https://jira.northstar.invalid/browse/CART-098) (`Done`)
- **Record Type**: Incident Post-Mortem Action

#### Context & Technical Objective
Follow-up remediation tracking for [CART-098] (Promotion stacking hierarchy and discount evaluation engine — Event outbox deduplication & ordering) in Cart & Promotions after staging fault-injection and replay testing.

#### Technical Decision & Invariants
Added transactional outbox and unique inbox constraints so worker restarts or network retries cannot duplicate side effects.

#### Verification & Evidence
Crash-replay simulation added to continuous integration to prevent regression.

---

### [DOC-CART-20260917-15] Cart & Promotions: Daily Standup & Blocker Log #15 (2026-09-17)
<a id="doc-cart-20260917-15"></a>

- **Document ID**: `DOC-CART-20260917-15`
- **Date**: 2026-09-17 (`2026-09-17T13:55:38+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-092`](https://jira.northstar.invalid/browse/CART-092) (`Done`)
- **Record Type**: Daily Standup & Blocker Log

#### Context & Technical Objective
Daily engineering standup checkpoint for Cart & Promotions covering active work on [CART-092] (Merchant cart item maximum quantity limit constraints — Timeout fallback & circuit breaker logic) (current ticket status: `Done`).

#### Technical Decision & Invariants
Reviewed upstream sandbox dependencies, PR review queue, and evening overtime (17:00–22:00+07:00) handoffs during sprint crunch.

#### Verification & Evidence
Updated Jira status transitions, blocker owners, and same-day escalation checkpoints.

---

### [DOC-CART-20260918-16] Cart & Promotions: API Contract Revision #16 (2026-09-18)
<a id="doc-cart-20260918-16"></a>

- **Document ID**: `DOC-CART-20260918-16`
- **Date**: 2026-09-18 (`2026-09-18T15:06:53+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-089`](https://jira.northstar.invalid/browse/CART-089) (`Done`)
- **Record Type**: API Contract Revision

#### Context & Technical Objective
Evaluated HTTP request/response payload schemas for [CART-089] (Idempotent cart item updates during concurrent requests — API contract & schema validation) in Cart & Promotions to ensure backward compatibility and deterministic error codes.

#### Technical Decision & Invariants
Standardized monetary fields to integer minor currency units alongside ISO 4217 currency codes; added explicit HTTP 409 conflict and HTTP 422 field validation responses.

#### Verification & Evidence
API schema snapshot tested against staging-sim consumer stubs with zero breaking changes.

---

### [DOC-CART-20260921-17] Cart & Promotions: Database Migration Checklist #17 (2026-09-21)
<a id="doc-cart-20260921-17"></a>

- **Document ID**: `DOC-CART-20260921-17`
- **Date**: 2026-09-21 (`2026-09-21T08:13:08+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-082`](https://jira.northstar.invalid/browse/CART-082) (`Done`)
- **Record Type**: Database Migration Checklist

#### Context & Technical Objective
Database schema change verification for [CART-082] (Cart coupon eligibility against customer group rules — Load test benchmark & p95 latency profiling) managed by Cart & Promotions.

#### Technical Decision & Invariants
Applied expand/contract migration sequencing: nullable/default columns and concurrent indexes deployed ahead of application readers/writers.

#### Verification & Evidence
Forward/down recovery notes and row-count reconciliation verified against isolated backup snapshot.

---

### [DOC-CART-20260921-18] Cart & Promotions: Daily Standup & Blocker Log #18 (2026-09-21)
<a id="doc-cart-20260921-18"></a>

- **Document ID**: `DOC-CART-20260921-18`
- **Date**: 2026-09-21 (`2026-09-21T08:29:52+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-098`](https://jira.northstar.invalid/browse/CART-098) (`Done`)
- **Record Type**: Daily Standup & Blocker Log

#### Context & Technical Objective
Daily engineering standup checkpoint for Cart & Promotions covering active work on [CART-098] (Promotion stacking hierarchy and discount evaluation engine — Event outbox deduplication & ordering) (current ticket status: `Done`).

#### Technical Decision & Invariants
Reviewed upstream sandbox dependencies, PR review queue, and evening overtime (17:00–22:00+07:00) handoffs during sprint crunch.

#### Verification & Evidence
Updated Jira status transitions, blocker owners, and same-day escalation checkpoints.

---

### [DOC-CART-20260922-19] Cart & Promotions: API Contract Revision #19 (2026-09-22)
<a id="doc-cart-20260922-19"></a>

- **Document ID**: `DOC-CART-20260922-19`
- **Date**: 2026-09-22 (`2026-09-22T10:36:07+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-091`](https://jira.northstar.invalid/browse/CART-091) (`Done`)
- **Record Type**: API Contract Revision

#### Context & Technical Objective
Evaluated HTTP request/response payload schemas for [CART-091] (Fixed-amount and percentage tier coupon discounts — Rate limiting & audit trail emission) in Cart & Promotions to ensure backward compatibility and deterministic error codes.

#### Technical Decision & Invariants
Standardized monetary fields to integer minor currency units alongside ISO 4217 currency codes; added explicit HTTP 409 conflict and HTTP 422 field validation responses.

#### Verification & Evidence
API schema snapshot tested against staging-sim consumer stubs with zero breaking changes.

---

### [DOC-CART-20260923-20] Cart & Promotions: Database Migration Checklist #20 (2026-09-23)
<a id="doc-cart-20260923-20"></a>

- **Document ID**: `DOC-CART-20260923-20`
- **Date**: 2026-09-23 (`2026-09-23T13:43:22+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-088`](https://jira.northstar.invalid/browse/CART-088) (`Done`)
- **Record Type**: Database Migration Checklist

#### Context & Technical Objective
Database schema change verification for [CART-088] (Order line total recalculation after real-time inventory adjustments — Operational runbook & support diagnostics) managed by Cart & Promotions.

#### Technical Decision & Invariants
Applied expand/contract migration sequencing: nullable/default columns and concurrent indexes deployed ahead of application readers/writers.

#### Verification & Evidence
Forward/down recovery notes and row-count reconciliation verified against isolated backup snapshot.

---

### [DOC-CART-20260924-21] Cart & Promotions: Daily Standup & Blocker Log #21 (2026-09-24)
<a id="doc-cart-20260924-21"></a>

- **Document ID**: `DOC-CART-20260924-21`
- **Date**: 2026-09-24 (`2026-09-24T15:50:37+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-081`](https://jira.northstar.invalid/browse/CART-081) (`Done`)
- **Record Type**: Daily Standup & Blocker Log

#### Context & Technical Objective
Daily engineering standup checkpoint for Cart & Promotions covering active work on [CART-081] (Cart currency conversion with cached FX exchange rates — Observability spans & SLO alert thresholds) (current ticket status: `Done`).

#### Technical Decision & Invariants
Reviewed upstream sandbox dependencies, PR review queue, and evening overtime (17:00–22:00+07:00) handoffs during sprint crunch.

#### Verification & Evidence
Updated Jira status transitions, blocker owners, and same-day escalation checkpoints.

---

### [DOC-CART-20260924-22] Cart & Promotions: API Contract Revision #22 (2026-09-24)
<a id="doc-cart-20260924-22"></a>

- **Document ID**: `DOC-CART-20260924-22`
- **Date**: 2026-09-24 (`2026-09-24T15:10:21+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-097`](https://jira.northstar.invalid/browse/CART-097) (`Done`)
- **Record Type**: API Contract Revision

#### Context & Technical Objective
Evaluated HTTP request/response payload schemas for [CART-097] (Guest cart merging into customer account upon login — Role-based access control policy enforcement) in Cart & Promotions to ensure backward compatibility and deterministic error codes.

#### Technical Decision & Invariants
Standardized monetary fields to integer minor currency units alongside ISO 4217 currency codes; added explicit HTTP 409 conflict and HTTP 422 field validation responses.

#### Verification & Evidence
API schema snapshot tested against staging-sim consumer stubs with zero breaking changes.

---

### [DOC-CART-20260925-23] Cart & Promotions: Integration Review Notes #23 (2026-09-25)
<a id="doc-cart-20260925-23"></a>

- **Document ID**: `DOC-CART-20260925-23`
- **Date**: 2026-09-25 (`2026-09-25T19:07:05+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-095`](https://jira.northstar.invalid/browse/CART-095) (`Done`)
- **Record Type**: Integration Review Notes

#### Context & Technical Objective
Cross-service and partner integration sync for [CART-095] (Cart session TTL extension on user checkout interaction — Automated recovery & rollback verification) in Cart & Promotions.

#### Technical Decision & Invariants
Verified HMAC-SHA256 webhook signature validation, bounded exponential backoff with jitter, and correlation ID propagation across service hops.

#### Verification & Evidence
Sandbox integration trace captured and linked to the requirement traceability matrix.

---

### [DOC-CART-20260928-24] Cart & Promotions: Security Review Note #24 (2026-09-28)
<a id="doc-cart-20260928-24"></a>

- **Document ID**: `DOC-CART-20260928-24`
- **Date**: 2026-09-28 (`2026-09-28T11:29:00+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-088`](https://jira.northstar.invalid/browse/CART-088) (`Done`)
- **Record Type**: Security Review Note

#### Context & Technical Objective
Application security and access-control assessment for [CART-088] (Order line total recalculation after real-time inventory adjustments — Operational runbook & support diagnostics) in Cart & Promotions.

#### Technical Decision & Invariants
Validated deny-by-default authorization, pre-retrieval ACL filtering, secret externalization, and zero persistence of PAN/CVV or raw credentials.

#### Verification & Evidence
AppSec sign-off recorded; negative cross-tenant and revoked-user probes passed in CI.

---

### [DOC-CART-20260928-25] Cart & Promotions: Regression Test Summary #25 (2026-09-28)
<a id="doc-cart-20260928-25"></a>

- **Document ID**: `DOC-CART-20260928-25`
- **Date**: 2026-09-28 (`2026-09-28T20:16:26+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-104`](https://jira.northstar.invalid/browse/CART-104) (`In Progress`)
- **Record Type**: Regression Test Summary

#### Context & Technical Objective
Executed automated regression and negative boundary suite for [CART-104] (Merchant cart item maximum quantity limit constraints — Multi-tenant isolation & negative permission checks) across Cart & Promotions staging fixtures.

#### Technical Decision & Invariants
Verified idempotent replay, duplicate event suppression, and cross-tenant HTTP 403 rejection before snippet or count generation.

#### Verification & Evidence
All regression assertions recorded with deterministic seed=42 and correlation trace evidence attached.

---

### [DOC-CART-20260929-26] Cart & Promotions: Integration Review Notes #26 (2026-09-29)
<a id="doc-cart-20260929-26"></a>

- **Document ID**: `DOC-CART-20260929-26`
- **Date**: 2026-09-29 (`2026-09-29T14:52:59+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-101`](https://jira.northstar.invalid/browse/CART-101) (`Done`)
- **Record Type**: Integration Review Notes

#### Context & Technical Objective
Cross-service and partner integration sync for [CART-101] (Idempotent cart item updates during concurrent requests — PostgreSQL indexing & tenant query guard) in Cart & Promotions.

#### Technical Decision & Invariants
Verified HMAC-SHA256 webhook signature validation, bounded exponential backoff with jitter, and correlation ID propagation across service hops.

#### Verification & Evidence
Sandbox integration trace captured and linked to the requirement traceability matrix.

---

### [DOC-CART-20260930-27] Cart & Promotions: Security Review Note #27 (2026-09-30)
<a id="doc-cart-20260930-27"></a>

- **Document ID**: `DOC-CART-20260930-27`
- **Date**: 2026-09-30 (`2026-09-30T16:03:14+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-094`](https://jira.northstar.invalid/browse/CART-094) (`Done`)
- **Record Type**: Security Review Note

#### Context & Technical Objective
Application security and access-control assessment for [CART-094] (Cart coupon eligibility against customer group rules — Edge-case race condition remediation) in Cart & Promotions.

#### Technical Decision & Invariants
Validated deny-by-default authorization, pre-retrieval ACL filtering, secret externalization, and zero persistence of PAN/CVV or raw credentials.

#### Verification & Evidence
AppSec sign-off recorded; negative cross-tenant and revoked-user probes passed in CI.

---
