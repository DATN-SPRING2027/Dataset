---
document_id: "DOC-ORG-PMP-001"
title: "Northstar Commerce Project Management Plan"
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
canonical_document_id: "DOC-ORG-PMP-001"
rendition_paths: ["documents/docx/Project_Management_Plan.docx"]
requirement_ids: []
file_path: "documents/markdown/formal/Project_Management_Plan.md"
format: "markdown"
synthetic: true
---

# Northstar Commerce Project Management Plan

Integrated governance baseline for the Northstar Commerce pilot and its eight Jira workstreams.

## Purpose and governance

The plan governs the fictional Northstar Commerce pilot for Meridian Outfitters with PulsePay Network as an integration partner. The executive sponsor (M-001) owns investment and release decisions; the product manager (M-002) owns scope and requirement baselines; project owners own delivery evidence. The as-of snapshot is 12 October 2026.

## Scope and deliverables

The release scope covers catalog, search, cart/promotions, checkout, payment, inventory, orders/returns, and platform governance. Shared deliverables are listed in the coverage matrix. Customer production migration, machine translation, cross-merchant personalization, and storage of raw payment card data are excluded.

## Work breakdown and schedule

The eight workstreams use 13 consecutive two-week sprints ending 12 October 2026 in the dataset snapshot. Engineering operates on Vietnam time (UTC+07:00) with regular hours 08:00–17:00 (12:00–13:00 lunch break), evening overtime 17:00–22:00 during sprint-end and pre-release crunch, and weekends plus Vietnam public holidays (2026-04-27, 2026-04-30, 2026-05-01, 2026-09-01, 2026-09-02) off for human staff except P0/P1 incident response, while automated CI/SFTP/alert bots run 24/7. Release readiness is planned for 16 October 2026 and the pilot launch target is 23 October 2026, subject to the checkout/payment gate. Platform foundation continues through 4 December 2026.

## Roles and capacity

The product manager maintains the backlog and acceptance wording; engineering owners estimate and deliver; QA owns test design and execution evidence; Security approves restricted-data controls; SRE owns operational readiness; merchant and partner contacts validate their tenant-specific workflows.

## Communication and change control

Daily squad updates are represented as anchored Markdown records. Weekly pilot decisions are recorded with action owner and linked Jira issue. Changes to approved requirements require a change request, impact analysis, product/security approval as applicable, updated RTM, and a new version; no silent baseline edits are allowed.

## Quality and acceptance

A release candidate must pass the approved functional and regression suites, have no unresolved critical security defect, demonstrate tenant isolation, provide rollback evidence, and receive merchant UAT sign-off or an explicitly documented exception.

## Risk and escalation

The risk register is reviewed weekly. A P0/P1 security, payment duplication, or data-loss event is escalated immediately to the sponsor and incident lead; a release-impacting blocker without a recovery owner is raised at the same business day checkpoint.
