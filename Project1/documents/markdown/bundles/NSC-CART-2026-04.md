---
bundle_id: "BUNDLE-NSC-CART-2026-04"
project_id: "NSC-CART"
project_name: "Cart & Promotions"
period: "2026-04"
classification: "Internal"
access_groups: ["GRP-CART"]
logical_document_count: 13
synthetic: true
---

# Cart & Promotions — Monthly Engineering Records (2026-04)

This Markdown bundle organizes 13 verified logical project records, decisions, meeting outcomes, and technical milestone updates for NSC-CART during 2026-04.

### [DOC-CART-20260416-01] Cart & Promotions: Merchant Sync Decision #1 (2026-04-16)
<a id="doc-cart-20260416-01"></a>

- **Document ID**: `DOC-CART-20260416-01`
- **Date**: 2026-04-16 (`2026-04-16T09:51:30+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-003`](https://jira.northstar.invalid/browse/CART-003) (`Done`)
- **Record Type**: Merchant Sync Decision

#### Context & Technical Objective
Reviewed Meridian Outfitters pilot integration requirements for [CART-003] (Abandoned cart expiration workflow with automated stock release) with Cart & Promotions engineering and merchant support.

#### Technical Decision & Invariants
Confirmed tenant-isolated configuration rules, CSV batch error reporting, and SFTP nightly sync schedule at 02:00+07:00.

#### Verification & Evidence
Action items logged with merchant onboarding specialists and verified against tenant boundary checks.

---

### [DOC-CART-20260416-02] Cart & Promotions: Architecture Decision Note #2 (2026-04-16)
<a id="doc-cart-20260416-02"></a>

- **Document ID**: `DOC-CART-20260416-02`
- **Date**: 2026-04-16 (`2026-04-16T20:02:16+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-001`](https://jira.northstar.invalid/browse/CART-001) (`Done`)
- **Record Type**: Architecture Decision Note

#### Context & Technical Objective
Architectural review for [CART-001] (Guest cart merging into customer account upon login) within Cart & Promotions, focusing on service ownership boundaries, failure compensation, and multi-tenant isolation.

#### Technical Decision & Invariants
Enforced strict tenant_id scoping at the repository layer and durable 72-hour idempotency keys for mutating operations.

#### Verification & Evidence
Design aligns with DOC-ORG-SDS-001; contract tests and sequence diagrams validated by the tech lead.

---

### [DOC-CART-20260417-03] Cart & Promotions: Incident Post-Mortem Action #3 (2026-04-17)
<a id="doc-cart-20260417-03"></a>

- **Document ID**: `DOC-CART-20260417-03`
- **Date**: 2026-04-17 (`2026-04-17T11:18:29+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-003`](https://jira.northstar.invalid/browse/CART-003) (`Done`)
- **Record Type**: Incident Post-Mortem Action

#### Context & Technical Objective
Follow-up remediation tracking for [CART-003] (Abandoned cart expiration workflow with automated stock release) in Cart & Promotions after staging fault-injection and replay testing.

#### Technical Decision & Invariants
Added transactional outbox and unique inbox constraints so worker restarts or network retries cannot duplicate side effects.

#### Verification & Evidence
Crash-replay simulation added to continuous integration to prevent regression.

---

### [DOC-CART-20260420-04] Cart & Promotions: Merchant Sync Decision #4 (2026-04-20)
<a id="doc-cart-20260420-04"></a>

- **Document ID**: `DOC-CART-20260420-04`
- **Date**: 2026-04-20 (`2026-04-20T14:25:44+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-004`](https://jira.northstar.invalid/browse/CART-004) (`In Progress`)
- **Record Type**: Merchant Sync Decision

#### Context & Technical Objective
Reviewed Meridian Outfitters pilot integration requirements for [CART-004] (Order line total recalculation after real-time inventory adjustments) with Cart & Promotions engineering and merchant support.

#### Technical Decision & Invariants
Confirmed tenant-isolated configuration rules, CSV batch error reporting, and SFTP nightly sync schedule at 02:00+07:00.

#### Verification & Evidence
Action items logged with merchant onboarding specialists and verified against tenant boundary checks.

---

### [DOC-CART-20260421-05] Cart & Promotions: Architecture Decision Note #5 (2026-04-21)
<a id="doc-cart-20260421-05"></a>

- **Document ID**: `DOC-CART-20260421-05`
- **Date**: 2026-04-21 (`2026-04-21T16:32:59+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-001`](https://jira.northstar.invalid/browse/CART-001) (`Done`)
- **Record Type**: Architecture Decision Note

#### Context & Technical Objective
Architectural review for [CART-001] (Guest cart merging into customer account upon login) within Cart & Promotions, focusing on service ownership boundaries, failure compensation, and multi-tenant isolation.

#### Technical Decision & Invariants
Enforced strict tenant_id scoping at the repository layer and durable 72-hour idempotency keys for mutating operations.

#### Verification & Evidence
Design aligns with DOC-ORG-SDS-001; contract tests and sequence diagrams validated by the tech lead.

---

### [DOC-CART-20260421-06] Cart & Promotions: Incident Post-Mortem Action #6 (2026-04-21)
<a id="doc-cart-20260421-06"></a>

- **Document ID**: `DOC-CART-20260421-06`
- **Date**: 2026-04-21 (`2026-04-21T16:48:43+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-004`](https://jira.northstar.invalid/browse/CART-004) (`In Progress`)
- **Record Type**: Incident Post-Mortem Action

#### Context & Technical Objective
Follow-up remediation tracking for [CART-004] (Order line total recalculation after real-time inventory adjustments) in Cart & Promotions after staging fault-injection and replay testing.

#### Technical Decision & Invariants
Added transactional outbox and unique inbox constraints so worker restarts or network retries cannot duplicate side effects.

#### Verification & Evidence
Crash-replay simulation added to continuous integration to prevent regression.

---

### [DOC-CART-20260422-07] Cart & Promotions: Merchant Sync Decision #7 (2026-04-22)
<a id="doc-cart-20260422-07"></a>

- **Document ID**: `DOC-CART-20260422-07`
- **Date**: 2026-04-22 (`2026-04-22T09:55:58+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-014`](https://jira.northstar.invalid/browse/CART-014) (`Done`)
- **Record Type**: Merchant Sync Decision

#### Context & Technical Objective
Reviewed Meridian Outfitters pilot integration requirements for [CART-014] (Promotion stacking hierarchy and discount evaluation engine — Cache invalidation & version lineage check) with Cart & Promotions engineering and merchant support.

#### Technical Decision & Invariants
Confirmed tenant-isolated configuration rules, CSV batch error reporting, and SFTP nightly sync schedule at 02:00+07:00.

#### Verification & Evidence
Action items logged with merchant onboarding specialists and verified against tenant boundary checks.

---

### [DOC-CART-20260423-08] Cart & Promotions: Architecture Decision Note #8 (2026-04-23)
<a id="doc-cart-20260423-08"></a>

- **Document ID**: `DOC-CART-20260423-08`
- **Date**: 2026-04-23 (`2026-04-23T11:06:13+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sofia Nguyen (`M-005`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-003`](https://jira.northstar.invalid/browse/CART-003) (`Done`)
- **Record Type**: Architecture Decision Note

#### Context & Technical Objective
Architectural review for [CART-003] (Abandoned cart expiration workflow with automated stock release) within Cart & Promotions, focusing on service ownership boundaries, failure compensation, and multi-tenant isolation.

#### Technical Decision & Invariants
Enforced strict tenant_id scoping at the repository layer and durable 72-hour idempotency keys for mutating operations.

#### Verification & Evidence
Design aligns with DOC-ORG-SDS-001; contract tests and sequence diagrams validated by the tech lead.

---

### [DOC-CART-20260424-09] Cart & Promotions: Incident Post-Mortem Action #9 (2026-04-24)
<a id="doc-cart-20260424-09"></a>

- **Document ID**: `DOC-CART-20260424-09`
- **Date**: 2026-04-24 (`2026-04-24T14:13:28+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-015`](https://jira.northstar.invalid/browse/CART-015) (`Done`)
- **Record Type**: Incident Post-Mortem Action

#### Context & Technical Objective
Follow-up remediation tracking for [CART-015] (Abandoned cart expiration workflow with automated stock release — Partner sandbox contract reconciliation) in Cart & Promotions after staging fault-injection and replay testing.

#### Technical Decision & Invariants
Added transactional outbox and unique inbox constraints so worker restarts or network retries cannot duplicate side effects.

#### Verification & Evidence
Crash-replay simulation added to continuous integration to prevent regression.

---

### [DOC-CART-20260424-10] Cart & Promotions: Merchant Sync Decision #10 (2026-04-24)
<a id="doc-cart-20260424-10"></a>

- **Document ID**: `DOC-CART-20260424-10`
- **Date**: 2026-04-24 (`2026-04-24T14:29:12+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Andrew Green (`M-052`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-012`](https://jira.northstar.invalid/browse/CART-012) (`Done`)
- **Record Type**: Merchant Sync Decision

#### Context & Technical Objective
Reviewed Meridian Outfitters pilot integration requirements for [CART-012] (Bundle product component price breakdown in cart session) with Cart & Promotions engineering and merchant support.

#### Technical Decision & Invariants
Confirmed tenant-isolated configuration rules, CSV batch error reporting, and SFTP nightly sync schedule at 02:00+07:00.

#### Verification & Evidence
Action items logged with merchant onboarding specialists and verified against tenant boundary checks.

---

### [DOC-CART-20260428-11] Cart & Promotions: API Contract Revision #11 (2026-04-28)
<a id="doc-cart-20260428-11"></a>

- **Document ID**: `DOC-CART-20260428-11`
- **Date**: 2026-04-28 (`2026-04-28T08:41:36+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Chloe Lopez (`M-049`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-005`](https://jira.northstar.invalid/browse/CART-005) (`Done`)
- **Record Type**: API Contract Revision

#### Context & Technical Objective
Evaluated HTTP request/response payload schemas for [CART-005] (Idempotent cart item updates during concurrent requests) in Cart & Promotions to ensure backward compatibility and deterministic error codes.

#### Technical Decision & Invariants
Standardized monetary fields to integer minor currency units alongside ISO 4217 currency codes; added explicit HTTP 409 conflict and HTTP 422 field validation responses.

#### Verification & Evidence
API schema snapshot tested against staging-sim consumer stubs with zero breaking changes.

---

### [DOC-CART-20260429-12] Cart & Promotions: Database Migration Checklist #12 (2026-04-29)
<a id="doc-cart-20260429-12"></a>

- **Document ID**: `DOC-CART-20260429-12`
- **Date**: 2026-04-29 (`2026-04-29T10:48:51+07:00`)
- **Work Shift**: Regular Business Hours (08:00–17:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-003`](https://jira.northstar.invalid/browse/CART-003) (`Done`)
- **Record Type**: Database Migration Checklist

#### Context & Technical Objective
Database schema change verification for [CART-003] (Abandoned cart expiration workflow with automated stock release) managed by Cart & Promotions.

#### Technical Decision & Invariants
Applied expand/contract migration sequencing: nullable/default columns and concurrent indexes deployed ahead of application readers/writers.

#### Verification & Evidence
Forward/down recovery notes and row-count reconciliation verified against isolated backup snapshot.

---

### [DOC-CART-20260429-13] Cart & Promotions: Daily Standup & Blocker Log #13 (2026-04-29)
<a id="doc-cart-20260429-13"></a>

- **Document ID**: `DOC-CART-20260429-13`
- **Date**: 2026-04-29 (`2026-04-29T19:09:35+07:00`)
- **Work Shift**: Evening Overtime (17:00–22:00+07:00)
- **Author**: Sophia Wilson (`M-024`)
- **Project**: `NSC-CART`
- **Scope**: `project`
- **Classification**: `Internal`
- **Access Groups**: `GRP-CART`
- **Linked Issue**: [`CART-019`](https://jira.northstar.invalid/browse/CART-019) (`Blocked`)
- **Record Type**: Daily Standup & Blocker Log

#### Context & Technical Objective
Daily engineering standup checkpoint for Cart & Promotions covering active work on [CART-019] (Fixed-amount and percentage tier coupon discounts — API contract & schema validation) (current ticket status: `Blocked`).

#### Technical Decision & Invariants
Reviewed upstream sandbox dependencies, PR review queue, and evening overtime (17:00–22:00+07:00) handoffs during sprint crunch.

#### Verification & Evidence
Updated Jira status transitions, blocker owners, and same-day escalation checkpoints.

---
