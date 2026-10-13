---
document_id: "DOC-ORG-CODE-001"
title: "Northstar Commerce Coding Standards"
project_id: null
organization_id: "ORG-NSC"
scope: "organization"
owner_id: "M-009"
created_at: "2026-10-12"
updated_at: "2026-10-12"
version: "1.0"
status: "Approved"
classification: "Internal"
access_groups: ["GRP-ALL-STAFF"]
source_issue_keys: ["PLAT-004", "PLAT-007"]
canonical_document_id: "DOC-ORG-CODE-001"
rendition_paths: []
requirement_ids: []
file_path: "documents/markdown/formal/Coding_Standards.md"
format: "markdown"
synthetic: true
---

# Northstar Commerce Coding Standards

Shared implementation, review, test, security, observability, and dependency standards for Laravel/PHP and Vue.js workstreams.

## Language and structure

Backend code follows the repository's formatter and static-analysis configuration, uses explicit types for public contracts, and keeps controller transport logic separate from domain rules. Vue components use typed props, predictable state ownership, accessible labels, and small composable units. Naming follows the owning module vocabulary.

## Validation and errors

Validate at trust boundaries and again at domain invariants where needed. Return stable error codes and avoid leaking foreign-tenant resource existence. Never swallow exceptions; map known failures to documented errors and preserve correlation IDs.

## Data, tenancy, and transactions

Every tenant-owned query includes tenant scope. Mutations use transactions for coupled state changes and rely on unique constraints for race safety. Do not log access tokens, credentials, PAN/CVV, or unmasked customer contact details.

## Testing and review

Each change includes requirement-linked unit or integration evidence, negative/permission tests, and regression coverage. Reviews check correctness, security, compatibility, operational visibility, and documentation updates. Flaky tests are fixed at their cause rather than retried indefinitely.

## Dependency and supply chain

Prefer established dependencies already in the approved lockfile. New dependencies require owner, maintenance, license, vulnerability, and size review. Pin and audit production dependencies; do not copy proprietary code from reference projects.

## Accessibility and frontend quality

Interactive flows support keyboard operation, visible focus, semantic form labels, meaningful errors, and contrast meeting the project accessibility target. Loading, empty, error, and success states are explicit and testable.
