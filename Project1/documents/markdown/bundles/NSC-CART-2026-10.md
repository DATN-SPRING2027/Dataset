---
bundle_id: "BUNDLE-NSC-CART-2026-10"
project_id: "NSC-CART"
project_name: "Cart & Promotions"
period: "2026-10"
classification: "Internal"
access_groups: ["GRP-CART"]
logical_document_count: 11
synthetic: true
---

# Cart & Promotions — Monthly Engineering Records (2026-10)

This Markdown bundle organizes 11 verified logical project records, decisions, meeting outcomes, and technical milestone updates for NSC-CART during 2026-10.

### [DOC-CART-20261001-01] Cart & Promotions: Regression Test Summary #1 (2026-10-01)
<a id="doc-cart-20261001-01"></a>

- **Document ID**: `DOC-CART-20261001-01`
- **Date**: 2026-10-01 (`2026-10-01T20:11:17+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-087`](https://jira.northstar.invalid/browse/CART-087) (`To Do`)
- **Record Type**: Regression Test Summary

#### Context & Technical Objective
Executed automated regression and negative boundary suite for [CART-087] (Abandoned cart expiration workflow with automated stock release — Storefront response serialization & pagination) across Cart & Promotions staging fixtures.

#### Technical Decision & Invariants
Verified idempotent replay, duplicate event suppression, and cross-tenant HTTP 403 rejection before snippet or count generation.

#### Verification & Evidence
All regression assertions recorded with deterministic seed=42 and correlation trace evidence attached.

---

### [DOC-CART-20261001-02] Cart & Promotions: Integration Review Notes #2 (2026-10-01)
<a id="doc-cart-20261001-02"></a>

- **Document ID**: `DOC-CART-20261001-02`
- **Date**: 2026-10-01 (`2026-10-01T09:26:13+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-103`](https://jira.northstar.invalid/browse/CART-103) (`Done`)
- **Record Type**: Integration Review Notes

#### Context & Technical Objective
Cross-service and partner integration sync for [CART-103] (Fixed-amount and percentage tier coupon discounts — Backfill worker & batch memory tuning) in Cart & Promotions.

#### Technical Decision & Invariants
Verified HMAC-SHA256 webhook signature validation, bounded exponential backoff with jitter, and correlation ID propagation across service hops.

#### Verification & Evidence
Sandbox integration trace captured and linked to the requirement traceability matrix.

---

### [DOC-CART-20261002-03] Cart & Promotions: Security Review Note #3 (2026-10-02)
<a id="doc-cart-20261002-03"></a>

- **Document ID**: `DOC-CART-20261002-03`
- **Date**: 2026-10-02 (`2026-10-02T11:33:28+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-101`](https://jira.northstar.invalid/browse/CART-101) (`Done`)
- **Record Type**: Security Review Note

#### Context & Technical Objective
Application security and access-control assessment for [CART-101] (Idempotent cart item updates during concurrent requests — PostgreSQL indexing & tenant query guard) in Cart & Promotions.

#### Technical Decision & Invariants
Validated deny-by-default authorization, pre-retrieval ACL filtering, secret externalization, and zero persistence of PAN/CVV or raw credentials.

#### Verification & Evidence
AppSec sign-off recorded; negative cross-tenant and revoked-user probes passed in CI.

---

### [DOC-CART-20261005-04] Cart & Promotions: Performance Benchmark Report #4 (2026-10-05)
<a id="doc-cart-20261005-04"></a>

- **Document ID**: `DOC-CART-20261005-04`
- **Date**: 2026-10-05 (`2026-10-05T15:45:52+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-095`](https://jira.northstar.invalid/browse/CART-095) (`Done`)
- **Record Type**: Performance Benchmark Report

#### Context & Technical Objective
Conducted load and latency profiling for [CART-095] (Cart session TTL extension on user checkout interaction — Automated recovery & rollback verification) in Cart & Promotions under the pilot reference workload.

#### Technical Decision & Invariants
Tuned PostgreSQL composite indexes and Redis lock TTLs to keep p95 latency within the approved service-level objective.

#### Verification & Evidence
Measured p95 response times, connection pool saturation, and queue lag metrics on the staging telemetry dashboard.

---

### [DOC-CART-20261006-05] Cart & Promotions: Sprint Planning Update #5 (2026-10-06)
<a id="doc-cart-20261006-05"></a>

- **Document ID**: `DOC-CART-20261006-05`
- **Date**: 2026-10-06 (`2026-10-06T17:05:03+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-091`](https://jira.northstar.invalid/browse/CART-091) (`Done`)
- **Record Type**: Sprint Planning Update

#### Context & Technical Objective
During sprint backlog commitment on [CART-091] (Fixed-amount and percentage tier coupon discounts — Rate limiting & audit trail emission), the Cart & Promotions squad decomposed acceptance criteria, story point capacity, and cross-service dependencies.

#### Technical Decision & Invariants
Confirmed sprint scope and velocity guardrails. Unfinished items from prior closed iterations are formally tracked via sprint spillover transitions into the active sprint.

#### Verification & Evidence
Backlog readiness verified with product owner and QA lead; test fixtures and correlation IDs linked in Jira.

---

### [DOC-CART-20261006-06] Cart & Promotions: Feature Rollout Milestone #6 (2026-10-06)
<a id="doc-cart-20261006-06"></a>

- **Document ID**: `DOC-CART-20261006-06`
- **Date**: 2026-10-06 (`2026-10-06T08:12:51+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-108`](https://jira.northstar.invalid/browse/CART-108) (`Done`)
- **Record Type**: Feature Rollout Milestone

#### Context & Technical Objective
Staged canary rollout readiness check for [CART-108] (Bundle product component price breakdown in cart session — Storefront response serialization & pagination) in Cart & Promotions.

#### Technical Decision & Invariants
Configured feature flag toggle and progressive traffic gates (0% synthetic -> 5% -> 25% -> 50% -> 100%) with automated rollback triggers.

#### Verification & Evidence
On-call SRE and workstream owner verified rollback runbook steps and alert routing.

---

### [DOC-CART-20261007-07] Cart & Promotions: Performance Benchmark Report #7 (2026-10-07)
<a id="doc-cart-20261007-07"></a>

- **Document ID**: `DOC-CART-20261007-07`
- **Date**: 2026-10-07 (`2026-10-07T10:19:06+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-101`](https://jira.northstar.invalid/browse/CART-101) (`Done`)
- **Record Type**: Performance Benchmark Report

#### Context & Technical Objective
Conducted load and latency profiling for [CART-101] (Idempotent cart item updates during concurrent requests — PostgreSQL indexing & tenant query guard) in Cart & Promotions under the pilot reference workload.

#### Technical Decision & Invariants
Tuned PostgreSQL composite indexes and Redis lock TTLs to keep p95 latency within the approved service-level objective.

#### Verification & Evidence
Measured p95 response times, connection pool saturation, and queue lag metrics on the staging telemetry dashboard.

---

### [DOC-CART-20261008-08] Cart & Promotions: Sprint Planning Update #8 (2026-10-08)
<a id="doc-cart-20261008-08"></a>

- **Document ID**: `DOC-CART-20261008-08`
- **Date**: 2026-10-08 (`2026-10-08T13:26:21+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-097`](https://jira.northstar.invalid/browse/CART-097) (`Done`)
- **Record Type**: Sprint Planning Update

#### Context & Technical Objective
During sprint backlog commitment on [CART-097] (Guest cart merging into customer account upon login — Role-based access control policy enforcement), the Cart & Promotions squad decomposed acceptance criteria, story point capacity, and cross-service dependencies.

#### Technical Decision & Invariants
Confirmed sprint scope and velocity guardrails. Unfinished items from prior closed iterations are formally tracked via sprint spillover transitions into the active sprint.

#### Verification & Evidence
Backlog readiness verified with product owner and QA lead; test fixtures and correlation IDs linked in Jira.

---

### [DOC-CART-20261008-09] Cart & Promotions: Feature Rollout Milestone #9 (2026-10-08)
<a id="doc-cart-20261008-09"></a>

- **Document ID**: `DOC-CART-20261008-09`
- **Date**: 2026-10-08 (`2026-10-08T19:23:45+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-114`](https://jira.northstar.invalid/browse/CART-114) (`Done`)
- **Record Type**: Feature Rollout Milestone

#### Context & Technical Objective
Staged canary rollout readiness check for [CART-114] (Immutable cart audit transition event logging — Merchant admin UI state & error boundary) in Cart & Promotions.

#### Technical Decision & Invariants
Configured feature flag toggle and progressive traffic gates (0% synthetic -> 5% -> 25% -> 50% -> 100%) with automated rollback triggers.

#### Verification & Evidence
On-call SRE and workstream owner verified rollback runbook steps and alert routing.

---

### [DOC-CART-20261009-10] Cart & Promotions: Performance Benchmark Report #10 (2026-10-09)
<a id="doc-cart-20261009-10"></a>

- **Document ID**: `DOC-CART-20261009-10`
- **Date**: 2026-10-09 (`2026-10-09T19:40:22+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-118`](https://jira.northstar.invalid/browse/CART-118) (`Done`)
- **Record Type**: Performance Benchmark Report

#### Context & Technical Objective
Conducted load and latency profiling for [CART-118] (Cart coupon eligibility against customer group rules — Role-based access control policy enforcement) in Cart & Promotions under the pilot reference workload.

#### Technical Decision & Invariants
Tuned PostgreSQL composite indexes and Redis lock TTLs to keep p95 latency within the approved service-level objective.

#### Verification & Evidence
Measured p95 response times, connection pool saturation, and queue lag metrics on the staging telemetry dashboard.

---

### [DOC-CART-20261012-11] Cart & Promotions: Sprint Planning Update #11 (2026-10-12)
<a id="doc-cart-20261012-11"></a>

- **Document ID**: `DOC-CART-20261012-11`
- **Date**: 2026-10-12 (`2026-10-12T08:00:35+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-123`](https://jira.northstar.invalid/browse/CART-123) (`Done`)
- **Record Type**: Sprint Planning Update

#### Context & Technical Objective
During sprint backlog commitment on [CART-123] (Abandoned cart expiration workflow with automated stock release — Operational runbook & support diagnostics), the Cart & Promotions squad decomposed acceptance criteria, story point capacity, and cross-service dependencies.

#### Technical Decision & Invariants
Confirmed sprint scope and velocity guardrails. Unfinished items from prior closed iterations are formally tracked via sprint spillover transitions into the active sprint.

#### Verification & Evidence
Backlog readiness verified with product owner and QA lead; test fixtures and correlation IDs linked in Jira.

---
