---
document_id: "DOC-ORG-RISK-001"
title: "Northstar Commerce Risk Register"
project_id: null
organization_id: "ORG-NSC"
scope: "organization"
owner_id: "M-001"
created_at: "2026-10-12"
updated_at: "2026-10-12"
version: "1.0"
status: "Approved"
classification: "Restricted"
access_groups: ["GRP-LEADERS", "GRP-SECURITY"]
source_issue_keys: ["CHKO-005", "PAY-002", "PLAT-009"]
canonical_document_id: "DOC-ORG-RISK-001"
rendition_paths: []
requirement_ids: []
file_path: "documents/markdown/formal/Risk_Register.md"
format: "markdown"
synthetic: true
---

# Northstar Commerce Risk Register

Owned risk statements, likelihood/impact, mitigation, contingency, review date, and residual status for pilot delivery.

## Scoring method

Likelihood and impact use a 1–5 scale; score is their product. High risks (15–25) require sponsor visibility and a funded mitigation. Scores describe the synthetic project snapshot and must be reassessed when evidence changes.

## Risk owners and review

Every risk has one accountable owner, mitigation, trigger, contingency, due date, linked issue, and residual status. The product manager reviews weekly; security and payment risks are reviewed at each release gate.

## Escalation

A risk becoming an incident triggers the incident response plan. A mitigation overdue by more than one checkpoint is escalated. Risk acceptance requires a named approver, rationale, compensating control, and expiry date.

## Risk register

| Risk ID | Risk | Likelihood | Impact | Owner | Mitigation | Trigger | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-001 | Concurrent checkout retries may create duplicate orders or captures | 4 | 5 | M-005 | Enforce unique durable idempotency and rerun concurrency case FT-CHKO-007 | FT-CHKO-007 fails | Open |
| RISK-002 | PulsePay certificate rotation may delay signed webhook verification | 4 | 4 | M-006 | Coordinate partner window and execute FT-PAY-008 | Certificate unavailable | Open |
| RISK-003 | Tenant context defects could expose another merchant's records | 2 | 5 | M-012 | Gateway-derived tenant scope and pre-retrieval ACL tests | Any cross-tenant signal | Mitigating |
| RISK-004 | Catalog sample may not represent the full production SKU distribution | 3 | 3 | M-016 | Profile a larger merchant sample before launch | Sample misses edge formats | Open |
| RISK-005 | External tax or carrier sandbox instability may block end-to-end UAT | 3 | 3 | M-002 | Use contract stubs only for isolated tests; rerun provider scenarios | Provider outage | Mitigating |
| RISK-006 | Search relevance may miss target for long-tail apparel queries | 3 | 3 | M-004 | Expand judged query set and tune versioned synonyms | nDCG@10 below 0.82 | Open |
| RISK-007 | Recovery process may exceed pilot RTO if restore is not rehearsed | 2 | 4 | M-013 | Run isolated restore drill and record measured RPO/RTO | Drill misses target | Mitigating |
| RISK-008 | Superseded or test-only content may be mistaken for active policy | 3 | 4 | M-002 | Canonical IDs, status lineage, and isolated fixture namespace | Stale answer citation | Open |
