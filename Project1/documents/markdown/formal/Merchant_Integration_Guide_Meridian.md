---
document_id: "DOC-INT-MERIDIAN-001"
title: "Merchant Integration Guide: Meridian Outfitters"
project_id: "NSC-CAT"
organization_id: "ORG-NSC"
scope: "project"
owner_id: "M-015"
created_at: "2026-05-18"
updated_at: "2026-05-18"
version: "1.5"
status: "Approved"
classification: "Customer Restricted"
access_groups: ["GRP-MERIDIAN"]
source_issue_keys: ["CAT-008"]
canonical_document_id: "DOC-INT-MERIDIAN-001"
rendition_paths: []
requirement_ids: []
file_path: "documents/markdown/formal/Merchant_Integration_Guide_Meridian.md"
format: "markdown"
synthetic: true
---

# Merchant Integration Guide: Meridian Outfitters

Tailored integration specification for Meridian Outfitters ERP catalog feed and inventory synchronization.

## Catalog Synchronization Protocol

Meridian exports nightly CSV catalog snapshots to designated SFTP endpoint. The automated batch worker ingests records at 02:00 UTC. Canonical issue tracking corresponds to CAT-008 (Meridian partner feed reference INT-001).

## Authentication Credentials

Meridian API clients utilize OAuth2 client credentials scoped exclusively to tenant identifier 'MERIDIAN-01'.
