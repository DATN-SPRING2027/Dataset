---
document_id: "DOC-SRCH-STD-005"
title: "Search Synonym Dictionary Standard"
project_id: "NSC-SRCH"
organization_id: "ORG-NSC"
scope: "project"
owner_id: "M-021"
created_at: "2026-07-19"
updated_at: "2026-07-19"
version: "2.0"
status: "Approved"
classification: "Internal"
access_groups: ["GRP-ALL-STAFF"]
source_issue_keys: ["SRCH-002", "SRCH-005"]
file_path: "documents/markdown/formal/Search_Synonym_Dictionary_Standard_v2.md"
format: "markdown"
synthetic: true
---

# Search Synonym Dictionary Standard

Formatting rules, expansion syntax, and validation criteria for merchant synonym dictionary definitions.

## Synonym Syntax Standards

Synonyms are specified as one-way mappings ('coat => jacket, outerwear') or bidirectional equivalences ('trousers, pants').

## Tenant Isolation Constraint

Synonyms configured for Meridian Outfitters must not expand queries for any other merchant tenant on the shared cluster.
