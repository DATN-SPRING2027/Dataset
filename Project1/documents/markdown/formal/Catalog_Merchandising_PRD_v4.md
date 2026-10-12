---
document_id: "DOC-CAT-PRD-004"
title: "Catalog and Merchandising Requirements"
project_id: "NSC-CAT"
organization_id: "ORG-NSC"
scope: "project"
owner_id: "M-002"
created_at: "2026-09-22"
updated_at: "2026-09-22"
version: "4.0"
status: "Approved"
classification: "Internal"
access_groups: ["GRP-CATALOG"]
source_issue_keys: ["CAT-001", "CAT-002", "CAT-004"]
file_path: "documents/markdown/formal/Catalog_Merchandising_PRD_v4.md"
format: "markdown"
synthetic: true
---

# Catalog and Merchandising Requirements

Product requirements for products, variants, bulk catalog imports, price books, and facet taxonomies.

## Problem Statement

Meridian currently manages complex apparel data in external spreadsheets. The pilot requires predictable CSV imports with row-level validation errors prior to records becoming searchable.

## Product Data Model

A parent product contains sellable variants. SKU is strictly unique per merchant. Archived SKUs remain reserved indefinitely for financial and audit traceability.

## Import Pipeline Behavior

CSV uploads require pre-import validation. Mandatory fields: merchant_sku, product_name, currency, category, and price. Invalid rows generate error codes without rejecting valid rows.

## Acceptance Criteria

Enforce unique merchant SKU; validate HTTPS image URLs; store timestamps in UTC; provide downloadable error reports.

## Unresolved & Out of Scope

Automated multi-lingual machine translation of catalog copy is NOT approved for v1. Search synonym dictionaries must not alter catalog source text.
