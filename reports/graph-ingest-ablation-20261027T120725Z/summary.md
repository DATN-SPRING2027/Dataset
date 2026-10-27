# 8-file ingest: dense graph on/off

> Scope correction: documents were ingested into fresh projects in the `sag` dev schema; run metadata was recorded in the benchmark schema. See [scope correction](../ingest-scope-correction-20261027.md).

This is a paired, fresh-project comparison. Dense SearchUnit embeddings and KnowledgeUnit embeddings are generated in both runs; the off condition removes dense vectors only from the graph-builder payload. Top-K is fixed at 5 but no search query is issued.

| Condition | Qdrant setup (s) | Upload (s) | Processing to tree ready (s) | Total incl. setup (s) | Knowledge Units | Graph builds |
|---|---:|---:|---:|---:|---:|---:|
| dense_on | 2.344 | 0.408 | 78.608 | 81.371 | 581 | 1 |
| dense_off | 3.280 | 0.311 | 69.437 | 73.044 | 581 | 1 |

Dense-off finished **8.327 s (10.2%) faster** in this single pair. The graph itself still builds in both conditions; dense-off removes only dense signals from graph construction. Dense embeddings for SearchUnits and KnowledgeUnits remain enabled in both.

## Graph work

| Condition | Graph edges | Semantic edges | Graph CPU (s) | Graph persistence (s) | Tree rebuild (s) |
|---|---:|---:|---:|---:|---:|
| dense_on | 5,619 | 5,619 | 4.658 | 6.056 | 40.493 |
| dense_off | 4,478 | 0 | 1.759 | 2.856 | 36.857 |

Dense-off saved **2.899 s** in graph CPU and **3.200 s** in graph persistence. CPU is inside persistence, so these savings must not be added. The tree rebuild, which also includes persistence, was **3.636 s** shorter.

## Ingestion stages

| Condition | DEDUP_TEMPORAL total (s) | INDEX_SEARCH total (s) |
|---|---:|---:|
| dense_on | 32.432 | 36.331 |
| dense_off | 13.922 | 42.574 |

These are summed stage durations across eight documents; stages can overlap because documents process concurrently, so they do not add up to wall time. The large upstream stage variation is a reason to treat the end-to-end difference as an initial probe, not a stable speedup estimate.

Graph CPU timings include child-process spawn/IPC; graph persistence timings include database writes. Per-build timings, foundation-job timings, Qdrant cleanup status codes and per-document ingestion timings are in `comparison.json` and each condition's `run_manifest.json`.

## Scope

Eight corpus files are selected deterministically across file-size ranks. Each condition gets a new project/source/collection. Both graphs keep lexical/entity/structure links. Each Qdrant collection and its payload indexes are prepared with the production helper, and that setup time is included in the total. Top-K is recorded as 5; no retrieval quality query was run.
