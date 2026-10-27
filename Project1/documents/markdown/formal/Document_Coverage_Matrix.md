---
document_id: "DOC-ORG-COVERAGE-001"
title: "Project Document Coverage Matrix"
project_id: null
organization_id: "ORG-NSC"
scope: "organization"
owner_id: "M-002"
created_at: "2026-10-12"
updated_at: "2026-10-12"
version: "1.0"
status: "Approved"
classification: "Internal"
access_groups: ["GRP-ALL-STAFF"]
source_issue_keys: ["PLAT-001", "PLAT-004"]
canonical_document_id: "DOC-ORG-COVERAGE-001"
rendition_paths: []
requirement_ids: []
file_path: "documents/markdown/formal/Document_Coverage_Matrix.md"
format: "markdown"
synthetic: true
---

# Project Document Coverage Matrix

Inventory of formal project deliverables, canonical sources, owners, scope, and coverage across the eight workstreams.

## Coverage policy

Present means a maintained source exists and has a defined owner; Partial means a related document exists but omits required project-wide coverage; Missing means no authoritative deliverable exists. Markdown is the canonical editable source for paired Word renditions.

## Organization and platform deliverables

The PMP, BRD, SRS, RDS, SDS, database design, API specification, coding standards, threat model, ADR index, RTM, master test plan, functional test catalog, execution report, UAT plan/report, deployment guide, operations runbook, user manual, release/handover, risk register, and change control form the shared baseline.

## Project coverage

Each of the eight workstreams has a project annex with an accountable owner, access group, scope boundary, requirements, data contracts, dependencies, acceptance measures, and source Jira keys. Existing module-specific PRDs, contracts, SOPs, incident reports, and standards remain linked as detailed supporting documents.

## Version and access controls

A paired DOCX is a presentation rendition and is not a second canonical document. Superseded material remains discoverable for history but must not outrank the current approved source. ACL is enforced on the canonical record and inherited by renditions.

## Formal document inventory

| Canonical ID | Title | Scope | Owner | Status | Classification | Access groups | Format |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DOC-ORG-CHARTER-001 | Northstar Company and Product Charter | ORG-NSC | M-001 | Approved | Internal | GRP-ALL-STAFF | Markdown |
| DOC-CAT-PRD-004 | Catalog and Merchandising Requirements | NSC-CAT | M-002 | Approved | Internal | GRP-CATALOG | Markdown |
| DOC-SRCH-STRATEGY-003 | Search Relevance and Discovery Strategy | NSC-SRCH | M-004 | In Review | Internal | GRP-ALL-STAFF | Markdown |
| DOC-PAY-ADR-001 | ADR-001: Initial Payment Orchestration (SUPERSEDED) | NSC-PAY | M-018 | Superseded | Restricted | GRP-PAYMENT | Markdown |
| DOC-PAY-ADR-003 | ADR-003: Payment Orchestration and Idempotency | NSC-PAY | M-006 | Approved | Restricted | GRP-PAYMENT, GRP-PULSEPAY | Markdown |
| DOC-ORD-POL-005 | Refund and Cancellation Policy | NSC-ORD | M-008 | Approved | Internal | GRP-ALL-STAFF, GRP-MERIDIAN | Markdown |
| DOC-ORG-MEETING-2026-10-09 | Pilot Weekly Decisions and Actions — 9 October | ORG-NSC | M-002 | Approved | Internal | GRP-ALL-STAFF | Markdown |
| DOC-PLAT-MIG-010 | Multi-Tenant Database Migration Plan | NSC-PLAT | M-035 | Approved | Internal | GRP-PLATFORM | Markdown |
| DOC-SRCH-STD-005 | Search Synonym Dictionary Standard | NSC-SRCH | M-021 | Approved | Internal | GRP-ALL-STAFF | Markdown |
| DOC-CHKO-RCA-008 | Incident RCA: Checkout Idempotency Key Conflict | NSC-CHKO | M-026 | Approved | Restricted | GRP-CHECKOUT, GRP-SECURITY | Markdown |
| DOC-INT-MERIDIAN-001 | Merchant Integration Guide: Meridian Outfitters | NSC-CAT | M-015 | Approved | Customer Restricted | GRP-MERIDIAN | Markdown |
| DOC-INT-PULSEPAY-002 | Partner Webhook Specification: PulsePay Network | NSC-PAY | M-017 | Approved | Restricted | GRP-PULSEPAY, GRP-PAYMENT | Markdown |
| DOC-ORG-COVERAGE-001 | Project Document Coverage Matrix | ORG-NSC | M-002 | Approved | Internal | GRP-ALL-STAFF | Markdown |
| DOC-ORG-PMP-001 | Northstar Commerce Project Management Plan | ORG-NSC | M-002 | Approved | Internal | GRP-ALL-STAFF | Markdown + DOCX rendition |
| DOC-ORG-BRD-001 | Northstar Commerce Business Requirements Document | ORG-NSC | M-002 | Approved | Internal | GRP-ALL-STAFF | Markdown + DOCX rendition |
| DOC-ORG-SRS-001 | Northstar Commerce Software Requirements Specification | ORG-NSC | M-002 | Approved | Internal | GRP-ALL-STAFF | Markdown + DOCX rendition |
| DOC-ORG-RDS-001 | Northstar Commerce Requirements and Design Specification | ORG-NSC | M-002 | Approved | Internal | GRP-ALL-STAFF | Markdown + DOCX rendition |
| DOC-ORG-SDS-001 | Northstar Commerce Software Design Specification | ORG-NSC | M-009 | Approved | Internal | GRP-ALL-STAFF | Markdown + DOCX rendition |
| DOC-ORG-DBD-001 | Northstar Commerce Database Design and ERD | ORG-NSC | M-009 | Approved | Internal | GRP-PLATFORM, GRP-SECURITY | Markdown + DOCX rendition |
| DOC-ORG-API-001 | Northstar Commerce API Specification | ORG-NSC | M-009 | Approved | Internal | GRP-ALL-STAFF | Markdown + DOCX rendition |
| DOC-ORG-CODE-001 | Northstar Commerce Coding Standards | ORG-NSC | M-009 | Approved | Internal | GRP-ALL-STAFF | Markdown |
| DOC-ORG-THREAT-001 | Northstar Commerce Threat Model | ORG-NSC | M-012 | Approved | Restricted | GRP-SECURITY, GRP-LEADERS | Markdown |
| DOC-ORG-ADR-INDEX-001 | Architecture Decision Record Index | ORG-NSC | M-009 | Approved | Internal | GRP-ALL-STAFF | Markdown |
| DOC-ORG-RTM-001 | Requirements Traceability Matrix | ORG-NSC | M-010 | Approved | Internal | GRP-ALL-STAFF | Markdown |
| DOC-ORG-TEST-PLAN-001 | Northstar Commerce Master Test Plan | ORG-NSC | M-010 | Approved | Internal | GRP-ALL-STAFF | Markdown + DOCX rendition |
| DOC-ORG-FTCAT-001 | Northstar Commerce Functional Test Catalog | ORG-NSC | M-010 | Approved | Internal | GRP-ALL-STAFF | Markdown |
| DOC-ORG-TEST-REPORT-001 | Northstar Commerce Test Execution Report | ORG-NSC | M-010 | In Review | Internal | GRP-ALL-STAFF | Markdown |
| DOC-ORG-UAT-PLAN-001 | Northstar Commerce User Acceptance Test Plan | ORG-NSC | M-002 | Approved | Customer Restricted | GRP-MERIDIAN, GRP-LEADERS | Markdown |
| DOC-ORG-UAT-REPORT-001 | Northstar Commerce User Acceptance Test Report | ORG-NSC | M-002 | In Review | Customer Restricted | GRP-MERIDIAN, GRP-LEADERS | Markdown |
| DOC-ORG-DEPLOY-001 | Northstar Commerce Deployment Guide | ORG-NSC | M-009 | Approved | Internal | GRP-PLATFORM, GRP-SECURITY | Markdown |
| DOC-ORG-OPS-001 | Northstar Commerce Operations Runbook | ORG-NSC | M-013 | Approved | Internal | GRP-PLATFORM, GRP-SUPPORT | Markdown |
| DOC-ORG-USER-MAN-001 | Northstar Commerce User Manual | ORG-NSC | M-016 | Approved | Internal | GRP-ALL-STAFF | Markdown |
| DOC-ORG-HANDOVER-001 | Release Notes and Operational Handover | ORG-NSC | M-002 | In Review | Internal | GRP-ALL-STAFF | Markdown |
| DOC-ORG-RISK-001 | Northstar Commerce Risk Register | ORG-NSC | M-001 | Approved | Restricted | GRP-LEADERS, GRP-SECURITY | Markdown |
| DOC-ORG-CHANGE-001 | Change Log and Change Control Procedure | ORG-NSC | M-002 | Approved | Internal | GRP-ALL-STAFF | Markdown |
| DOC-CAT-ANNEX-001 | Product Catalog & Merchandising Project Annex | NSC-CAT | M-002 | Approved | Internal | GRP-CATALOG | Markdown |
| DOC-SRCH-ANNEX-001 | Search & Discovery Project Annex | NSC-SRCH | M-002 | Approved | Internal | GRP-SEARCH | Markdown |
| DOC-CART-ANNEX-001 | Cart & Promotions Project Annex | NSC-CART | M-005 | Approved | Internal | GRP-CART | Markdown |
| DOC-CHKO-ANNEX-001 | Checkout Experience Project Annex | NSC-CHKO | M-005 | Approved | Internal | GRP-CHECKOUT | Markdown |
| DOC-PAY-ANNEX-001 | Payment Orchestration Project Annex | NSC-PAY | M-006 | Approved | Internal | GRP-PAYMENT | Markdown |
| DOC-INV-ANNEX-001 | Inventory & Fulfillment Project Annex | NSC-INV | M-007 | Approved | Internal | GRP-INVENTORY | Markdown |
| DOC-ORD-ANNEX-001 | Orders, Returns & Refunds Project Annex | NSC-ORD | M-008 | Approved | Internal | GRP-ORDERS | Markdown |
| DOC-PLAT-ANNEX-001 | Platform Reliability & Governance Project Annex | NSC-PLAT | M-009 | Approved | Internal | GRP-PLATFORM | Markdown |
| DOC-ARCH-PLAT-001 | Commerce Platform Architecture Overview | NSC-PLAT | M-009 | Approved | Internal | GRP-ALL-STAFF | DOCX canonical |
| DOC-CHKO-API-002 | Checkout API Contract | NSC-CHKO | M-005 | Approved | Internal | GRP-CHECKOUT, GRP-MERIDIAN | DOCX canonical |
| DOC-QA-CHECKOUT-017 | Checkout and Order Regression Test Plan | NSC-CHKO | M-010 | In Review | Internal | GRP-CHECKOUT | DOCX canonical |
| DOC-SEC-CLASS-002 | Security Data Classification and Access Standard | NSC-PLAT | M-012 | Approved | Restricted | GRP-SECURITY, GRP-LEADERS | DOCX canonical |
| DOC-PAY-RCA-006 | Incident RCA: Duplicate Payment Webhook Processing | NSC-PAY | M-013 | Approved | Restricted | GRP-CHECKOUT, GRP-SECURITY | DOCX canonical |
| DOC-REL-RUN-009 | Commerce Release and Rollback Runbook | NSC-PLAT | M-013 | Approved | Internal | GRP-ALL-STAFF | DOCX canonical |
| DOC-INV-STD-003 | Inventory Reservation and Safety Stock Standard | NSC-INV | M-007 | Approved | Internal | GRP-ALL-STAFF | DOCX canonical |
| DOC-ORD-SOP-004 | Customer Order Lifecycle and Fulfillment SOP | NSC-ORD | M-008 | Approved | Internal | GRP-ALL-STAFF, GRP-MERIDIAN | DOCX canonical |
| DOC-CART-SPEC-005 | Cart Promotion Rules and Coupon Engine Spec | NSC-CART | M-005 | Approved | Internal | GRP-ALL-STAFF | DOCX canonical |
| DOC-DATA-DICT-008 | Data Pipeline and Analytics Data Dictionary | NSC-PLAT | M-011 | Approved | Internal | GRP-DATA, GRP-ALL-STAFF | DOCX canonical |

## Eight project coverage

| Project | Owner | Access group | Annex | Requirement count |
| --- | --- | --- | --- | --- |
| NSC-CAT | M-002 | GRP-CATALOG | DOC-CAT-ANNEX-001 | 8 |
| NSC-SRCH | M-002 | GRP-SEARCH | DOC-SRCH-ANNEX-001 | 8 |
| NSC-CART | M-005 | GRP-CART | DOC-CART-ANNEX-001 | 8 |
| NSC-CHKO | M-005 | GRP-CHECKOUT | DOC-CHKO-ANNEX-001 | 8 |
| NSC-PAY | M-006 | GRP-PAYMENT | DOC-PAY-ANNEX-001 | 8 |
| NSC-INV | M-007 | GRP-INVENTORY | DOC-INV-ANNEX-001 | 8 |
| NSC-ORD | M-008 | GRP-ORDERS | DOC-ORD-ANNEX-001 | 8 |
| NSC-PLAT | M-009 | GRP-PLATFORM | DOC-PLAT-ANNEX-001 | 8 |
