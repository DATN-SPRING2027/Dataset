"""Trace one real SAG document from upload through graph and tree readiness."""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BENCH = ROOT / "RetrievalCI_Bench_v0_2026"
SAG = ROOT.parent / "sag-laya-integration" / "SAG"
CORPUS = BENCH / "examples/rag_eval/bench_v0/corpus"
QUESTIONS = BENCH / "examples/rag_eval/bench_v0/questions.jsonl"


def traced_cpu_entry(connection, operation, payload):
    """Keep the worker protocol intact while recording child startup/import/compute time."""
    import importlib

    entered = time.perf_counter()
    imported = entered
    calculated = entered
    routing_substeps = {}
    response = None
    try:
        from sag_api.services.cpu_worker import _calculate

        modules = {
            "minhash": ("sag_api.services.dedup_and_temporal_service",),
            "dedup_candidates": ("sag_api.services.dedup_and_temporal_service",),
            "graph": ("sag_api.services.knowledge_service",),
            "routing": ("sag_api.services.routing_tree_service", "sag_api.services.tree_publish_service"),
            "prepare_tree": ("sag_api.services.tree_publish_service",),
        }
        for module in modules.get(operation, ()):
            importlib.import_module(module)
        if operation == "routing":
            routing = importlib.import_module("sag_api.services.routing_tree_service")

            def track(function, name):
                def call(*args, **kwargs):
                    started = time.perf_counter()
                    try:
                        return function(*args, **kwargs)
                    finally:
                        stat = routing_substeps.setdefault(name, {"calls": 0, "seconds": 0.0})
                        stat["calls"] += 1
                        stat["seconds"] += time.perf_counter() - started
                return call

            routing._profile = track(routing._profile, "profiles")
            routing._partition = track(routing._partition, "partition")
        imported = time.perf_counter()
        result = _calculate(operation, payload)
        calculated = time.perf_counter()
        response = (True, result)
    except Exception as error:
        response = (False, type(error).__name__)
    finally:
        try:
            with open(os.environ["SAG_TRACE_CPU_TIMINGS"], "a", encoding="utf-8") as output:
                output.write(json.dumps({
                    "operation": operation,
                    "entry_absolute": entered,
                    "import_seconds": round(imported - entered, 3),
                    "calculate_seconds": round(calculated - imported, 3),
                    "routing_substeps": routing_substeps,
                }) + "\n")
        except (OSError, KeyError):
            pass
        try:
            if response is not None:
                connection.send(response)
        finally:
            connection.close()


async def wait_until_ready(runtime, timeline: list, origin: float, poll_seconds: float = 0.5) -> tuple[dict, int]:
    polls = 0
    previous = None
    while True:
        state = await runtime.state()
        polls += 1
        snapshot = {
            "ingestion": state["ingestion"],
            "versions": [[v["search_status"], v["knowledge_status"]] for v in state["ready_versions"]],
            "units": state["units"],
            "evidence": state["evidence"],
            "dense_graph": state["dense_graph"],
            "jobs": [[j["kind"], j["status"], j["count"]] for j in state["jobs"]],
            "tree": [t["status"] for t in state["tree"]],
            "tree_jobs": [str(j["status"]) for j in state["tree_jobs"]],
            "tree_matches_current": state["tree_matches_current"],
        }
        if snapshot != previous:
            timeline.append({"elapsed_seconds": round(time.perf_counter() - origin, 3), **snapshot})
            previous = snapshot
        versions = state["ready_versions"]
        ready = len(versions) == len(runtime.documents) and all(
            version["search_status"] in ("READY", "SEARCH_READY")
            and version["knowledge_status"] == "DATA_READY"
            for version in versions
        )
        if any(
            job.get("error_code") == "DAILY_BUDGET" and job["status"] in ("QUEUED", "RETRY")
            for job in state["jobs"]
        ):
            raise RuntimeError("Knowledge work is deferred by the real SAG daily budget")
        active_jobs = any(
            job["status"] in ("QUEUED", "RUNNING", "RETRY")
            for job in state["jobs"]
        )
        if state["ingestion"].get("FAILED"):
            raise RuntimeError("SAG document ingestion failed; see the retained stage trace")
        if any(
            job["kind"] in ("FOUNDATION", "E2") and job["status"] in ("FAILED", "EXPIRED")
            for job in state["jobs"]
        ):
            raise RuntimeError("SAG KnowledgeUnit foundation or E2 job failed")
        e2_pending = int(state["units"].get("e2_pending", 0) or 0)
        tree_active_jobs = any(job["status"] in ("queued", "running") for job in state["tree_jobs"])
        if ready and not active_jobs and e2_pending == 0 and not tree_active_jobs and state["tree_matches_current"]:
            if state["units"]["with_dense"] != state["units"]["total"]:
                raise RuntimeError("DenseGraph embeddings incomplete in ingest speed trace")
            if state["units"].get("e2_selected", 0) > 0 and state["units"].get("e2_enriched", 0) <= 0:
                raise RuntimeError("E2 enrichment incomplete in ingest speed trace")
            return state, polls
        await asyncio.sleep(poll_seconds)


async def main(identity_manifest: Path) -> None:
    identity = json.loads(identity_manifest.read_text(encoding="utf-8"))
    if identity.get("benchmark") != "retrievalci_v0" or not identity.get("user_id") or not identity.get("organization_id"):
        raise ValueError("Pass a completed RetrievalCI manifest with an active benchmark owner")

    file = max(CORPUS.glob("*.md"), key=lambda path: (path.stat().st_size, path.name))
    file_hash = hashlib.sha256(file.read_bytes()).hexdigest()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_root = ROOT / "reports" / f"ingest-speed-trace-{stamp}"
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

    from sqlalchemy import text
    from sqlalchemy.engine import make_url
    from benchmark_support import BenchmarkRun
    from graph_ingest_ablation_probe import install_instrumentation, restore_instrumentation
    from sag_api.core.config import settings

    url = make_url(settings.database_url)
    settings.database_url = url.set(
        query={**url.query, "search_path": identity["schema"]}
    ).render_as_string(hide_password=False)

    from sag_api.core.db import SessionLocal
    from sag_api.jobs import knowledge
    from sag_api.services import search_index_service, cpu_worker, knowledge_candidate_service, dedup_and_temporal_service
    from sag_api.services import tree_publish_service, universe_tree_service
    from sag_benchmark_runtime import SAGBenchmark

    async with SessionLocal() as session:
        runtime_schema = await session.scalar(text("SELECT current_schema()"))
    if runtime_schema != identity["schema"]:
        raise RuntimeError("SAG runtime database schema does not match benchmark schema")

    sample = {
        "uploads": [], "knowledge_jobs": [], "graph_cpu": [],
        "graph_persistence": [], "tree_rebuilds": [], "qdrant_cleanup": [],
        "search_embedding_batches": [], "knowledge_embedding_batches": [],
        "qdrant_collection_setup": [], "spans": [], "timeline": [],
    }
    conditions = {"dense_on": sample}
    active = {"mode": "dense_on", "project_ids": [], "phase": "startup", "origin": None}
    instrumentation = None
    extra_original = None
    span_originals = []
    run = None
    try:
        run_dir = output_root / "result"
        os.environ["SAG_BENCHMARK_OUTPUT_DIR"] = str(run_dir)
        run = BenchmarkRun("ingest_speed_trace", BENCH, settings.database_url)
        registration_started = time.perf_counter()
        await run.start([file], QUESTIONS, {
            "mode": "single_file_full_ingest_speed_trace",
            "dense_graph": True,
            "e2_enrichment": False,
            "top_k": 5,
        })
        registration_seconds = time.perf_counter() - registration_started
        active["project_ids"] = [run.project_id]
        for key, value in {
            "DATA_DIR": str(output_root / "engine"),
            "UPLOAD_DIR": str(output_root / "uploads"),
            "DSH_CONNECTION_FILE": str(output_root / "private-connection.json"),
        }.items():
            setattr(settings, key.lower(), value)
        run.manifest["probe_protocol"] = {
            "file": file.relative_to(BENCH).as_posix(),
            "bytes": file.stat().st_size,
            "sha256": file_hash,
            "dense_graph": True,
            "top_k": "fixed at 5; no retrieval query issued",
            "pipeline": "real SAG upload, parse, dedup/temporal, SearchUnit index, KnowledgeUnit foundation, graph build/persist, tree publish",
            "queue_isolation": "skip recovery of pre-existing document jobs and scope ORM queries to this fresh project",
            "runtime_schema": runtime_schema,
            "qdrant_setup": "production collection/index helper run once before upload to avoid the observed fresh-index race; setup duration included in ingest wall time",
        }
        run._write_manifest()

        instrumentation = install_instrumentation(conditions, active)
        extra_original = {
            "compute_embeddings": search_index_service.compute_unit_embeddings,
            "ensure_qdrant": search_index_service.ensure_qdrant_collection_and_indexes,
            "embed_blocks": knowledge._embed_blocks,
        }

        async def timed_search_embeddings(embedder, texts):
            started = time.perf_counter()
            vectors = await extra_original["compute_embeddings"](embedder, texts)
            sample["search_embedding_batches"].append({
                "texts": len(texts),
                "vectors": len(vectors),
                "seconds": round(time.perf_counter() - started, 3),
            })
            return vectors

        async def timed_knowledge_embeddings(embedder, blocks):
            started = time.perf_counter()
            vectors = await extra_original["embed_blocks"](embedder, blocks)
            sample["knowledge_embedding_batches"].append({
                "blocks": len(blocks),
                "vectors": len(vectors),
                "seconds": round(time.perf_counter() - started, 3),
            })
            return vectors

        async def timed_qdrant_setup(client, collection, vector_dim=1536):
            started = time.perf_counter()
            result = await extra_original["ensure_qdrant"](client, collection, vector_dim)
            sample["qdrant_collection_setup"].append({
                "phase": active["phase"],
                "seconds": round(time.perf_counter() - started, 3),
            })
            return result

        search_index_service.compute_unit_embeddings = timed_search_embeddings
        search_index_service.ensure_qdrant_collection_and_indexes = timed_qdrant_setup
        knowledge._embed_blocks = timed_knowledge_embeddings

        def trace_async(module, name, label):
            original = getattr(module, name)
            span_originals.append((module, name, original))

            async def traced(*args, **kwargs):
                started = time.perf_counter()
                try:
                    return await original(*args, **kwargs)
                finally:
                    origin = active["origin"]
                    if origin is not None:
                        sample["spans"].append({
                            "name": label,
                            "start_seconds": round(started - origin, 3),
                            "duration_seconds": round(time.perf_counter() - started, 3),
                        })
            setattr(module, name, traced)

        for module, name, label in (
            (dedup_and_temporal_service, "run_dedup_and_temporal_stage", "ingest.dedup_temporal"),
            (search_index_service, "run_search_indexing_stage", "ingest.index_search"),
            (search_index_service, "compute_unit_embeddings", "index.search_embeddings"),
            (search_index_service, "ensure_qdrant_collection_and_indexes", "index.ensure_qdrant"),
            (knowledge, "_embed_blocks", "foundation.knowledge_embeddings"),
            (knowledge, "rebuild_knowledge_version", "foundation.rebuild_units"),
            (universe_tree_service, "rebuild_project_universe_tree", "tree.rebuild"),
            (universe_tree_service, "build_project_routing_snapshot", "tree.snapshot"),
            (universe_tree_service, "_search_unit_assignments", "tree.assignments"),
            (universe_tree_service, "publish_tree_candidate", "tree.publish"),
            (knowledge_candidate_service, "current_units", "snapshot.current_units"),
            (knowledge_candidate_service, "persist_graph", "snapshot.persist_graph"),
            (tree_publish_service, "_stage_candidate", "publish.stage_db"),
            (tree_publish_service, "_verify_database_search_units", "publish.verify_db_units"),
            (tree_publish_service, "_clear_inactive_slot_qdrant_payloads", "publish.clear_qdrant_slot"),
            (tree_publish_service, "update_inactive_slot_qdrant_payloads", "publish.write_qdrant_payloads"),
            (tree_publish_service, "_verify_staged_candidate", "publish.verify_staged_db"),
            (tree_publish_service, "_verify_qdrant_slot", "publish.verify_qdrant_slot"),
            (tree_publish_service, "_count_qdrant_points", "publish.qdrant_count"),
            (tree_publish_service, "_verify_qdrant_point_payloads", "publish.verify_qdrant_points"),
            (tree_publish_service, "_atomic_switch", "publish.atomic_switch"),
        ):
            trace_async(module, name, label)

        original_cpu = cpu_worker.run_cpu
        span_originals.append((cpu_worker, "run_cpu", original_cpu))
        span_originals.append((cpu_worker, "_entry", cpu_worker._entry))
        cpu_worker._entry = traced_cpu_entry
        cpu_trace_path = output_root / "cpu_child_timings.jsonl"
        os.environ["SAG_TRACE_CPU_TIMINGS"] = str(cpu_trace_path)

        async def timed_cpu(operation, payload):
            started = time.perf_counter()
            try:
                return await original_cpu(operation, payload)
            finally:
                origin = active["origin"]
                if origin is not None:
                    sample["spans"].append({
                        "name": f"cpu.{operation}",
                        "start_seconds": round(started - origin, 3),
                        "duration_seconds": round(time.perf_counter() - started, 3),
                    })
        cpu_worker.run_cpu = timed_cpu

        runtime = SAGBenchmark(run, SAG)
        service_started = time.perf_counter()
        async with runtime.serve():
            app_startup_seconds = time.perf_counter() - service_started
            qdrant_client = await runtime.app.state.engine_manager.get_search_unit_qdrant_client()
            reference = await qdrant_client.get(f"/collections/{identity['collection']}")
            reference.raise_for_status()
            vectors = reference.json().get("result", {}).get("config", {}).get("params", {}).get("vectors", {})
            if not isinstance(vectors, dict) or "content_vector" not in vectors:
                raise ValueError("Reference Qdrant collection has no named content_vector")

            ingest_started = time.perf_counter()
            active["phase"] = "qdrant_preflight"
            await search_index_service.ensure_qdrant_collection_and_indexes(
                qdrant_client, run.collection, vector_dim=int(vectors["content_vector"]["size"])
            )
            sample["qdrant_preflight_seconds"] = sample["qdrant_collection_setup"][-1]["seconds"]
            search_index_service._SHARED_TEXT_EMBEDDING_CACHE.clear()
            active["phase"] = "document_ingest"
            upload_started = time.perf_counter()
            active["origin"] = upload_started
            await runtime.ingest([file])
            upload_finished = time.perf_counter()
            state, polls = await wait_until_ready(runtime, sample["timeline"], upload_started)
            ready_at = time.perf_counter()
            child_timings = []
            if cpu_trace_path.exists():
                for line in cpu_trace_path.read_text(encoding="utf-8").splitlines():
                    record = json.loads(line)
                    record["entry_seconds"] = round(record.pop("entry_absolute") - upload_started, 3)
                    child_timings.append(record)
            sample["cpu_child_timings"] = child_timings

            async with SessionLocal() as session:
                rows = (await session.execute(text("""
                    SELECT i.id AS ingestion_run_id, i.status AS ingestion_status,
                           s.stage, s.status AS stage_status, s.duration_ms
                    FROM ingestion_runs i LEFT JOIN stage_runs s ON s.run_id=i.id
                    WHERE i.project_id=:project AND i.tenant_id=:tenant
                    ORDER BY i.created_at, s.created_at
                """), {"project": run.project_id, "tenant": run.organization_id})).mappings().all()
            details = [dict(row) for row in rows]
            stage_totals = {}
            for row in details:
                if row["stage"]:
                    stage_totals.setdefault(row["stage"], []).append(float(row["duration_ms"] or 0) / 1000)
            sample.update({
                "file": file.relative_to(BENCH).as_posix(),
                "bytes": file.stat().st_size,
                "sha256": file_hash,
                "benchmark_registration_seconds": round(registration_seconds, 3),
                "app_startup_and_login_seconds": round(app_startup_seconds, 3),
                "qdrant_preflight_seconds": round(sample["qdrant_preflight_seconds"], 3),
                "upload_service_seconds": round(upload_finished - upload_started, 3),
                "processing_after_upload_seconds": round(ready_at - upload_finished, 3),
                "upload_to_tree_active_seconds": round(ready_at - upload_started, 3),
                "collection_setup_to_tree_active_seconds": round(ready_at - ingest_started, 3),
                "service_start_to_tree_active_seconds": round(ready_at - service_started, 3),
                "poll_interval_seconds": 0.5,
                "readiness_polls": polls,
                "documents_ready": len(state["ready_versions"]),
                "knowledge_units": state["units"]["total"],
                "foundation_job_count": sum(job["kind"] == "FOUNDATION" for job in sample["knowledge_jobs"]),
                "foundation_job_seconds_total": round(sum(job["seconds"] for job in sample["knowledge_jobs"] if job["kind"] == "FOUNDATION"), 3),
                "graph_cpu_seconds_total": round(sum(item["seconds"] for item in sample["graph_cpu"]), 3),
                "graph_persistence_seconds_total": round(sum(item["seconds"] for item in sample["graph_persistence"]), 3),
                "tree_rebuild_seconds_total": round(sum(item["seconds"] for item in sample["tree_rebuilds"]), 3),
                "ingestion_stages": {
                    stage: {
                        "count": len(values),
                        "total_seconds": round(sum(values), 3),
                        "mean_seconds": round(sum(values) / len(values), 3),
                    }
                    for stage, values in stage_totals.items()
                },
                "ingestion_stage_details": details,
                "final_state": state,
            })
            assert sample["documents_ready"] == 1, "The single uploaded document did not reach READY"
            assert sample["graph_cpu"], "No graph build was traced"
            assert sample["tree_rebuilds"], "No tree rebuild was traced"
            run.manifest["speed_trace"] = sample
            await run.complete(sample)

        report = [
            "# Single-file full ingest speed trace",
            "",
            f"File: `{file.relative_to(BENCH).as_posix()}` ({file.stat().st_size:,} bytes).",
            "Real SAG path: upload → parse → dedup/temporal → SearchUnit index → KnowledgeUnit foundation → graph build/persist → active tree.",
            "Dense graph is enabled. Top-K is fixed at 5; no retrieval query or quality metric was run.",
            "",
            "## Wall clock",
            "",
            "| Segment | Seconds |",
            "|---|---:|",
            f"| Benchmark registration | {sample['benchmark_registration_seconds']:.3f} |",
            f"| SAG app startup + login | {sample['app_startup_and_login_seconds']:.3f} |",
            f"| Fresh Qdrant collection/index setup | {sample['qdrant_preflight_seconds']:.3f} |",
            f"| Upload service | {sample['upload_service_seconds']:.3f} |",
            f"| Upload start → tree ACTIVE | {sample['upload_to_tree_active_seconds']:.3f} |",
            f"| Collection setup start → tree ACTIVE | {sample['collection_setup_to_tree_active_seconds']:.3f} |",
            f"| App start → tree ACTIVE | {sample['service_start_to_tree_active_seconds']:.3f} |",
            "",
            "## Pipeline stages",
            "",
            "Stage durations are from SAG `stage_runs`; KnowledgeUnit, graph, persistence, and tree timings are instrumented separately. Stage durations can overlap with background jobs.",
            "",
            "| Stage | Count | Total seconds | Mean seconds |",
            "|---|---:|---:|---:|",
        ]
        for stage, values in sample["ingestion_stages"].items():
            report.append(f"| {stage} | {values['count']} | {values['total_seconds']:.3f} | {values['mean_seconds']:.3f} |")
        report.extend([
            "",
            "## Knowledge and graph stages",
            "",
            f"- KnowledgeUnit Foundation jobs: {sample['foundation_job_count']} job(s), {sample['foundation_job_seconds_total']:.3f} s total.",
            f"- SearchUnit embedding batches: `{json.dumps(sample['search_embedding_batches'], ensure_ascii=False)}`.",
            f"- KnowledgeUnit embedding batches: `{json.dumps(sample['knowledge_embedding_batches'], ensure_ascii=False)}`.",
            f"- Graph CPU: {sample['graph_cpu_seconds_total']:.3f} s, included in graph persistence: {sample['graph_persistence_seconds_total']:.3f} s.",
            f"- Tree rebuild: {sample['tree_rebuild_seconds_total']:.3f} s, including graph persistence; do not add these nested durations.",
            "",
            "Raw per-stage records, graph edge counts, Qdrant statuses, and final state are in `trace.json` and the run manifest.",
            "",
        ])
        (output_root / "summary.md").write_text("\n".join(report), encoding="utf-8")
        (output_root / "trace.json").write_text(json.dumps(sample, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"SPEED_TRACE={output_root}", flush=True)
    except BaseException as error:
        if run is not None and run.started:
            run.manifest["speed_trace_partial"] = sample
            run._write_manifest()
            await run.fail(error)
        (output_root / "failure.json").write_text(json.dumps({
            "error_type": type(error).__name__, "trace": sample,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        raise
    finally:
        for module, name, original in reversed(span_originals):
            setattr(module, name, original)
        if extra_original is not None:
            search_index_service.compute_unit_embeddings = extra_original["compute_embeddings"]
            search_index_service.ensure_qdrant_collection_and_indexes = extra_original["ensure_qdrant"]
            knowledge._embed_blocks = extra_original["embed_blocks"]
        if instrumentation is not None:
            restore_instrumentation(instrumentation)
        if run is not None:
            await run.close()
        os.environ.pop("SAG_TRACE_CPU_TIMINGS", None)
        (output_root / "private-connection.json").unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--identity-manifest", required=True, type=Path)
    args = parser.parse_args()
    asyncio.run(main(args.identity_manifest.resolve()))
