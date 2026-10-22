Inventory Reservation and Safety Stock Standard

*Operational standard for real-time inventory reservations, concurrency locks, and safety stock thresholds.*

|  |  |  |  |
| --- | --- | --- | --- |
| **Document ID** | DOC-INV-STD-003 | **Project** | NSC-INV |
| **Owner** | M-007 | **Version** | 1.1 |
| **Updated** | 2026-07-14 | **Status** | Approved |
| **Classification** | Internal | **Access Groups** | GRP-ALL-STAFF |

# Stock Hold Mechanics

* Inventory reservation is initiated at the checkout payment step with a strict 15-minute time-to-live (TTL).
* If the checkout session expires or payment fails, an automated queue worker releases the reservation back to available stock.
* Reservations utilize Redis atomic locks combined with PostgreSQL SELECT ... FOR UPDATE to prevent race conditions.

# Safety Stock Rules

* Merchants can configure minimum safety buffers per SKU category to protect against warehouse inventory discrepancies.
* Available to promise (ATP) is calculated as: ATP = Physical On-Hand - Allocated Reserves - Safety Buffer.

# Reference Table

|  |  |  |  |
| --- | --- | --- | --- |
| **Category** | **Default Safety Stock** | **Reservation TTL** | **Oversell Action** |
| High Velocity Apparel | 5 units | 15 minutes | Hard reject at checkout |
| Standard Catalog Items | 2 units | 15 minutes | Hard reject at checkout |
| Backorder Eligible | 0 units | 30 minutes | Accept with delayed shipping notice |
