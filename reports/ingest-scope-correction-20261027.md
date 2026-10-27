# Ingest probe database scope correction

The `graph_ingest_ablation_probe.py` and `ingest_speed_trace.py` harnesses imported the SAG database engine before assigning the intended benchmark `search_path`. Consequently, the benchmark run registry and its `schema` manifest field used `sag_bench_retrievalci_20261027070959`, while SAG document processing actually used the default `sag` schema in the dev environment. The timings remain measurements of those real SAG runs, but the earlier description of their database isolation was incorrect.

Read-only checks found 60 documents in 11 fresh probe projects in the `sag` schema across the four single-file traces and the graph ablation attempts; the first failed graph attempt has no document there. The corresponding completed projects had no documents in the benchmark schema. The run manifests identify the project IDs. No probe data has been deleted.

An earlier interrupted run also started recovery of existing queued document jobs in `sag` before it was stopped. The precise effects on those pre-existing jobs have not been reconstructed. Later probe runs skipped persisted document-queue recovery and scoped KnowledgeWorker ORM operations to the active fresh project.

Both harnesses now set the database URL before importing the SAG database engine and check `current_schema()` against the intended benchmark schema. A read-only connection check confirmed the corrected import order selects the benchmark schema. Historical manifest `schema` fields remain the registry schema; consult this correction for the actual historical document location.
