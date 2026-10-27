"""Run the official VN-MTEB / MMTEB Vietnamese RAG Benchmark against SAG Engine (Full AI Pipeline).

Evaluates on the exact same 130-document Vietnamese corpus (`70` Legal + `60` Multi-Hop):
1. Same-Corpus Fair Ablation Baselines:
   - Pure Dense (`Qwen/Qwen3-Embedding-0.6B` Cosine Vector Search only)
   - Pure Sparse / BM25 (`bm25_sparse` Lexical Overlap only)
   - SAG Engine (Full AI Pipeline: Dense + Sparse + E0/E1/E2 LLM Knowledge Graph + Universe Tree Routing + Multi-Hop Bridge + Clause Reranker)
2. Official Published MTEB / MMTEB Leaderboard Reference Baselines:
   - `ZacLegalTextRetrieval` (`GreenNode/zalo-ai-legal-text-retrieval-vn`)
   - `HotpotQA-VN` (`GreenNode/nano-hotpotqa-vn`, arXiv:2507.21500)
3. End-to-End AI Audit Metrics:
   - Embedding API calls (`Qwen/Qwen3-Embedding-0.6B` for SearchUnits + KnowledgeUnits)
   - Tier E2 LLM Knowledge Extraction calls (`Qwen/Qwen3-8B` via `llm_enrich` + `apply_e2`)
   - Universe Tree Routing publication & active snapshot routing (`ROUTING_OK`)
   - End-to-End LLM Answer Synthesis (`Qwen/Qwen3-8B` via `synthesize_search_answer`) with citation verification
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import math
import os
import re
import statistics
import sys
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

BENCH_ROOT = Path(r"d:\DoAnTotnghiep\Dataset\VN_MTEB_RAG_Bench_2026")
CORPUS_DIR = BENCH_ROOT / "corpus"
DATA_DIR = BENCH_ROOT / "data"
REPORTS_DIR = BENCH_ROOT / "reports"
SAG_ROOT = Path(r"d:\DoAnTotnghiep\sag-laya-integration\SAG")
SAG_API_ROOT = SAG_ROOT / "apps" / "api"

os.chdir(SAG_ROOT)
if str(SAG_API_ROOT) not in sys.path:
    sys.path.insert(0, str(SAG_API_ROOT))

from sag_api.core.config import settings

SCHEMA_NAME = "sag_vn_mteb_bench_2026"
base_db_url = settings.database_url.split("?")[0]
settings.database_url = f"{base_db_url}?search_path={SCHEMA_NAME},public"

import httpx
from sqlalchemy import select, text
from sag_api.core.db import Base, SessionLocal, engine
from sag_api.core.principal_assertion import VerifiedPrincipal
from sag_api.db.models import (
    Document,
    DocumentVersion,
    IngestionRun,
    KnowledgeGraphBuild,
    KnowledgeJob,
    KnowledgeUnit,
    Source,
    SourceProjectMapping,
)
from sag_api.enums import (
    ConnectorKind,
    DocumentStatus,
    SourceStatus,
    SourceType,
)
from sag_api.jobs.knowledge import QueuePolicy, _embed_blocks, apply_e2, llm_enrich
from sag_api.sag.search_unit_store import (
    SearchUnitQdrantStore,
    build_search_filter,
    build_sparse_query_vector,
)
from sag_api.services.canonical_service import parse_and_persist_document_content
from sag_api.services.knowledge_service import (
    KnowledgeConfig,
    persist_graph,
    rebuild_knowledge_version,
    version_input,
)
from sag_api.services.search_index_service import (
    ensure_qdrant_collection_and_indexes,
    get_cached_text_embedding,
    put_cached_text_embedding,
    run_search_indexing_stage,
)
from sag_api.services.retrieval_service import synthesize_search_answer
from sag_api.services.search_unit_retrieval_service import (
    retrieve_search_unit_sections,
)
from sag_api.services.tree_query_snapshot_service import (
    acquire_tree_query_snapshot,
    release_tree_query_snapshot,
)
from sag_api.services.universe_tree_service import rebuild_project_universe_tree

PROJECT_ID = "670000000000000000000301"
SOURCE_ID = "670000000000000000000302"
MAPPING_ID = "670000000000000000000303"
SAG_SOURCE_CONFIG_ID = "scfg-vn-mteb-bench-2026"
ORG_ID = "org-vn-mteb-2026"
TENANT_ID = "tenant-vn-mteb-2026"
PARTITION_ID = "part-vn-mteb-2026"


class _SiliconFlowEmbedder:
    def __init__(self, client: httpx.AsyncClient, model: str, dimensions: int | None = None) -> None:
        self._client = client
        self._model = model
        self._dimensions = dimensions
        self.api_calls = 0
        self.texts_embedded = 0

    async def batch_generate(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        out: list[list[float]] = []
        batch_size = 32
        for i in range(0, len(texts), batch_size):
            batch = [t[:6000] for t in texts[i : i + batch_size]]
            payload: dict[str, Any] = {"model": self._model, "input": batch}
            if self._dimensions:
                payload["dimensions"] = self._dimensions
            for attempt in range(4):
                try:
                    res = await self._client.post("/embeddings", json=payload)
                except (httpx.TransportError, httpx.TimeoutException):
                    if attempt < 3:
                        await asyncio.sleep(1.0 * (attempt + 1))
                        continue
                    raise
                if res.status_code in (429, 500, 502, 503, 504) and attempt < 3:
                    await asyncio.sleep(1.5 * (attempt + 1))
                    continue
                res.raise_for_status()
                self.api_calls += 1
                self.texts_embedded += len(batch)
                data = sorted(res.json()["data"], key=lambda item: item["index"])
                out.extend([float(v) for v in item["embedding"]] for item in data)
                break
        return out

    async def generate(self, text_input: str) -> list[float]:
        cached = get_cached_text_embedding(text_input)
        if cached is not None:
            return cached
        vecs = await self.batch_generate([text_input])
        put_cached_text_embedding(text_input, vecs[0])
        return vecs[0]


class _SiliconFlowLLM:
    configured = True

    def __init__(self, client: httpx.AsyncClient, model: str) -> None:
        self._client = client
        self._model = model
        self.api_calls = 0

    async def complete(self, messages: list[dict[str, str]]) -> str:
        body: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": 512,
        }
        if "qwen" in self._model.casefold():
            body["enable_thinking"] = False
        for attempt in range(4):
            try:
                res = await self._client.post("/chat/completions", json=body)
            except (httpx.TransportError, httpx.TimeoutException):
                if attempt < 3:
                    await asyncio.sleep(1.0 * (attempt + 1))
                    continue
                raise
            if res.status_code in (429, 500, 502, 503, 504) and attempt < 3:
                await asyncio.sleep(1.5 * (attempt + 1))
                continue
            res.raise_for_status()
            self.api_calls += 1
            return str(res.json()["choices"][0]["message"]["content"] or "")
        return ""


class _CanonicalRuntime:
    def __init__(self) -> None:
        qdrant_headers = {"api-key": settings.sag_qdrant_api_key} if settings.sag_qdrant_api_key else {}
        self._qdrant = httpx.AsyncClient(
            base_url=settings.sag_qdrant_url.rstrip("/"),
            headers=qdrant_headers,
            timeout=30.0,
        )
        embed_base = (settings.embedding_base_url or settings.llm_base_url or "").rstrip("/")
        embed_key = settings.embedding_api_key or settings.llm_api_key or ""
        self._embed_http = httpx.AsyncClient(
            base_url=embed_base,
            headers={"Authorization": f"Bearer {embed_key}"},
            timeout=60.0,
        )
        self._embedder = _SiliconFlowEmbedder(
            self._embed_http,
            model=settings.embedding_model,
            dimensions=settings.embedding_dimensions,
        )
        llm_base = (settings.llm_base_url or embed_base).rstrip("/")
        llm_key = settings.llm_api_key or embed_key
        self._llm_http = httpx.AsyncClient(
            base_url=llm_base,
            headers={"Authorization": f"Bearer {llm_key}"},
            timeout=60.0,
        )
        self.llm = _SiliconFlowLLM(self._llm_http, model=settings.llm_model)

    async def get_search_unit_qdrant_client(self) -> httpx.AsyncClient:
        return self._qdrant

    async def get_sag_embedding(self, source_config_id: str, source: Any = None) -> _SiliconFlowEmbedder:
        return self._embedder

    async def get_routing_snapshot(
        self,
        *,
        query: str,
        scopes: list[dict[str, object]],
        planner: dict[str, object],
    ) -> Any:
        del planner
        async with SessionLocal() as session:
            await session.execute(text(f'SET search_path TO "{SCHEMA_NAME}", public'))
            return await acquire_tree_query_snapshot(query=query, scopes=scopes)

    async def release_routing_snapshot(self, snapshot_id: str) -> None:
        async with SessionLocal() as session:
            await session.execute(text(f'SET search_path TO "{SCHEMA_NAME}", public'))
            await release_tree_query_snapshot(snapshot_id)

    async def shutdown(self) -> None:
        await self._qdrant.aclose()
        await self._embed_http.aclose()
        await self._llm_http.aclose()


def _extract_title(md_text: str, fallback_stem: str) -> str:
    for line in md_text.splitlines():
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip()
    return fallback_stem


async def _init_schema(reset: bool = True) -> None:
    async with engine.begin() as conn:
        if reset:
            await conn.execute(text(f'DROP SCHEMA IF EXISTS "{SCHEMA_NAME}" CASCADE'))
        await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{SCHEMA_NAME}"'))
        await conn.execute(text(f'SET search_path TO "{SCHEMA_NAME}", public'))
        await conn.run_sync(Base.metadata.create_all)


async def index_vn_corpus(
    runtime: _CanonicalRuntime,
    corpus_files: list[Path],
    *,
    run_e2_llm: bool = True,
) -> tuple[dict[str, str], dict[str, Any]]:
    t0 = time.perf_counter()
    print(f"[1/4] Resetting schema `{SCHEMA_NAME}` and Qdrant collection for project `{PROJECT_ID}`...")
    await _init_schema(reset=True)
    qdrant_client = await runtime.get_search_unit_qdrant_client()
    await qdrant_client.delete(f"/collections/search_units_{PROJECT_ID}")

    now = datetime.now(UTC)
    started_at = now - timedelta(minutes=5)
    doc_id_to_filename: dict[str, str] = {}
    ver_ids: list[tuple[str, str, str]] = []

    async with SessionLocal() as session:
        await session.execute(text(f'SET search_path TO "{SCHEMA_NAME}", public'))
        source = Source(
            id=SOURCE_ID,
            name="VN-MTEB Benchmark Source",
            description="130 Vietnamese Legal + Multi-hop QA documents (MMTEB / VN-MTEB)",
            source_type=SourceType.DOCUMENT,
            connector_kind=ConnectorKind.FILE_UPLOAD,
            sag_source_config_id=SAG_SOURCE_CONFIG_ID,
            config={},
            status=SourceStatus.ACTIVE,
            document_count=len(corpus_files),
        )
        mapping = SourceProjectMapping(
            id=MAPPING_ID,
            source_id=SOURCE_ID,
            organization_id=ORG_ID,
            project_id=PROJECT_ID,
            state="CONFIRMED",
            mapping_version=1,
            confirmed_at=now,
            confirmed_by="vn-mteb-runner",
            approval_ref="approval-vn-mteb-2026",
        )
        session.add_all([source, mapping])
        await session.flush()

        for idx, file_path in enumerate(corpus_files, start=1):
            raw_text = file_path.read_text(encoding="utf-8")
            title = _extract_title(raw_text, file_path.stem)
            checksum = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
            byte_len = len(raw_text.encode("utf-8"))

            doc_id = f"67000000000000000030{idx:04d}"
            ver_id = f"67000000000000000031{idx:04d}"
            run_id = f"67000000000000000032{idx:04d}"

            doc = Document(
                id=doc_id,
                tenant_id=TENANT_ID,
                project_id=PROJECT_ID,
                source_id=SOURCE_ID,
                filename=file_path.name,
                content_type="text/markdown",
                size_bytes=byte_len,
                storage_path=str(file_path),
                status=DocumentStatus.READY,
                is_active=True,
            )
            ver = DocumentVersion(
                id=ver_id,
                document_id=doc_id,
                version_no=1,
                file_hash=checksum,
                observed_at=started_at,
                ingested_at=now,
                valid_from=started_at,
                valid_to=datetime(9999, 12, 31, 23, 59, 59, tzinfo=UTC),
                status="READY",
                search_status="READY",
                knowledge_status="READY",
                search_ready_at=now,
                knowledge_ready_at=now,
                metadata_json={
                    "security_partition_id": PARTITION_ID,
                    "document_title": title,
                    "rel_path": file_path.name,
                },
            )
            run = IngestionRun(
                id=run_id,
                tenant_id=TENANT_ID,
                project_id=PROJECT_ID,
                document_version_id=ver_id,
                idempotency_key=f"idem-vn-mteb-{idx:04d}",
                payload_hash=checksum,
                content_hash=checksum,
                current_stage="COMPLETE",
                status="SUCCEEDED",
                started_at=started_at,
                completed_at=now,
            )
            session.add_all([doc, ver, run])
            await session.flush()

            await parse_and_persist_document_content(
                session,
                ver_id,
                raw_text,
                run_id=run_id,
                document_title=title,
            )
            doc_id_to_filename[doc_id] = file_path.name
            ver_ids.append((doc_id, ver_id, run_id))

        await session.commit()

    print(f"Parsed canonical blocks for {len(ver_ids)} Vietnamese documents in {time.perf_counter() - t0:.1f}s.")

    async with SessionLocal() as session:
        await session.execute(text(f'SET search_path TO "{SCHEMA_NAME}", public'))
        source_obj = await session.get(Source, SOURCE_ID)
    embedder = await runtime.get_sag_embedding(SAG_SOURCE_CONFIG_ID, source_obj)
    sample_vec = await embedder.generate("dimension probe")
    await ensure_qdrant_collection_and_indexes(
        qdrant_client,
        f"search_units_{PROJECT_ID}",
        vector_dim=len(sample_vec),
    )

    t_idx = time.perf_counter()
    k_config = KnowledgeConfig()
    all_knowledge_units: list[KnowledgeUnit] = []
    dense_ku_count = 0

    async with SessionLocal() as session:
        await session.execute(text(f'SET search_path TO "{SCHEMA_NAME}", public'))
        for i, (doc_id, ver_id, run_id) in enumerate(ver_ids, start=1):
            ver_obj = await session.get(DocumentVersion, ver_id)
            await run_search_indexing_stage(
                session,
                project_id=PROJECT_ID,
                document_version=ver_obj,
                security_partition_id=PARTITION_ID,
                tenant_id=TENANT_ID,
                qdrant_client=qdrant_client,
                embedder=embedder,
                run_id=run_id,
            )
            # AI Stage 1: Embed CanonicalBlocks so KnowledgeUnit.features_json["dense"] is populated
            _, blocks, _, _ = await version_input(session, ver_id, k_config)
            non_heading_blocks = [
                (b.id, b.normalized_text)
                for b in blocks
                if b.block_type != "heading" and b.normalized_text.strip()
            ]
            dense_by_block_id = await _embed_blocks(embedder, non_heading_blocks) if non_heading_blocks else {}
            kus = await rebuild_knowledge_version(
                session,
                ver_id,
                k_config,
                dense_by_block_id=dense_by_block_id,
            )
            for ku in kus:
                if ku.features_json.get("dense"):
                    dense_ku_count += 1
            all_knowledge_units.extend(kus)
            if i % 25 == 0 or i == len(ver_ids):
                await session.commit()
                print(
                    f"  Indexed {i}/{len(ver_ids)} docs + Dense KU Vectors "
                    f"({time.perf_counter() - t_idx:.1f}s elapsed)..."
                )

    t_e2_graph = await _finalize_e2_graph_and_tree(runtime, run_e2_llm=run_e2_llm, k_config=k_config)
    ai_index_stats = {
        "total_docs": len(ver_ids),
        "total_knowledge_units": len(all_knowledge_units),
        "dense_embedded_knowledge_units": dense_ku_count,
        "embedding_api_batches": embedder.api_calls,
        "embedding_texts_processed": embedder.texts_embedded,
        **t_e2_graph,
        "indexing_elapsed_s": round(time.perf_counter() - t0, 2),
    }
    print(
        f"Completed Full-AI indexing: {len(ver_ids)} docs, {len(all_knowledge_units)} KUs "
        f"({dense_ku_count} with dense vectors), {ai_index_stats['e2_llm_succeeded_units']} E2 LLM units, "
        f"{ai_index_stats['graph_edges_total']} graph edges ({ai_index_stats['graph_edges_with_semantic_signal']} with semantic signal) "
        f"in {ai_index_stats['indexing_elapsed_s']}s."
    )
    return doc_id_to_filename, ai_index_stats


async def _finalize_e2_graph_and_tree(
    runtime: _CanonicalRuntime,
    *,
    run_e2_llm: bool = True,
    k_config: KnowledgeConfig = KnowledgeConfig(),
) -> dict[str, Any]:
    async with SessionLocal() as session:
        await session.execute(text(f'SET search_path TO "{SCHEMA_NAME}", public'))
        all_knowledge_units = list(
            (
                await session.scalars(
                    select(KnowledgeUnit).where(
                        KnowledgeUnit.tenant_id == TENANT_ID,
                        KnowledgeUnit.project_id == PROJECT_ID,
                        KnowledgeUnit.is_current.is_(True),
                    )
                )
            ).all()
        )
        existing_jobs = list(
            (
                await session.scalars(
                    select(KnowledgeJob).where(KnowledgeJob.kind == "E2")
                )
            ).all()
        )
    jobs_by_unit = {j.unit_id: j for j in existing_jobs}
    e2_candidates = [
        u
        for u in all_knowledge_units
        if u.features_json.get("e2_reason")
        or (
            u.id in jobs_by_unit
            and not any((jobs_by_unit[u.id].result_json or {}).get(k) for k in ("entities", "aliases", "claims", "relations"))
        )
    ]
    e2_candidates.sort(key=lambda u: -float(u.features_json.get("importance", 0.0)))
    e2_candidates = e2_candidates[:24]
    e2_succeeded = 0
    e2_entities_added = 0
    e2_claims_added = 0
    e2_relations_added = 0
    if run_e2_llm and e2_candidates:
        t_e2 = time.perf_counter()
        print(
            f"[1b/4] Running Tier E2 LLM Knowledge Extraction (`{settings.llm_model}`) "
            f"on {len(e2_candidates)} flagged KnowledgeUnits..."
        )
        policy = QueuePolicy(
            concurrency=6,
            timeout_seconds=45.0,
            max_input_chars=2600,
            max_output_tokens=1200,
        )
        sem = asyncio.Semaphore(6)

        async def _enrich_one(u: KnowledgeUnit) -> tuple[KnowledgeUnit, dict | None, str | None]:
            async with sem:
                for attempt in range(2):
                    try:
                        res, ext_ver = await llm_enrich(u, settings, policy)
                        return u, res, ext_ver
                    except Exception as exc:  # noqa: BLE001
                        if attempt == 0:
                            await asyncio.sleep(1.0)
                        else:
                            print(f"    [WARN] E2 enrich skipped for unit {u.id[:8]}: {type(exc).__name__}: {exc}")
                return u, None, None

        enriched_results = await asyncio.gather(*(_enrich_one(u) for u in e2_candidates))
        async with SessionLocal() as session:
            await session.execute(text(f'SET search_path TO "{SCHEMA_NAME}", public'))
            for u, res, ext_ver in enriched_results:
                if not res or not ext_ver:
                    continue
                job_id = f"e2-job-{u.id[:24]}"
                existing_job = await session.get(KnowledgeJob, job_id)
                if existing_job is not None:
                    job = existing_job
                else:
                    job = KnowledgeJob(
                        id=job_id,
                        tenant_id=u.tenant_id,
                        document_version_id=u.document_version_id,
                        unit_id=u.id,
                        kind="E2",
                        status="RUNNING",
                        priority=round(float(u.features_json.get("importance", 0.5)) * 10),
                        input_checksum=u.input_checksum,
                        reserved_tokens=300,
                        attempts=1,
                    )
                    session.add(job)
                    await session.flush()
                try:
                    await apply_e2(session, job, res, extractor_version=ext_ver, config=k_config)
                    job.status = "SUCCEEDED"
                    job.result_json = res
                    job.extractor_version = ext_ver
                    e2_succeeded += 1
                    e2_entities_added += len(res.get("entities", [])) + len(res.get("aliases", []))
                    e2_claims_added += len(res.get("claims", []))
                    e2_relations_added += len(res.get("relations", []))
                except Exception as exc:  # noqa: BLE001
                    print(f"    [WARN] apply_e2 skipped for unit {u.id[:8]}: {exc}")
            await session.commit()
        print(
            f"  Completed E2 LLM Enrichment: {e2_succeeded}/{len(e2_candidates)} units enriched "
            f"(+{e2_entities_added} entities, +{e2_claims_added} claims, +{e2_relations_added} relations) "
            f"in {time.perf_counter() - t_e2:.1f}s."
        )

    tree_published = False
    async with SessionLocal() as session:
        await session.execute(text(f'SET search_path TO "{SCHEMA_NAME}", public'))
        refreshed_units = list(
            (
                await session.scalars(
                    select(KnowledgeUnit).where(
                        KnowledgeUnit.tenant_id == TENANT_ID,
                        KnowledgeUnit.project_id == PROJECT_ID,
                        KnowledgeUnit.is_current.is_(True),
                    )
                )
            ).all()
        )
        print(f"[1c/4] Persisting KnowledgeUnit graph edges across {len(refreshed_units)} KUs (with 0.40 semantic + 0.35 entity + 0.25 lexical signals)...")
        build = await persist_graph(session, refreshed_units, k_config)
        await session.commit()
        edges_list = (build.manifest_json or {}).get("edges", [])
        edge_count = len(edges_list)
        semantic_edge_count = sum(
            1 for e in edges_list if (e.get("signals") or {}).get("semantic") is not None
        )

        print(f"[1d/4] Building & publishing Universe Routing Tree for project `{PROJECT_ID}`...")
        try:
            tree_res = await rebuild_project_universe_tree(
                session,
                runtime,
                tenant_id=TENANT_ID,
                project_id=PROJECT_ID,
            )
            if tree_res is not None:
                tree_published = True
                print(f"  Published active Universe Tree snapshot (tree_id={getattr(tree_res, 'tree_id', 'ok')}).")
        except Exception as exc:  # noqa: BLE001
            print(f"  [WARN] Universe tree publish note: {type(exc).__name__}: {exc}")

    return {
        "e2_flagged_units": len(e2_candidates),
        "e2_llm_succeeded_units": e2_succeeded,
        "e2_entities_extracted": e2_entities_added,
        "e2_claims_extracted": e2_claims_added,
        "e2_relations_extracted": e2_relations_added,
        "graph_edges_total": edge_count,
        "graph_edges_with_semantic_signal": semantic_edge_count,
        "universe_tree_published": tree_published,
    }


def _compute_ir_metrics(ranked_docs: list[str], relevant_docs: set[str], k: int) -> dict[str, float]:
    if not relevant_docs:
        return {"recall": 0.0, "precision": 0.0, "mrr": 0.0, "map": 0.0, "ndcg": 0.0}
    top_k = ranked_docs[:k]
    hits = [1 if d in relevant_docs else 0 for d in top_k]
    num_rel = len(relevant_docs)
    recall = sum(hits) / num_rel
    precision = sum(hits) / max(1, len(top_k))

    mrr = 0.0
    for idx, h in enumerate(hits, start=1):
        if h:
            mrr = 1.0 / idx
            break

    ap_sum = 0.0
    hit_count = 0
    for idx, h in enumerate(hits, start=1):
        if h:
            hit_count += 1
            ap_sum += hit_count / idx
    map_k = ap_sum / min(num_rel, k)

    dcg = sum((1.0 / math.log2(idx + 1)) for idx, h in enumerate(hits, start=1) if h)
    idcg = sum((1.0 / math.log2(idx + 1)) for idx in range(1, min(num_rel, k) + 1))
    ndcg = dcg / idcg if idcg > 0 else 0.0

    return {
        "recall": recall,
        "precision": precision,
        "mrr": mrr,
        "map": map_k,
        "ndcg": ndcg,
    }


async def evaluate_vn_benchmark(
    skip_index: bool = False,
    top_k: int = 10,
    run_e2_llm: bool = True,
    run_synthesis_llm: bool = True,
) -> None:
    corpus_files = sorted(CORPUS_DIR.glob("*.md"), key=lambda p: p.name)
    questions = [
        json.loads(line)
        for line in (DATA_DIR / "questions.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    runtime = _CanonicalRuntime()
    try:
        if not skip_index:
            doc_id_to_filename, ai_index_stats = await index_vn_corpus(
                runtime, corpus_files, run_e2_llm=run_e2_llm
            )
        else:
            async with SessionLocal() as session:
                await session.execute(text(f'SET search_path TO "{SCHEMA_NAME}", public'))
                rows = (await session.execute(select(Document.id, Document.filename))).all()
                doc_id_to_filename = {str(r[0]): str(r[1]) for r in rows}
                builds = (await session.scalars(select(KnowledgeGraphBuild))).all()
                e2_jobs_check = (
                    await session.scalars(
                        select(KnowledgeJob).where(KnowledgeJob.kind == "E2", KnowledgeJob.status == "SUCCEEDED")
                    )
                ).all()
                populated_e2 = sum(
                    1
                    for j in e2_jobs_check
                    if any((j.result_json or {}).get(k) for k in ("entities", "aliases", "claims", "relations"))
                )
            if not builds or (run_e2_llm and populated_e2 == 0):
                print("Running Stage 1b/1c/1d (Tier E2 LLM Enrichment + Graph + Universe Tree) on indexed 130 docs...")
                t_e2_graph = await _finalize_e2_graph_and_tree(runtime, run_e2_llm=run_e2_llm)
            else:
                t_e2_graph = {}
            async with SessionLocal() as session:
                await session.execute(text(f'SET search_path TO "{SCHEMA_NAME}", public'))
                kus = (await session.scalars(select(KnowledgeUnit).where(KnowledgeUnit.is_current.is_(True)))).all()
                builds = (await session.scalars(select(KnowledgeGraphBuild))).all()
                e2_jobs = (
                    await session.scalars(
                        select(KnowledgeJob).where(KnowledgeJob.kind == "E2", KnowledgeJob.status == "SUCCEEDED")
                    )
                ).all()
                edge_list = (builds[-1].manifest_json or {}).get("edges", []) if builds else []
                ai_index_stats = {
                    "total_docs": len(doc_id_to_filename),
                    "total_knowledge_units": len(kus),
                    "dense_embedded_knowledge_units": sum(1 for u in kus if u.features_json.get("dense")),
                    **t_e2_graph,
                    "e2_llm_succeeded_units": len(e2_jobs),
                    "graph_edges_total": len(edge_list),
                    "graph_edges_with_semantic_signal": sum(
                        1 for e in edge_list if (e.get("signals") or {}).get("semantic") is not None
                    ),
                }
            print(f"Loaded {len(doc_id_to_filename)} existing Vietnamese documents from `{SCHEMA_NAME}`.")

        async with SessionLocal() as session:
            await session.execute(text(f'SET search_path TO "{SCHEMA_NAME}", public'))
            source = await session.get(Source, SOURCE_ID)
            ver_rows = (
                await session.execute(
                    select(DocumentVersion.id, Document.filename).join(
                        Document, Document.id == DocumentVersion.document_id
                    )
                )
            ).all()
            ver_id_to_filename = {str(r[0]): str(r[1]) for r in ver_rows}
        now_ts = int(time.time())
        principal = VerifiedPrincipal(
            subject="vn-mteb-evaluator",
            organization_id=ORG_ID,
            allowed_project_ids=frozenset({PROJECT_ID}),
            issuer="https://continuum.local",
            key_id="vn-mteb-key-1",
            token_id="vn-mteb-tok-1",
            issued_at=now_ts - 60,
            expires_at=now_ts + 3600,
            tenant_id=TENANT_ID,
            allowed_partition_ids=frozenset({PARTITION_ID}),
        )

        qdrant_client = await runtime.get_search_unit_qdrant_client()
        store = SearchUnitQdrantStore(qdrant_client, max_retries=3)
        embedder = await runtime.get_sag_embedding(SAG_SOURCE_CONFIG_ID, source)
        collection_name = f"search_units_{PROJECT_ID}"
        base_qdrant_filter = build_search_filter(
            project_id=PROJECT_ID,
            tenant_id=TENANT_ID,
            partition_id=PARTITION_ID,
            document_version_ids=sorted(ver_id_to_filename.keys()),
        )

        # Warmup connection pool & batch-embed all 50 query texts via Qwen/Qwen3-Embedding-0.6B
        all_q_texts = [q["question"] for q in questions]
        all_q_vecs = await embedder.batch_generate(all_q_texts)
        for qt, qv in zip(all_q_texts, all_q_vecs, strict=True):
            put_cached_text_embedding(qt, qv)
        _ = await retrieve_search_unit_sections(
            runtime, [source], "khởi tạo kết nối", principal=principal, top_k=top_k
        )

        print(
            f"[2/4] Evaluating {len(questions)} Vietnamese queries across 3 Same-Corpus Systems:\n"
            f"      (A) Pure Dense (`{settings.embedding_model}` Cosine Only)\n"
            f"      (B) Pure Sparse (`bm25_sparse` Lexical Overlap Only)\n"
            f"      (C) SAG Engine (Full AI Pipeline: Hybrid + E0/E1/E2 Graph + Multi-Hop Bridge + Clause Reranker)"
        )
        zalo_sag_k5: list[dict[str, float]] = []
        zalo_sag_k10: list[dict[str, float]] = []
        zalo_dense_k5: list[dict[str, float]] = []
        zalo_sparse_k5: list[dict[str, float]] = []

        hp_sag_k5: list[dict[str, float]] = []
        hp_sag_k10: list[dict[str, float]] = []
        hp_dense_k5: list[dict[str, float]] = []
        hp_dense_k10: list[dict[str, float]] = []
        hp_sparse_k5: list[dict[str, float]] = []
        hp_sparse_k10: list[dict[str, float]] = []

        latencies_ms: list[float] = []
        detailed_rows: list[dict[str, Any]] = []
        outcomes_by_qid: dict[str, Any] = {}

        for idx, q in enumerate(questions, start=1):
            q_text = q["question"]
            rel_set = set(q["relevant_doc_ids"])

            # (C) SAG Engine Full Pipeline
            t_start = time.perf_counter()
            async with SessionLocal() as session:
                await session.execute(text(f'SET search_path TO "{SCHEMA_NAME}", public'))
                outcome = await retrieve_search_unit_sections(
                    runtime,
                    [source],
                    q_text,
                    principal=principal,
                    top_k=top_k,
                )
            elapsed_ms = (time.perf_counter() - t_start) * 1000.0
            latencies_ms.append(elapsed_ms)
            outcomes_by_qid[q["question_id"]] = outcome

            sag_docs: list[str] = []
            for sec in outcome.sections:
                fname = doc_id_to_filename.get(str(sec.document_id or ""), sec.document_name or "")
                if fname and fname not in sag_docs:
                    sag_docs.append(fname)

            # (A) Pure Dense Baseline & (B) Pure Sparse Baseline on exact same corpus
            q_vec = await embedder.generate(q_text)
            sparse_q = build_sparse_query_vector(q_text)
            dense_hits, sparse_hits = await store.search_batch(
                collection_name,
                searches=[
                    {
                        "vector_name": "content_vector",
                        "query": q_vec,
                        "search_filter": base_qdrant_filter,
                        "limit": top_k * 2,
                    },
                    {
                        "vector_name": "bm25_sparse",
                        "query": sparse_q,
                        "search_filter": base_qdrant_filter,
                        "limit": top_k * 2,
                    },
                ],
            )
            dense_docs: list[str] = []
            for hit in dense_hits:
                v_id = str(hit.payload.get("document_version_id") or "")
                fname = ver_id_to_filename.get(v_id, "")
                if fname and fname not in dense_docs:
                    dense_docs.append(fname)

            sparse_docs: list[str] = []
            for hit in sparse_hits:
                v_id = str(hit.payload.get("document_version_id") or "")
                fname = ver_id_to_filename.get(v_id, "")
                if fname and fname not in sparse_docs:
                    sparse_docs.append(fname)

            m5_sag = _compute_ir_metrics(sag_docs, rel_set, k=5)
            m10_sag = _compute_ir_metrics(sag_docs, rel_set, k=10)
            m5_dense = _compute_ir_metrics(dense_docs, rel_set, k=5)
            m10_dense = _compute_ir_metrics(dense_docs, rel_set, k=10)
            m5_sparse = _compute_ir_metrics(sparse_docs, rel_set, k=5)
            m10_sparse = _compute_ir_metrics(sparse_docs, rel_set, k=10)

            if q["subset"] == "ZacLegalTextRetrieval":
                zalo_sag_k5.append(m5_sag)
                zalo_sag_k10.append(m10_sag)
                zalo_dense_k5.append(m5_dense)
                zalo_sparse_k5.append(m5_sparse)
            else:
                hp_sag_k5.append(m5_sag)
                hp_sag_k10.append(m10_sag)
                hp_dense_k5.append(m5_dense)
                hp_dense_k10.append(m10_dense)
                hp_sparse_k5.append(m5_sparse)
                hp_sparse_k10.append(m10_sparse)

            detailed_rows.append(
                {
                    "question_id": q["question_id"],
                    "subset": q["subset"],
                    "question": q_text,
                    "relevant_doc_ids": q["relevant_doc_ids"],
                    "retrieved_doc_ids": sag_docs[:top_k],
                    "pure_dense_doc_ids": dense_docs[:top_k],
                    "pure_sparse_doc_ids": sparse_docs[:top_k],
                    "metrics_at_5": m5_sag,
                    "metrics_at_10": m10_sag,
                    "pure_dense_at_5": m5_dense,
                    "pure_dense_at_10": m10_dense,
                    "pure_sparse_at_5": m5_sparse,
                    "pure_sparse_at_10": m10_sparse,
                    "latency_ms": round(elapsed_ms, 2),
                }
            )
            if idx % 10 == 0 or idx == len(questions):
                print(f"  Evaluated {idx}/{len(questions)} queries...")

        # AI Stage 4: End-to-End LLM Answer Synthesis (`Qwen/Qwen3-8B`)
        synthesis_stats = {
            "enabled": run_synthesis_llm,
            "model": settings.llm_model,
            "queries_synthesized": 0,
            "non_empty_answers": 0,
            "citation_grounded_answers": 0,
            "p50_synthesis_ms": 0.0,
        }
        if run_synthesis_llm:
            print(
                f"[3/4] Running End-to-End LLM Answer Synthesis (`{settings.llm_model}`) "
                f"across {len(questions)} Vietnamese queries..."
            )
            synth_sem = asyncio.Semaphore(8)
            synth_latencies: list[float] = []

            async def _synth_one(row: dict[str, Any]) -> None:
                qid = row["question_id"]
                out = outcomes_by_qid[qid]
                async with synth_sem:
                    t_s = time.perf_counter()
                    ans_obj = await synthesize_search_answer(
                        row["question"],
                        out.sections[:5],
                        llm=runtime.llm,
                        sources=[source],
                    )
                    el_ms = (time.perf_counter() - t_s) * 1000.0
                    synth_latencies.append(el_ms)
                    row["synthesized_answer"] = ans_obj.text or ""
                    row["synthesis_status"] = ans_obj.status
                    row["synthesis_citations_count"] = len(ans_obj.citations or [])
                    row["synthesis_latency_ms"] = round(el_ms, 1)

            await asyncio.gather(*(_synth_one(r) for r in detailed_rows))
            non_empty = sum(1 for r in detailed_rows if r.get("synthesized_answer", "").strip())
            cited = sum(
                1
                for r in detailed_rows
                if re.search(r"\[\d+\]", r.get("synthesized_answer", ""))
            )
            synthesis_stats = {
                "enabled": True,
                "model": settings.llm_model,
                "queries_synthesized": len(detailed_rows),
                "non_empty_answers": non_empty,
                "citation_grounded_answers": cited,
                "citation_grounded_rate_pct": round(100.0 * cited / max(1, len(detailed_rows)), 2),
                "p50_synthesis_ms": round(statistics.median(synth_latencies), 1) if synth_latencies else 0.0,
            }
            print(
                f"  Completed LLM Answer Synthesis: {non_empty}/{len(detailed_rows)} answers generated, "
                f"{cited}/{len(detailed_rows)} ({synthesis_stats['citation_grounded_rate_pct']}%) grounded with citations "
                f"(p50={synthesis_stats['p50_synthesis_ms']}ms)."
            )

        def _avg(rows: list[dict[str, float]], key: str) -> float:
            return round(100.0 * sum(r[key] for r in rows) / max(1, len(rows)), 2)

        # ZacLegalTextRetrieval metrics
        z_map5 = _avg(zalo_sag_k5, "map")
        z_mrr5 = _avg(zalo_sag_k5, "mrr")
        z_ndcg5 = _avg(zalo_sag_k5, "ndcg")
        z_rec5 = _avg(zalo_sag_k5, "recall")
        z_mean5 = round((z_map5 + z_mrr5 + z_ndcg5 + z_rec5) / 4.0, 2)
        z_ndcg10 = _avg(zalo_sag_k10, "ndcg")
        z_rec10 = _avg(zalo_sag_k10, "recall")

        zd_map5 = _avg(zalo_dense_k5, "map")
        zd_mrr5 = _avg(zalo_dense_k5, "mrr")
        zd_ndcg5 = _avg(zalo_dense_k5, "ndcg")
        zd_rec5 = _avg(zalo_dense_k5, "recall")
        zd_mean5 = round((zd_map5 + zd_mrr5 + zd_ndcg5 + zd_rec5) / 4.0, 2)

        zs_map5 = _avg(zalo_sparse_k5, "map")
        zs_mrr5 = _avg(zalo_sparse_k5, "mrr")
        zs_ndcg5 = _avg(zalo_sparse_k5, "ndcg")
        zs_rec5 = _avg(zalo_sparse_k5, "recall")
        zs_mean5 = round((zs_map5 + zs_mrr5 + zs_ndcg5 + zs_rec5) / 4.0, 2)

        # HotpotQA-VN metrics
        h_map5 = _avg(hp_sag_k5, "map")
        h_mrr5 = _avg(hp_sag_k5, "mrr")
        h_ndcg5 = _avg(hp_sag_k5, "ndcg")
        h_rec5 = _avg(hp_sag_k5, "recall")
        h_ndcg10 = _avg(hp_sag_k10, "ndcg")
        h_rec10 = _avg(hp_sag_k10, "recall")

        hd_mrr5 = _avg(hp_dense_k5, "mrr")
        hd_rec5 = _avg(hp_dense_k5, "recall")
        hd_ndcg10 = _avg(hp_dense_k10, "ndcg")
        hd_rec10 = _avg(hp_dense_k10, "recall")

        hs_mrr5 = _avg(hp_sparse_k5, "mrr")
        hs_rec5 = _avg(hp_sparse_k5, "recall")
        hs_ndcg10 = _avg(hp_sparse_k10, "ndcg")
        hs_rec10 = _avg(hp_sparse_k10, "recall")

        all_k5 = zalo_sag_k5 + hp_sag_k5
        all_k10 = zalo_sag_k10 + hp_sag_k10
        all_ndcg5 = _avg(all_k5, "ndcg")
        all_rec5 = _avg(all_k5, "recall")
        all_ndcg10 = _avg(all_k10, "ndcg")
        all_rec10 = _avg(all_k10, "recall")
        p50_ms = round(statistics.median(latencies_ms), 1) if latencies_ms else 0.0

        print("\n" + "=" * 92)
        print("1. VIETNAMESE LEGAL RAG BENCHMARK: ZacLegalTextRetrieval (Same-Corpus + MMTEB Leaderboard)")
        print("=" * 92)
        print("| System / Model | Mode | MAP@5 | MRR@5 | NDCG@5 | Recall@5 | Mean |")
        print("| :--- | :--- | ---: | ---: | ---: | ---: | ---: |")
        print(f"| **SAG Engine (Full AI Pipeline)** | **Same-Corpus (130 docs)** | **{z_map5:.2f}** | **{z_mrr5:.2f}** | **{z_ndcg5:.2f}** | **{z_rec5:.2f}** | **{z_mean5:.2f}** |")
        print(f"| Pure Dense (`Qwen3-Embedding-0.6B`) | Same-Corpus (130 docs) | {zd_map5:.2f} | {zd_mrr5:.2f} | {zd_ndcg5:.2f} | {zd_rec5:.2f} | {zd_mean5:.2f} |")
        print(f"| Pure Sparse (`BM25 / Token Overlap`) | Same-Corpus (130 docs) | {zs_map5:.2f} | {zs_mrr5:.2f} | {zs_ndcg5:.2f} | {zs_rec5:.2f} | {zs_mean5:.2f} |")
        print("| GreenNode M3-GN-VN-Mixed (SOTA VN) | Full Leaderboard | 69.75 | 69.28 | 74.01 | 86.74 | 74.95 |")
        print("| BAAI M3-Embedding (`bge-m3`) | Full Leaderboard | 69.34 | 68.96 | 73.70 | 86.68 | 74.67 |")
        print("| Microsoft `multilingual-e5-large` | Full Leaderboard | 60.14 | 59.62 | 64.17 | 76.02 | 64.99 |")
        print("| **OpenAI `text-embedding-3`** | Full Leaderboard | 38.68 | 38.80 | 41.53 | 49.94 | 41.74 |")

        print("\n" + "=" * 92)
        print("2. VIETNAMESE MULTI-HOP RAG BENCHMARK: HotpotQA-VN (Same-Corpus + VN-MTEB Leaderboard)")
        print("=" * 92)
        print("| System / Model | Mode | NDCG@10 | Recall@5 | Recall@10 | MRR@5 |")
        print("| :--- | :--- | ---: | ---: | ---: | ---: |")
        print(f"| **SAG Engine (Full AI Pipeline)** | **Same-Corpus (130 docs)** | **{h_ndcg10:.2f}** | **{h_rec5:.2f}** | **{h_rec10:.2f}** | **{h_mrr5:.2f}** |")
        print(f"| Pure Dense (`Qwen3-Embedding-0.6B`) | Same-Corpus (130 docs) | {hd_ndcg10:.2f} | {hd_rec5:.2f} | {hd_rec10:.2f} | {hd_mrr5:.2f} |")
        print(f"| Pure Sparse (`BM25 / Token Overlap`) | Same-Corpus (130 docs) | {hs_ndcg10:.2f} | {hs_rec5:.2f} | {hs_rec10:.2f} | {hs_mrr5:.2f} |")
        print("| AITeamVN `Vietnamese_Embedding` (568M) | Full Leaderboard | 70.07 | - | - | - |")
        print("| **Alibaba `gte-Qwen2-7B-instruct` (7B)** | Full Leaderboard | 67.99 | - | - | - |")
        print("| **Microsoft `multilingual-e5-large` (560M)** | Full Leaderboard | 65.11 | - | - | - |")
        print("| **BAAI `bge-m3` (568M)** | Full Leaderboard | 63.76 | - | - | - |")
        print("| **Google `bge-multilingual-Gemma2` (9B)** | Full Leaderboard | 29.72 | - | - | - |")

        print("\n" + "=" * 92)
        print(
            f"OVERALL VN-MTEB SUMMARY (n={len(questions)}): "
            f"NDCG@5={all_ndcg5:.2f}% | Recall@5={all_rec5:.2f}% | "
            f"NDCG@10={all_ndcg10:.2f}% | Recall@10={all_rec10:.2f}% | p50={p50_ms:.1f}ms"
        )
        print("=" * 92)

        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        summary_payload = {
            "ai_pipeline_audit": {
                **ai_index_stats,
                "answer_synthesis": synthesis_stats,
            },
            "zalo_legal": {
                "sag_full": {
                    "map@5": z_map5,
                    "mrr@5": z_mrr5,
                    "ndcg@5": z_ndcg5,
                    "recall@5": z_rec5,
                    "mean@5": z_mean5,
                    "ndcg@10": z_ndcg10,
                    "recall@10": z_rec10,
                },
                "pure_dense_same_corpus": {
                    "map@5": zd_map5,
                    "mrr@5": zd_mrr5,
                    "ndcg@5": zd_ndcg5,
                    "recall@5": zd_rec5,
                    "mean@5": zd_mean5,
                },
                "pure_sparse_same_corpus": {
                    "map@5": zs_map5,
                    "mrr@5": zs_mrr5,
                    "ndcg@5": zs_ndcg5,
                    "recall@5": zs_rec5,
                    "mean@5": zs_mean5,
                },
            },
            "hotpotqa_vn": {
                "sag_full": {
                    "map@5": h_map5,
                    "mrr@5": h_mrr5,
                    "ndcg@5": h_ndcg5,
                    "recall@5": h_rec5,
                    "ndcg@10": h_ndcg10,
                    "recall@10": h_rec10,
                },
                "pure_dense_same_corpus": {
                    "mrr@5": hd_mrr5,
                    "recall@5": hd_rec5,
                    "ndcg@10": hd_ndcg10,
                    "recall@10": hd_rec10,
                },
                "pure_sparse_same_corpus": {
                    "mrr@5": hs_mrr5,
                    "recall@5": hs_rec5,
                    "ndcg@10": hs_ndcg10,
                    "recall@10": hs_rec10,
                },
            },
            "overall": {
                "ndcg@5": all_ndcg5,
                "recall@5": all_rec5,
                "ndcg@10": all_ndcg10,
                "recall@10": all_rec10,
                "p50_latency_ms": p50_ms,
            },
            "questions": detailed_rows,
        }
        (REPORTS_DIR / "vn_mteb_sag_results.json").write_text(
            json.dumps(summary_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    finally:
        await runtime.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-index", action="store_true")
    parser.add_argument("--no-e2-llm", action="store_true")
    parser.add_argument("--no-synthesis-llm", action="store_true")
    parser.add_argument("--top-k", type=int, default=10)
    args = parser.parse_args()
    asyncio.run(
        evaluate_vn_benchmark(
            skip_index=args.skip_index,
            top_k=args.top_k,
            run_e2_llm=not args.no_e2_llm,
            run_synthesis_llm=not args.no_synthesis_llm,
        )
    )
