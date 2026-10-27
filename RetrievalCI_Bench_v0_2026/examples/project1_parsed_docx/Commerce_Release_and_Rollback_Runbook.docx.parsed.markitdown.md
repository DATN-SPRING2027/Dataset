Commerce Release and Rollback Runbook

*Standard operating procedure for staged rollout, canary verification, and emergency rollback of commerce services.*

|  |  |  |  |
| --- | --- | --- | --- |
| **Document ID** | DOC-REL-RUN-009 | **Project** | NSC-PLAT |
| **Owner** | M-013 | **Version** | 1.2 |
| **Updated** | 2026-10-02 | **Status** | Approved |
| **Classification** | Internal | **Access Groups** | GRP-ALL-STAFF |

# Pre-Deployment Verification Checklist

* Verify all P0/P1 issues for the release milestone are resolved or hold an approved executive exception.
* Verify automated smoke tests across checkout, payment idempotency, and tenant access control on staging.
* Ensure designated on-call SRE and squad leads are present in release bridge.

# Canary Rollout Progression

* Stage 1: Internal synthetic test merchants (0% live customer traffic) for 30 minutes observation.
* Stage 2: Meridian Outfitters pilot tenant at 5% traffic allocation, expanding to 25%, 50%, and 100% over 2 hours.
* Continuously monitor p95 latency, 5xx error rate, and payment pending queue age.

# Rollback Triggers & Execution

* Trigger 1: Checkout 5xx rate exceeds 1.5% over a 5-minute rolling window.
* Trigger 2: Any duplicate payment capture or order creation anomaly detected.
* Trigger 3: Confirmed cross-tenant data disclosure or tenant isolation breach.
* Execution: Toggle feature flag 'ff\_checkout\_v2' to false immediately, then revert deployment container tag.

# Reference Table

|  |  |  |  |
| --- | --- | --- | --- |
| **Metric Name** | **Warning Threshold** | **Critical Rollback Threshold** | **Action** |
| Checkout HTTP 5xx Rate | > 0.5% | > 1.5% for 5 min | Disable feature flag, page SRE |
| Payment Pending Age | > 5 minutes | > 15 minutes | Halt canary, trigger reconciliation |
| Database Deadlock Rate | > 2 / min | > 10 / min | Roll back migration transaction |
| Tenant Isolation Violation | 0 detected | >= 1 confirmed event | Immediate emergency rollback |
