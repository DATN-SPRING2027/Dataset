# Workflow fixes — 27/10/2026

Implementation is in the working tree; no commit or push performed. Full benchmark
verification is in progress. This document must not be read as a completed quality
or latency comparison until the final run manifests say COMPLETED.

## Implemented

- Canonical document ingestion ends after verified SearchUnit indexing. Legacy
  Event/Entity extraction remains opt-in. One durable FOUNDATION producer builds
  E0/E1 and dense KU data per version; it no longer rebuilds a whole project.
- FOUNDATION/E2 success durably requests a project tree rebuild, with recovery
  of missing delivery receipts. Concurrent changes retain a queued follow-up.
  Active ingestion/FOUNDATION dependencies defer without spending a failure attempt.
- Spawned, cancellable CPU work covers graph, routing, MinHash and dedup ranking.
  Admission/deadline and child termination are bounded. CPU children receive
  data only; DB/provider clients stay in the API process.
- Prepared dense arithmetic, cached LSH signs and routing vector norms retain
  existing outputs. Graph fingerprints avoid duplicate computations; evidence
  checksums are fetched in SQL batches. Published trees pin one graph build.
- MinHash derivatives are cached with content/signature checksums, without
  limiting the prior-document comparison set. Dynamic Top-K MMR no longer
  recomputes the same pair at each selection round.
- Transient indexing errors preserve retryability through domain wrappers.
  FOUNDATION has a provider-derived timeout separate from E2; at the current
  120-second embedding timeout/three retries, the envelope is 633.5 seconds.
  CPU work has a separate 300-second deadline including admission.
- Document/source deletion persists project invalidation in the same transaction.
  Empty projects clear the active pointer. Snapshot inputs are revalidated before
  publishing under the input lock shared by FOUNDATION and E2.
- Dataset HTTP measurement runs in a separate process, with frontend first-result
  and idle deadlines (30/45 seconds). No auth dependency is replaced. Run manifests
  retain source hashes including untracked API modules and DB scope identifiers.

## Evidence so far

- Backend: **87 passed, 1 skipped**, `fix-tests-final.log`.
- Dataset runner: **18 passed**, `runner-tests-final.log` (independent HTTP timeout,
  mapped-column/project filtering and exhausted-tree readiness regressions included).
- Graph: **677 dense KUs / 7,869 edges**, entire payload and checksum equal;
  24.6779 s -> 5.0461 s in the isolated math check, `fixed_graph_parity.json`.
- Intermediate diagnostic run `20261027T062831Z-8a3a2f` reached 81/81 READY and
  81 FOUNDATION SUCCEEDED on attempt 1. Its graph-stage health probe had 90 requests,
  zero errors, max 118 ms. It also exposed uncached synchronous MinHash and a
  premature tree rebuild. These are fixed in the subsequent code.
- That diagnostic run is explicitly **ABORTED / SupersededDiagnostic**. Its
  documents, Qdrant collection, partial QA checkpoints and DB records are retained.
  It is not the final benchmark.
- A subsequent runner diagnostic failed on its new tree-job SQL probe (ORM `payload`
  maps to SQL `payload_json`). The probe now uses the mapped ORM column. That FAILED
  run is retained rather than rewritten as successful.
- `fixed_math_parity.json`: dedup outcomes match the captured old stage, routing
  manifests match exactly, and all three MMR test outputs/order/stats match.
  The 100-evidence automatic MMR example took 31.2684 s before / 1.9875 s after;
  the Top-5 example did not improve (1.0825 s / 1.1110 s). These are isolated
  computation examples, not end-to-end product latency claims.

## Final runs

- Retained diagnostic RetrievalCI: `20261027T071001Z-15e97d`, schema
  `sag_bench_retrievalci_20261027070959`, project `25ea0fd0b8be4081b6ffe9f4`.
  Status: **ABORTED**, full fresh ingestion with MinHash/MMR and dependency deferral.
  Log: `retrievalci-final-live-2.log`; output: `../retrievalci-fixed-20261027070959/result`.
  81/81 READY, 3,585 dense KUs, 81 FOUNDATION SUCCEEDED at attempt 1, tree ACTIVE.
  One stale build was rejected and retried before activation. The run exposed
  the SEARCH_READY-before-discovery gap, slow manifest decoding/preparation and
  the background query-demand 100 ms budget. The final working tree fixes these;
  this API process retains its startup modules. Its manifest hashes identify the
  measured revision; VN-MTEB will start with the final revision. Retrieval scoring
  math remains identical by differential checks.
- The diagnostic HTTP runner also reset idle only on data events, whereas the
  web client resets idle on received bytes/ping comments after the first result.
  One reported timeout therefore used a stricter protocol than the UI. The runner
  is corrected and regression-tested for both phases: pings do not extend first
  result, but do extend post-result idle. The diagnostic run is retained as ABORTED.
- Retained protocol-correct diagnostic RetrievalCI: `20261027T074440Z-b7357e`, same schema/project and verified
  corpus/index, a new run ID/output and fresh API process using the final code.
  Status **ABORTED**. Output `../retrievalci-fixed-20261027074439/result`, log
  `retrievalci-final-protocol.log`. `ingestion_reused=true` is recorded explicitly;
  this is not presented as a new ingestion timing measurement.
- Retained INFO-logging diagnostic RetrievalCI: `20261027T080912Z-871da9`, using the same verified corpus and
  new API process with cooperative diversity selection, authorization recheck,
  and the corrected client timeout. `ingestion_reused_from_run_id` and manifest
  SHA-256 are retained. Status **ABORTED**. Output
  `../retrievalci-fixed-20261027080911/result`, log `retrievalci-final-cooperative.log`.
- Current RetrievalCI: `20261027T081142Z-984c8a`, using the same verified
  corpus and API code, with the configured SAG debug setting (`debug_logging=true`).
  SSE payload debug logging is suppressed to avoid writing evidence to log.
  Status **COMPLETED**. Output `../retrievalci-fixed-20261027081141/result`,
  log `retrievalci-default-config.log`. Its ingestion source is recorded as
  `20261027T071001Z-15e97d`; corpus identity and hashes are checked on reuse.
- A paired Top-5/auto probe is running against this verified index. VN-MTEB is
  queued after the probe to avoid sharing provider load during latency measurement.

E2 is disabled by the current application configuration; selecting E2-eligible
units does not mean an E2 LLM job ran. Report E0/E1/E2 evidence counts separately.
Historical hosted baselines are retained comparisons, not same-hardware latency
experiments. Windows packaged/PyInstaller execution has not been tested.

## Remaining measurement conditions

- The provider reported `TPM limit reached` (RateLimitError, configured SDK retry
  count 2) during the retained diagnostic. Do not label evidence fallback as a
  successful model generation, or silently remove these answers from quality
  evaluation. Final metrics include the product's actual fallback behavior.
- The final run's sampled long generation had the API main thread idle in the
  Windows event loop (`final-qa-wait-stack.txt`), distinct from the former MinHash
  CPU stall. Full-answer latency still includes upstream generation/retries.
- SAG buffers provider text until citation syntax is checked. `first_token_ms`
  measures the first public validated summary delta, not raw upstream TTFT.
- The diagnostic ingestion health probe had zero errors over 353 requests,
  p50 2.66 ms / p95 117.83 ms / max 564.35 ms. The graph/publish interval had
  zero errors over 144 requests but max 1,794.46 ms. These earlier probes exposed
  manifest preparation/decoding work; they do not satisfy the proposed strict
  p95 <100 ms / max <500 ms goal and must not be presented as passing it.
- Final manifest preparation/checksumming is now offloaded; validated manifest
  decoding uses the installed fast decoder, without changing canonical encoding.
  VN-MTEB's fresh pipeline is the next full verification of this final revision.
- During the earlier QA probe, 1 of 144 health checks timed out and max was
  3,013 ms. Selection was synchronous even after its pair-comparison optimization.
  Selection now runs off-loop with bounded admission, request-deadline cancellation,
  and scope/version revalidation before response. A single long Python/native step
  cannot be forcibly interrupted; graph/routing still use the killable CPU process.
  A probe is running with the current API revision; as of the first 273 requests
  it had 0 errors and p95 79.64 ms, but max 1,414.15 ms. The max criterion is
  therefore not yet satisfied.
- Current API QA health probe completed: 1,173 samples, zero errors, p50
  3.62 ms, p95 62.19 ms, maximum 1,414.15 ms. The p95 criterion was met on
  this probe; the maximum remained above the requested 500 ms test target.
