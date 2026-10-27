"""Paired 8-file ingest probe; only dense signals sent to KnowledgeGraphBuild differ."""
from __future__ import annotations

import argparse
import asyncio
import contextvars
import hashlib
import json
import os
import statistics
import sys
import time
from contextlib import redirect_stdout
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BENCH = ROOT / "RetrievalCI_Bench_v0_2026"
SAG = ROOT.parent / "sag-laya-integration" / "SAG"
CORPUS = BENCH / "examples/rag_eval/bench_v0/corpus"
QUESTIONS = BENCH / "examples/rag_eval/bench_v0/questions.jsonl"


def select_files() -> list[Path]:
    ordered = sorted(CORPUS.glob("*.md"), key=lambda path: (path.stat().st_size, path.name))
    if len(ordered) < 8:
        raise ValueError("The RetrievalCI corpus must contain at least eight Markdown files")
    return [ordered[round(i * (len(ordered) - 1) / 7)] for i in range(8)]


def corpus_hash(files: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in files:
        digest.update(path.relative_to(BENCH).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def install_instrumentation(samples: dict, active: dict):
    import httpx

    from sag_api.jobs import knowledge
    from sag_api.jobs.knowledge import KnowledgeWorker
    from sag_api.jobs.inproc import InProcessAsyncQueue
    from sag_api.services import cpu_worker, document_service, knowledge_candidate_service
    from sag_api.services import search_index_service, universe_tree_service
    from sag_api.db.models import Document, DocumentVersion, KnowledgeJob
    from sqlalchemy import event, select
    from sqlalchemy.orm import Session, with_loader_criteria

    job_context = contextvars.ContextVar("graph_ingest_job", default=None)
    original = {
        "claim_job": knowledge.claim_job,
        "run_one": KnowledgeWorker.run_one,
        "upload": document_service.handle_document_upload,
        "cpu": cpu_worker.run_cpu,
        "post": httpx.AsyncClient.post,
        "persist_graph": knowledge_candidate_service.persist_graph,
        "tree": universe_tree_service.rebuild_project_universe_tree,
        "recover": InProcessAsyncQueue._recover,
    }

    async def skip_persisted_recovery(queue):
        # This probe creates and enqueues its own jobs after startup; leave the shared backlog untouched.
        return None

    def scope_orm_queries(state):
        if not state.is_orm_statement:
            return
        projects = tuple(active.get("project_ids", ()))
        if not projects:
            return
        project_documents = select(Document.id).where(Document.project_id.in_(projects))
        project_versions = select(DocumentVersion.id).where(
            DocumentVersion.document_id.in_(project_documents)
        )
        state.statement = state.statement.options(
            with_loader_criteria(
                Document, Document.project_id.in_(projects), include_aliases=True
            ),
            with_loader_criteria(
                DocumentVersion,
                DocumentVersion.document_id.in_(project_documents),
                include_aliases=True,
            ),
            with_loader_criteria(
                KnowledgeJob,
                KnowledgeJob.document_version_id.in_(project_versions),
                include_aliases=True,
            ),
        )

    event.listen(Session, "do_orm_execute", scope_orm_queries)

    async def claim_job(*args, **kwargs):
        job = await original["claim_job"](*args, **kwargs)
        if job is not None:
            job_context.set({"id": job.id, "kind": job.kind,
                             "version_id": job.document_version_id, "started": time.perf_counter()})
        return job

    async def run_one(worker):
        token = job_context.set(None)
        try:
            result = await original["run_one"](worker)
            job = job_context.get()
            if job is not None:
                samples[active["mode"]]["knowledge_jobs"].append({
                    "job_id": job["id"], "kind": job["kind"],
                    "document_version_id": job["version_id"],
                    "seconds": round(time.perf_counter() - job["started"], 3),
                })
            return result
        finally:
            job_context.reset(token)

    async def upload(*args, **kwargs):
        started = time.perf_counter()
        result = await original["upload"](*args, **kwargs)
        samples[active["mode"]]["uploads"].append({
            "filename": kwargs.get("original_filename"),
            "bytes": len(kwargs.get("file_bytes", b"")),
            "seconds": round(time.perf_counter() - started, 3),
        })
        return result

    async def post(client, url, *args, **kwargs):
        try:
            response = await original["post"](client, url, *args, **kwargs)
        except Exception as error:
            if "points/delete" in str(url):
                samples[active["mode"]]["qdrant_cleanup"].append({"exception": type(error).__name__})
            raise
        if "points/delete" in str(url):
            cleanup = {"status": response.status_code}
            if response.status_code >= 400 and response.status_code != 404:
                cleanup["detail"] = response.text[:1000]
            samples[active["mode"]]["qdrant_cleanup"].append(cleanup)
        return response

    async def run_cpu(operation, payload):
        if operation != "graph":
            return await original["cpu"](operation, payload)
        effective = payload
        if active["mode"] == "dense_off":
            effective = {
                **payload,
                "units": [
                    {**unit, "features_json": {**unit["features_json"], "dense": []}}
                    for unit in payload["units"]
                ],
            }
        started = time.perf_counter()
        result = await original["cpu"](operation, effective)
        semantic_scores = sum(edge["signals"].get("semantic") is not None for edge in result["edges"])
        if active["mode"] == "dense_off" and semantic_scores:
            raise AssertionError("Dense semantic signals remained in the graph-off build")
        samples[active["mode"]]["graph_cpu"].append({
            "units": len(payload["units"]), "edges": len(result["edges"]),
            "semantic_edges": semantic_scores,
            "seconds": round(time.perf_counter() - started, 3),
        })
        return result

    async def persist_graph(session, units, config=None):
        started = time.perf_counter()
        if config is None:
            result = await original["persist_graph"](session, units)
        else:
            result = await original["persist_graph"](session, units, config)
        samples[active["mode"]]["graph_persistence"].append({
            "units": len(units), "edges": len(result.manifest_json["edges"]),
            "seconds": round(time.perf_counter() - started, 3),
        })
        return result

    async def rebuild_tree(*args, **kwargs):
        started = time.perf_counter()
        result = await original["tree"](*args, **kwargs)
        samples[active["mode"]]["tree_rebuilds"].append({
            "project_id": kwargs.get("project_id"),
            "seconds": round(time.perf_counter() - started, 3),
        })
        return result

    knowledge.claim_job = claim_job
    KnowledgeWorker.run_one = run_one
    document_service.handle_document_upload = upload
    cpu_worker.run_cpu = run_cpu
    httpx.AsyncClient.post = post
    knowledge_candidate_service.persist_graph = persist_graph
    universe_tree_service.rebuild_project_universe_tree = rebuild_tree
    InProcessAsyncQueue._recover = skip_persisted_recovery
    original["scope_listener"] = scope_orm_queries
    return original


def restore_instrumentation(original):
    from sag_api.jobs import knowledge
    from sag_api.jobs.knowledge import KnowledgeWorker
    from sag_api.jobs.inproc import InProcessAsyncQueue
    from sag_api.services import cpu_worker, document_service, knowledge_candidate_service
    from sag_api.services import universe_tree_service
    from sqlalchemy import event
    from sqlalchemy.orm import Session
    import httpx

    knowledge.claim_job = original["claim_job"]
    KnowledgeWorker.run_one = original["run_one"]
    document_service.handle_document_upload = original["upload"]
    cpu_worker.run_cpu = original["cpu"]
    httpx.AsyncClient.post = original["post"]
    knowledge_candidate_service.persist_graph = original["persist_graph"]
    universe_tree_service.rebuild_project_universe_tree = original["tree"]
    InProcessAsyncQueue._recover = original["recover"]
    event.remove(Session, "do_orm_execute", original["scope_listener"])


async def main(identity_manifest: Path) -> None:
    identity = json.loads(identity_manifest.read_text(encoding="utf-8"))
    if identity.get("benchmark") != "retrievalci_v0" or not identity.get("user_id") or not identity.get("organization_id"):
        raise ValueError("Pass a completed RetrievalCI manifest with an active benchmark owner")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_root = ROOT / "reports" / f"graph-ingest-ablation-{stamp}"
    output_root.mkdir(parents=True)
    for key in ("PROJECT_ID", "SOURCE_ID", "SOURCE_CONFIG_ID", "RUN_ID", "REUSE_RUN_ID"):
        os.environ.pop(f"SAG_BENCHMARK_{key}", None)
    os.environ.update({
        "SAG_BENCHMARK_USER_ID": identity["user_id"],
        "SAG_BENCHMARK_ORGANIZATION_ID": identity["organization_id"],
        "SAG_BENCHMARK_SCHEMA": identity["schema"],
        "PYTHONUTF8": "1",
    })
    sys.path[:0] = [str(SAG / "apps/api"), str(ROOT), str(BENCH)]
    os.chdir(SAG)

    from sqlalchemy.engine import make_url
    from benchmark_support import BenchmarkRun
    from sag_api.core.config import settings

    url = make_url(settings.database_url)
    settings.database_url = url.set(query={**url.query, "search_path": identity["schema"]}).render_as_string(hide_password=False)

    from sag_api.core.db import SessionLocal
    from sag_api.services import search_index_service
    from sag_benchmark_runtime import SAGBenchmark
    from sqlalchemy import text

    files = select_files()
    expected_hash = corpus_hash(files)
    async with SessionLocal() as session:
        runtime_schema = await session.scalar(text("SELECT current_schema()"))
    if runtime_schema != identity["schema"]:
        raise RuntimeError("SAG runtime database schema does not match benchmark schema")

    conditions = {mode: {"uploads": [], "knowledge_jobs": [], "graph_cpu": [],
                         "graph_persistence": [], "tree_rebuilds": [], "qdrant_cleanup": []}
                  for mode in ("dense_on", "dense_off")}
    active = {"mode": "dense_on"}
    original = install_instrumentation(conditions, active)
    runs = []

    async def start_run(mode):
        active["mode"] = mode
        run_dir = output_root / mode / "result"
        os.environ["SAG_BENCHMARK_OUTPUT_DIR"] = str(run_dir)
        for key, value in {
            "DATA_DIR": str(output_root / mode / "engine"),
            "UPLOAD_DIR": str(output_root / mode / "uploads"),
            "DSH_CONNECTION_FILE": str(output_root / mode / "private-connection.json"),
        }.items():
            setattr(settings, key.lower(), value)
        run_dir.parent.mkdir(parents=True, exist_ok=True)
        run = BenchmarkRun("retrievalci_v0", BENCH, settings.database_url)
        runs.append(run)
        with redirect_stdout(StringIO()):
            await run.start(files, QUESTIONS, {
                "mode": "paired_8_file_graph_ingest_ablation",
                "dense_graph": mode == "dense_on",
                "top_k": 5,
            })
        active["project_ids"] = [run.project_id]
        run.manifest["probe_protocol"] = {
            "files": [{"path": path.relative_to(BENCH).as_posix(), "bytes": path.stat().st_size} for path in files],
            "corpus_sha256": expected_hash,
            "condition": mode,
            "dense_graph_only": True,
            "search_unit_dense": "unchanged",
            "knowledge_unit_dense_embeddings": "computed and stored in both conditions; omitted only from dense_off graph-builder payload",
            "top_k": "fixed at 5; no search queries issued during ingest probe",
            "order": "dense_on then dense_off; shared app runtime; local embedding cache cleared before each condition",
            "queue_isolation": "skip recovery of pre-existing document jobs and scope ORM reads/writes to this condition's fresh project; old backlog rows remain untouched",
            "runtime_schema": runtime_schema,
            "qdrant_setup": "initialize the fresh collection and payload indexes with the production helper before document upload; dimension is read from the existing benchmark collection; setup time is included in total elapsed time",
        }
        run._write_manifest()
        return run

    async def read_pipeline_stages(run):
        async with SessionLocal() as session:
            rows = (await session.execute(text("""
                SELECT i.id AS ingestion_run_id, i.document_version_id, i.status AS ingestion_status,
                       s.stage, s.status AS stage_status, s.duration_ms
                FROM ingestion_runs i LEFT JOIN stage_runs s ON s.run_id=i.id
                WHERE i.project_id=:project AND i.tenant_id=:tenant
                ORDER BY i.created_at, s.created_at
            """), {"project": run.project_id, "tenant": run.organization_id})).mappings().all()
        details = [dict(row) for row in rows]
        grouped = {}
        for row in details:
            if row["stage"]:
                grouped.setdefault(row["stage"], []).append(float(row["duration_ms"] or 0) / 1000)
        return {
            "details": details,
            "by_stage": {
                stage: {"count": len(values), "total_seconds": round(sum(values), 3),
                        "mean_seconds": round(statistics.mean(values), 3)}
                for stage, values in grouped.items()
            },
        }

    try:
        first = await start_run("dense_on")
        runtime = SAGBenchmark(first, SAG)
        async with runtime.serve():
            qdrant_client = await runtime.app.state.engine_manager.get_search_unit_qdrant_client()
            reference = await qdrant_client.get(f"/collections/{identity['collection']}")
            reference.raise_for_status()
            reference_vectors = reference.json().get("result", {}).get("config", {}).get("params", {}).get("vectors", {})
            if not isinstance(reference_vectors, dict) or "content_vector" not in reference_vectors:
                raise ValueError("Reference Qdrant collection has no named content_vector")
            qdrant_vector_dim = int(reference_vectors["content_vector"]["size"])
            for mode, run in (("dense_on", first), ("dense_off", None)):
                if run is None:
                    run = await start_run(mode)
                    runtime.run = run
                    runtime.documents = {}
                    await runtime.login()
                active["mode"] = mode
                search_index_service._SHARED_TEXT_EMBEDDING_CACHE.clear()
                started = time.perf_counter()
                qdrant_started = time.perf_counter()
                await search_index_service.ensure_qdrant_collection_and_indexes(
                    qdrant_client, run.collection, vector_dim=qdrant_vector_dim
                )
                qdrant_prepare_seconds = time.perf_counter() - qdrant_started
                upload_started = time.perf_counter()
                await runtime.ingest(files)
                upload_seconds = time.perf_counter() - upload_started
                processing_started = time.perf_counter()
                state = await runtime.wait_ready()
                processing_seconds = time.perf_counter() - processing_started
                sample = conditions[mode]
                if len(sample["uploads"]) != 8 or len(state["ready_versions"]) != 8:
                    raise AssertionError(f"{mode} did not process all eight documents")
                if not sample["graph_cpu"] or not sample["graph_persistence"]:
                    raise AssertionError(f"{mode} did not build a knowledge graph")
                if mode == "dense_on" and not any(item["semantic_edges"] for item in sample["graph_cpu"]):
                    raise AssertionError("Dense-on graph contained no semantic edge scores")
                if mode == "dense_off" and any(item["semantic_edges"] for item in sample["graph_cpu"]):
                    raise AssertionError("Dense-off graph still contains semantic edge scores")
                sample["pipeline_stages"] = await read_pipeline_stages(run)
                sample.update({
                    "upload_seconds": round(upload_seconds, 3),
                    "qdrant_prepare_seconds": round(qdrant_prepare_seconds, 3),
                    "processing_to_tree_ready_seconds": round(processing_seconds, 3),
                    "total_ingest_to_tree_ready_seconds": round(time.perf_counter() - started, 3),
                    "documents_ready": len(state["ready_versions"]),
                    "knowledge_units": state["units"]["total"],
                    "knowledge_jobs_state": state["jobs"],
                    "active_tree_count": sum(item["status"] == "ACTIVE" for item in state["tree"]),
                    "foundation_job_count": sum(item["kind"] == "FOUNDATION" for item in sample["knowledge_jobs"]),
                    "foundation_job_seconds_total": round(sum(item["seconds"] for item in sample["knowledge_jobs"]
                                                               if item["kind"] == "FOUNDATION"), 3),
                    "graph_cpu_seconds_total": round(sum(item["seconds"] for item in sample["graph_cpu"]), 3),
                    "graph_persistence_seconds_total": round(sum(item["seconds"] for item in sample["graph_persistence"]), 3),
                    "tree_rebuild_seconds_total": round(sum(item["seconds"] for item in sample["tree_rebuilds"]), 3),
                })
                run.manifest["ingest_probe"] = sample
                await run.complete(sample)
                print(f"INGEST_PROBE {mode} ready=8 units={sample['knowledge_units']} "
                      f"total_s={sample['total_ingest_to_tree_ready_seconds']} "
                      f"graph_builds={len(sample['graph_cpu'])}", flush=True)

        if first.manifest.get("probe_protocol", {}).get("corpus_sha256") != runs[1].manifest.get("probe_protocol", {}).get("corpus_sha256"):
            raise AssertionError("On/off conditions used different input files")
        report = {
            "protocol": "8-file fresh-project paired ingest; only KnowledgeUnit dense graph-builder signals differ",
            "order": ["dense_on", "dense_off"],
            "corpus_sha256": expected_hash,
            "conditions": conditions,
            "delta_dense_off_minus_on_seconds": {
                key: round(conditions["dense_off"][key] - conditions["dense_on"][key], 3)
                for key in ("qdrant_prepare_seconds", "upload_seconds", "processing_to_tree_ready_seconds", "total_ingest_to_tree_ready_seconds")
            },
        }
        (output_root / "comparison.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        markdown = [
            "# 8-file ingest: dense graph on/off",
            "",
            "This is a paired, fresh-project comparison. Dense SearchUnit embeddings and KnowledgeUnit embeddings are generated in both runs; the off condition removes dense vectors only from the graph-builder payload. Top-K is fixed at 5 but no search query is issued.",
            "",
            "| Condition | Qdrant setup (s) | Upload (s) | Processing to tree ready (s) | Total incl. setup (s) | Knowledge Units | Graph builds |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
        for mode in ("dense_on", "dense_off"):
            item = conditions[mode]
            markdown.append(
                f"| {mode} | {item['qdrant_prepare_seconds']:.3f} | {item['upload_seconds']:.3f} | "
                f"{item['processing_to_tree_ready_seconds']:.3f} | "
                f"{item['total_ingest_to_tree_ready_seconds']:.3f} | {item['knowledge_units']} | {len(item['graph_cpu'])} |"
            )
        markdown.extend([
            "",
            "## Graph stages",
            "",
            "Graph CPU timings include child-process spawn/IPC and are included within graph persistence, which is itself included within tree rebuild. Do not add these nested timings. Per-build timings, foundation-job timings, Qdrant cleanup status codes and per-stage ingestion timings are in `comparison.json` and each condition's `run_manifest.json`.",
            "",
            "## Scope",
            "",
            "Eight corpus files are selected deterministically across file-size ranks. Each condition gets a new project/source/collection. The graph-off run preserves lexical/entity/structure graph edges and disables only dense graph features; it does not remove dense embeddings from the rest of ingestion.",
            "",
        ])
        (output_root / "summary.md").write_text("\n".join(markdown), encoding="utf-8")
        print(f"REPORT={output_root}", flush=True)
    except BaseException as error:
        for run in runs:
            mode = run.manifest.get("probe_protocol", {}).get("condition")
            if mode in conditions:
                run.manifest["ingest_probe_partial"] = conditions[mode]
                run._write_manifest()
            await run.fail(error)
        (output_root / "failure.json").write_text(json.dumps({
            "error_type": type(error).__name__, "conditions": conditions,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        raise
    finally:
        restore_instrumentation(original)
        for run in runs:
            await run.close()
        for mode in ("dense_on", "dense_off"):
            (output_root / mode / "private-connection.json").unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--identity-manifest", required=True, type=Path)
    args = parser.parse_args()
    asyncio.run(main(args.identity_manifest.resolve()))
