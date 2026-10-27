# Single-file full ingest speed trace

> Scope correction: the document was ingested in the `sag` dev schema; run metadata was recorded in the benchmark schema. See [scope correction](../ingest-scope-correction-20261027.md).

File: `examples/rag_eval/bench_v0/corpus/fireflies__dsid_9ed01291d81947f49500df5fb28ab724.md` (34,236 bytes).
Real SAG path: upload → parse → dedup/temporal → SearchUnit index → KnowledgeUnit foundation → graph build/persist → active tree.
Dense graph is enabled. Top-K is fixed at 5; no retrieval query or quality metric was run.

## Wall clock

| Segment | Seconds |
|---|---:|
| Benchmark registration | 0.362 |
| SAG app startup + login | 5.343 |
| Fresh Qdrant collection/index setup | 2.242 |
| Upload service | 0.127 |
| Upload start → tree ACTIVE | 33.294 |
| Collection setup start → tree ACTIVE | 35.535 |
| App start → tree ACTIVE | 41.700 |

## Pipeline stages

Stage durations are from SAG `stage_runs`; KnowledgeUnit, graph, persistence, and tree timings are instrumented separately. Stage durations can overlap with background jobs.

| Stage | Count | Total seconds | Mean seconds |
|---|---:|---:|---:|
| receive | 1 | 0.010 | 0.010 |
| PARSE | 1 | 0.016 | 0.016 |
| DEDUP_TEMPORAL | 1 | 2.263 | 2.263 |
| INDEX_SEARCH | 1 | 10.621 | 10.621 |

## Knowledge and graph stages

- KnowledgeUnit Foundation jobs: 1 job(s), 2.539 s total.
- SearchUnit embedding batches: `[{"texts": 285, "vectors": 285, "seconds": 7.016}]`.
- KnowledgeUnit embedding batches: `[{"blocks": 274, "vectors": 274, "seconds": 0.009}]`.
- Graph CPU: 2.822 s, included in graph persistence: 3.280 s.
- Tree rebuild: 15.315 s, including graph persistence; these nested durations must not be added.

Raw per-stage records, graph edge counts, Qdrant statuses, and final state are in `trace.json` and the run manifest.
