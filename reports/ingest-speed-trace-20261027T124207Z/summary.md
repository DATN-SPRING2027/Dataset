# Single-file full ingest speed trace

> Scope correction: the document was ingested in the `sag` dev schema; run metadata was recorded in the benchmark schema. See [scope correction](../ingest-scope-correction-20261027.md).

File: `examples/rag_eval/bench_v0/corpus/fireflies__dsid_9ed01291d81947f49500df5fb28ab724.md` (34,236 bytes).
Real SAG path: upload → parse → dedup/temporal → SearchUnit index → KnowledgeUnit foundation → graph build/persist → active tree.
Dense graph is enabled. Top-K is fixed at 5; no retrieval query or quality metric was run.

## Wall clock

| Segment | Seconds |
|---|---:|
| Benchmark registration | 0.255 |
| SAG app startup + login | 5.261 |
| Fresh Qdrant collection/index setup | 2.228 |
| Upload service | 0.114 |
| Upload start → tree ACTIVE | 33.261 |
| Collection setup start → tree ACTIVE | 35.488 |
| App start → tree ACTIVE | 41.664 |

## Pipeline stages

Stage durations are from SAG `stage_runs`; KnowledgeUnit, graph, persistence, and tree timings are instrumented separately. Stage durations can overlap with background jobs.

| Stage | Count | Total seconds | Mean seconds |
|---|---:|---:|---:|
| receive | 1 | 0.010 | 0.010 |
| PARSE | 1 | 0.015 | 0.015 |
| DEDUP_TEMPORAL | 1 | 2.440 | 2.440 |
| INDEX_SEARCH | 1 | 10.891 | 10.891 |

## Knowledge and graph stages

- KnowledgeUnit Foundation jobs: 1 job(s), 2.125 s total.
- SearchUnit embedding batches: `[{"texts": 285, "vectors": 285, "seconds": 7.46}]`.
- KnowledgeUnit embedding batches: `[{"blocks": 274, "vectors": 274, "seconds": 0.008}]`.
- Graph CPU: 2.695 s, included in graph persistence: 3.170 s.
- Tree rebuild: 15.311 s, including graph persistence; these nested durations must not be added.

Raw per-stage records, graph edge counts, Qdrant statuses, and final state are in `trace.json` and the run manifest.
