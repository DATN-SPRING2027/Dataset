Data Pipeline and Analytics Data Dictionary

*Comprehensive schema definitions and metrics formulas for the merchant business intelligence and analytics pipelines.*

|  |  |  |  |
| --- | --- | --- | --- |
| **Document ID** | DOC-DATA-DICT-008 | **Project** | NSC-PLAT |
| **Owner** | M-011 | **Version** | 1.0 |
| **Updated** | 2026-07-29 | **Status** | Approved |
| **Classification** | Internal | **Access Groups** | GRP-DATA, GRP-ALL-STAFF |

# Core Metrics Formulas

* Gross Merchandise Value (GMV): Sum of all captured order totals excluding refunded or voided transactions.
* Checkout Conversion Rate: Total Completed Orders divided by Total Checkout Sessions Created in the observation window.
* Average Order Value (AOV): Total GMV divided by Total Completed Order Count.

# Data Privacy & Anonymization

* All customer personal data (names, physical addresses, emails) are masked using cryptographic salt hashes in analytics views.
* Merchant queries are strictly scoped by tenant identifier in analytics views.

# Reference Table

|  |  |  |  |
| --- | --- | --- | --- |
| **Table Name** | **Grain** | **Key Fields** | **Retention Period** |
| fact\_orders | One row per order | order\_id, merchant\_id, gmv\_cents, status | 7 years (regulatory) |
| fact\_checkout\_funnel | One row per session step | session\_id, merchant\_id, step\_name, drop\_off | 90 days |
| dim\_merchants | One row per merchant | merchant\_id, name, tier, onboarded\_date | Indefinite |
| fact\_payment\_events | One row per gateway event | event\_id, provider\_ref, amount, success | 3 years |
