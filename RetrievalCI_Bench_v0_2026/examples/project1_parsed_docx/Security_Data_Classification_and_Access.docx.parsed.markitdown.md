Security Data Classification and Access Standard

*Enterprise data classification tiers, role-based access rules, and search index filtering standards.*

|  |  |  |  |
| --- | --- | --- | --- |
| **Document ID** | DOC-SEC-CLASS-002 | **Project** | NSC-PLAT |
| **Owner** | M-012 | **Version** | 2.1 |
| **Updated** | 2026-09-05 | **Status** | Approved |
| **Classification** | Restricted | **Access Groups** | GRP-SECURITY, GRP-LEADERS |

# Data Classification Levels

* Level 1 - Public: Approved public marketing documentation, catalog specs, and public API reference.
* Level 2 - Internal: Standard operational documentation, sprint plans, and internal engineering designs (accessible to GRP-ALL-STAFF).
* Level 3 - Restricted: Security assessments, incident root-cause analyses, payment architecture, and vulnerability reports.
* Level 4 - Customer Restricted: Merchant export datasets and tenant configuration accessible strictly to authorized merchant personnel.

# Search & Vector Retrieval ACL Invariants

* Access control lists (ACL) must be evaluated as a pre-filter before vector distance calculation and snippet extraction.
* Under no circumstances may a search response expose document titles, summaries, or metadata for records the principal cannot access.
* Documents with missing or unparseable ACL metadata must be quarantined immediately and excluded from query indexes.

# Offboarding & Revocation Lifecycle

* When a team member transitions to inactive status, all group memberships and active authentication tokens are revoked instantly.
* Historical contributions (authorship, Jira changelogs) remain preserved for audit integrity, but current data access is denied.

# Reference Table

|  |  |  |  |
| --- | --- | --- | --- |
| **Data Category** | **Classification Tier** | **Authorized Access Groups** | **Quarantine on Missing ACL** |
| Product Requirements | Internal | GRP-ALL-STAFF, Project Squad | Yes |
| Security Audits & RCAs | Restricted | GRP-SECURITY, GRP-LEADERS | Yes |
| Payment Gateway Credentials | Restricted | GRP-CHECKOUT, GRP-SECURITY | Yes |
| Merchant Private Exports | Customer Restricted | GRP-MERIDIAN, GRP-SUPPORT | Yes |
