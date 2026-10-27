# Single-file full ingest speed trace

> Scope correction: the document was ingested in the `sag` dev schema; run metadata was recorded in the benchmark schema. See [scope correction](../ingest-scope-correction-20261027.md).

File: `examples/rag_eval/bench_v0/corpus/fireflies__dsid_9ed01291d81947f49500df5fb28ab724.md` (34,236 bytes).
Real SAG path: upload → parse → dedup/temporal → SearchUnit index → KnowledgeUnit foundation → graph build/persist → active tree.
Dense graph is enabled. Top-K is fixed at 5; no retrieval query or quality metric was run.

## Wall clock

| Segment | Seconds |
|---|---:|
| Benchmark registration | 0.332 |
| SAG app startup + login | 5.658 |
| Fresh Qdrant collection/index setup | 2.332 |
| Upload service | 0.091 |
| Upload start → tree ACTIVE | 33.176 |
| Collection setup start → tree ACTIVE | 35.508 |
| App start → tree ACTIVE | 42.018 |

## Pipeline stages

Stage durations are from SAG `stage_runs`; KnowledgeUnit, graph, persistence, and tree timings are instrumented separately. Stage durations can overlap with background jobs.

| Stage | Count | Total seconds | Mean seconds |
|---|---:|---:|---:|
| receive | 1 | 0.010 | 0.010 |
| PARSE | 1 | 0.031 | 0.031 |
| DEDUP_TEMPORAL | 1 | 2.326 | 2.326 |
| INDEX_SEARCH | 1 | 11.419 | 11.419 |

## Knowledge and graph stages

- KnowledgeUnit Foundation jobs: 1 job(s), 2.081 s total.
- SearchUnit embedding batches: `[{"texts": 285, "vectors": 285, "seconds": 7.866}]`.
- KnowledgeUnit embedding batches: `[{"blocks": 274, "vectors": 274, "seconds": 0.01}]`.
- Graph CPU: 2.995 s, included in graph persistence: 3.400 s.
- Tree rebuild: 15.768 s, including graph persistence; these nested durations must not be added.

Raw per-stage records, graph edge counts, Qdrant statuses, and final state are in `trace.json` and the run manifest.
