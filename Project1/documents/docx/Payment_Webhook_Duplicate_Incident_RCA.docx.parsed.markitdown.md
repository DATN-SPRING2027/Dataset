Incident RCA: Duplicate Payment Webhook Processing

*Root cause analysis of the staging duplicate payment webhook processing incident on 22 September 2026.*

|  |  |  |  |
| --- | --- | --- | --- |
| **Document ID** | DOC-PAY-RCA-006 | **Project** | NSC-PAY |
| **Owner** | M-013 | **Version** | 1.0 |
| **Updated** | 2026-09-24 | **Status** | Approved |
| **Classification** | Restricted | **Access Groups** | GRP-CHECKOUT, GRP-SECURITY |

# Incident Summary & Blast Radius

* On 22 September 2026 at 09:14 UTC, a network blip caused PulsePay to retransmit event 'EVT-SYN-1001' (payment.succeeded).
* A worker restart occurred between order state transition and event inbox acknowledgement, causing a duplicate fulfillment dispatch in staging.
* Zero customer financial impact; containment was achieved in staging before production rollout.

# Root Cause Investigation

* The payment consumer executed business side effects (order paid event emission) before committing the durable provider event ID.
* The consumer lacked a transactional outbox and unique database constraint across (merchant\_id, provider\_event\_id).

# Remediation Actions

* Implemented database unique constraint on payment\_event\_inbox(merchant\_id, provider\_event\_id).
* Refactored consumer to commit inbox insertion and state change in a single atomic database transaction.
* Added crash simulation tests to the continuous integration pipeline to prevent regressions.

# Reference Table

|  |  |  |  |
| --- | --- | --- | --- |
| **Action Item** | **Owner** | **Target Date** | **Verification Proof** |
| Inbox Unique Constraint | Noah Kim (M-006) | 2026-10-14 | Migration migration\_pay\_inbox\_idx validated |
| Crash Replay Test Suite | Owen Garcia (M-010) | 2026-10-15 | Automated CI test run attached to PAY-002 |
| Reconciliation Dashboard | Amara Okafor (M-013) | 2026-10-30 | Grafana duplicate rejection metric active |
