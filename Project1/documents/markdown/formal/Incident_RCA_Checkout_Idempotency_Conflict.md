---
document_id: "DOC-CHKO-RCA-008"
title: "Incident RCA: Checkout Idempotency Key Conflict"
project_id: "NSC-CHKO"
organization_id: "ORG-NSC"
scope: "project"
owner_id: "M-026"
created_at: "2026-08-27"
updated_at: "2026-08-27"
version: "1.0"
status: "Approved"
classification: "Restricted"
access_groups: ["GRP-CHECKOUT", "GRP-SECURITY"]
source_issue_keys: ["CHKO-012", "CHKO-015"]
file_path: "documents/markdown/formal/Incident_RCA_Checkout_Idempotency_Conflict.md"
format: "markdown"
synthetic: true
---

# Incident RCA: Checkout Idempotency Key Conflict

Analysis of transient HTTP 409 idempotency conflict errors during Meridian pilot simulated checkout stress tests.

## Incident Description

Automated stress testing triggered false-positive HTTP 409 errors due to floating point rounding discrepancies in total cart tax computations.

## Resolution & Invariant

Standardized all tax calculations to integer minor currency units prior to hashing payload for idempotency verification.
