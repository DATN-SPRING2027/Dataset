"""Run RetrievalCI Bench-v0 (2026) against SAG Engine (Mode A: Retrieve-Only & Full Diagnostics).

Indexes the 81 EnterpriseRAG-Bench stratified documents in `examples/rag_eval/bench_v0/corpus/*.md`
into an isolated PostgreSQL schema (`sag_retrievalci_bench_v0`) and Qdrant collection
(`search_units_670000000000000000000201`), then evaluates all 50 held-out questions in
`examples/rag_eval/bench_v0/questions.jsonl` and compares against the Big Tech hosted RAG
baselines (`vertex_ai_rag`, `bedrock_kb`, `openai_file_search`, `azure_ai_search`).
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import statistics
import sys
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

# Configure paths before importing sag_api
BENCH_ROOT = Path(r"d:\DoAnTotnghiep\Dataset\RetrievalCI_Bench_v0_2026")
SAG_ROOT = Path(r"d:\DoAnTotnghiep\sag-laya-integration\SAG")
SAG_API_ROOT = SAG_ROOT / "apps" / "api"

os.chdir(SAG_ROOT)
if str(SAG_API_ROOT) not in sys.path:
    sys.path.insert(0, str(SAG_API_ROOT))
if str(BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(BENCH_ROOT))

from sag_api.core.config import settings

SCHEMA_NAME = "sag_retrievalci_bench_v0"
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
    Source,
    SourceProjectMapping,
)
from sag_api.enums import (
    ConnectorKind,
    DocumentStatus,
    SourceStatus,
    SourceType,
)
from sag_api.services.canonical_service import parse_and_persist_document_content
from sag_api.services.knowledge_service import persist_graph, rebuild_knowledge_version
from sag_api.services.search_index_service import (
    ensure_qdrant_collection_and_indexes,
    run_search_indexing_stage,
)
from sag_api.services.search_unit_retrieval_service import (
    SearchableSource,
    retrieve_search_unit_sections,
)


class _SiliconFlowEmbedder:
    def __init__(self, client: httpx.AsyncClient, model: str, dimensions: int | None = None) -> None:
        self._client = client
        self._model = model
        self._dimensions = dimensions

    async def batch_generate(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        out: list[list[float]] = []
        batch_size = 32
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            payload: dict[str, Any] = {"model": self._model, "input": batch}
            if self._dimensions:
                payload["dimensions"] = self._dimensions
            res = await self._client.post("/embeddings", json=payload)
            res.raise_for_status()
            data = sorted(res.json()["data"], key=lambda item: item["index"])
            out.extend([float(v) for v in item["embedding"]] for item in data)
        return out

    async def generate(self, text_input: str) -> list[float]:
        vecs = await self.batch_generate([text_input])
        return vecs[0]


class _CanonicalRuntime:
    """Lightweight engine_manager replacement for Phase 2C canonical search & indexing."""

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

    async def get_search_unit_qdrant_client(self) -> httpx.AsyncClient:
        return self._qdrant

    async def get_sag_embedding(self, source_config_id: str, source: Any = None) -> _SiliconFlowEmbedder:
        return self._embedder

    async def shutdown(self) -> None:
        await self._qdrant.aclose()
        await self._embed_http.aclose()

from retrievalci.rag_eval.metrics import _aligned_metric_values, compute_row, paired_bootstrap_ci
from retrievalci.rag_eval.runner import _aggregate, load_questions
from retrievalci.rag_eval.types import (
    Citation,
    ComparisonReport,
    PairwiseDelta,
    QAItem,
    RunResult,
    SystemAnswer,
)
from retrievalci.reporting import render_scorecard_markdown, write_html_report

PROJECT_ID = "670000000000000000000201"
SOURCE_ID = "670000000000000000000202"
MAPPING_ID = "670000000000000000000203"
SAG_SOURCE_CONFIG_ID = "scfg-retrievalci-bench-v0"
ORG_ID = "org-retrievalci-v0"
TENANT_ID = "tenant-retrievalci-v0"
PARTITION_ID = "part-retrievalci-v0"


def _compute_corpus_hash(corpus_files: list[Path]) -> str:
    h = hashlib.sha256()
    for p in sorted(corpus_files, key=lambda x: x.name):
        rel = p.relative_to(BENCH_ROOT).as_posix()
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(p.read_bytes())
        h.update(b"\0")
    return h.hexdigest()


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


async def index_bench_v0_corpus(
    engine_manager: EngineManager,
    corpus_dir: Path,
) -> dict[str, str]:
    """Index all 81 Markdown files from bench_v0 into SAG canonical pipeline."""
    t0 = time.perf_counter()
    print(f"[1/3] Resetting schema `{SCHEMA_NAME}` and Qdrant collection for project `{PROJECT_ID}`...")
    await _init_schema(reset=True)
    qdrant_client = await engine_manager.get_search_unit_qdrant_client()
    await qdrant_client.delete(f"/collections/search_units_{PROJECT_ID}")

    corpus_files = sorted(corpus_dir.glob("*.md"))
    print(f"Found {len(corpus_files)} Markdown documents in {corpus_dir}")

    now = datetime.now(UTC)
    started_at = now - timedelta(minutes=5)
    doc_id_to_rel_path: dict[str, str] = {}
    ver_ids: list[tuple[str, str, str]] = []  # (doc_id, ver_id, run_id)

    async with SessionLocal() as session:
        await session.execute(text(f'SET search_path TO "{SCHEMA_NAME}", public'))
        source = Source(
            id=SOURCE_ID,
            name="EnterpriseRAG-Bench Corpus",
            description="81 stratified EnterpriseRAG-Bench v1.0.0 documents across 9 sources",
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
            confirmed_by="bench-admin",
            approval_ref="retrievalci-bench-v0",
        )
        session.add_all([source, mapping])
        await session.flush()

        for idx, file_path in enumerate(corpus_files, start=1):
            rel_path = file_path.relative_to(BENCH_ROOT).as_posix()
            raw_text = file_path.read_text(encoding="utf-8")
            title = _extract_title(raw_text, file_path.stem)
            checksum = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
            byte_len = len(raw_text.encode("utf-8"))

            doc_id = f"67000000000000000020{idx:04d}"
            ver_id = f"67000000000000000021{idx:04d}"
            run_id = f"67000000000000000022{idx:04d}"

            doc = Document(
                id=doc_id,
                tenant_id=TENANT_ID,
                project_id=PROJECT_ID,
                source_id=SOURCE_ID,
                filename=rel_path,
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
                    "rel_path": rel_path,
                },
            )
            run = IngestionRun(
                id=run_id,
                tenant_id=TENANT_ID,
                project_id=PROJECT_ID,
                document_version_id=ver_id,
                idempotency_key=f"idem-bench-v0-{idx:04d}",
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
            doc_id_to_rel_path[doc_id] = rel_path
            ver_ids.append((doc_id, ver_id, run_id))

        await session.commit()

    print(f"Parsed canonical blocks for {len(ver_ids)} documents in {time.perf_counter() - t0:.1f}s.")

    # Ensure Qdrant collection and payload indexes exist
    async with SessionLocal() as session:
        await session.execute(text(f'SET search_path TO "{SCHEMA_NAME}", public'))
        source_obj = await session.get(Source, SOURCE_ID)
    embedder = await engine_manager.get_sag_embedding(SAG_SOURCE_CONFIG_ID, source_obj)
    sample_vec = await embedder.generate("dimension probe")
    await ensure_qdrant_collection_and_indexes(
        qdrant_client,
        f"search_units_{PROJECT_ID}",
        vector_dim=len(sample_vec),
    )

    # Index search units and build knowledge units
    t_idx = time.perf_counter()
    all_knowledge_units = []
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
            kus = await rebuild_knowledge_version(session, ver_id)
            all_knowledge_units.extend(kus)
            if i % 10 == 0 or i == len(ver_ids):
                await session.commit()
                print(
                    f"  Indexed {i}/{len(ver_ids)} docs "
                    f"({time.perf_counter() - t_idx:.1f}s elapsed)..."
                )

        print(f"Persisting KnowledgeUnit graph edges across {len(all_knowledge_units)} KUs...")
        build = await persist_graph(session, all_knowledge_units)
        await session.commit()
        edge_count = len((build.manifest_json or {}).get("edges", []))
        print(
            f"Completed indexing 81 docs ({len(all_knowledge_units)} KUs, {edge_count} edges) "
            f"in {time.perf_counter() - t0:.1f}s."
        )

    return doc_id_to_rel_path


async def load_doc_id_to_rel_path() -> dict[str, str]:
    async with SessionLocal() as session:
        await session.execute(text(f'SET search_path TO "{SCHEMA_NAME}", public'))
        rows = (await session.execute(select(Document.id, Document.filename))).all()
        return {r[0]: r[1] for r in rows}


async def evaluate_sag_on_bench_v0(
    engine_manager: EngineManager,
    questions: list[QAItem],
    doc_id_to_rel_path: dict[str, str],
    corpus_hash: str,
    top_k: int = 5,
) -> tuple[list[RunResult], dict[str, dict[str, Any]]]:
    async with SessionLocal() as session:
        await session.execute(text(f'SET search_path TO "{SCHEMA_NAME}", public'))
        source = await session.get(Source, SOURCE_ID)
    now_ts = int(time.time())
    principal = VerifiedPrincipal(
        subject="bench-evaluator",
        organization_id=ORG_ID,
        allowed_project_ids=frozenset({PROJECT_ID}),
        issuer="https://continuum.local",
        key_id="bench-key-1",
        token_id="bench-tok-1",
        issued_at=now_ts - 60,
        expires_at=now_ts + 3600,
        tenant_id=TENANT_ID,
        allowed_partition_ids=frozenset({PARTITION_ID}),
    )

    # Warmup connection pool / embedder
    _ = await retrieve_search_unit_sections(
        engine_manager, [source], "warmup query", principal=principal, top_k=top_k
    )

    sag_rows: list[RunResult] = []
    diagnostics_by_qid: dict[str, dict[str, Any]] = {}

    print(f"[2/3] Running {len(questions)} RetrievalCI Bench-v0 questions (top_k={top_k})...")
    for idx, q in enumerate(questions, start=1):
        t0 = time.perf_counter()
        outcome = await retrieve_search_unit_sections(
            engine_manager,
            [source],
            q.question,
            principal=principal,
            top_k=top_k,
        )
        latency_ms = (time.perf_counter() - t0) * 1000.0

        citations: list[Citation] = []
        section_debug: list[dict[str, Any]] = []
        for s in outcome.sections:
            rel_path = doc_id_to_rel_path.get(s.document_id or "", s.document_name or "")
            span_preview = (s.content or "")[:180]
            citations.append(Citation(source_path=rel_path, span=span_preview))
            section_debug.append(
                {
                    "source_path": rel_path,
                    "score": round(float(s.score or 0.0), 4),
                    "heading": s.heading,
                    "search_unit_id": s.search_unit_id,
                    "span_preview": span_preview[:120],
                }
            )

        refused = len(citations) == 0
        ans = SystemAnswer(
            answer="",
            citations=(),
            latency_ms=latency_ms,
            retrieval_latency_ms=latency_ms,
            tokens_used=0,
            refused=refused,
            refusal_reason="low_retrieval_confidence" if refused else None,
            retrieved_sources=tuple(citations),
            answer_citations=(),
            cost_usd=0.0001,
            corpus_version_hash=corpus_hash,
            index_build_id=f"sag://{SCHEMA_NAME}/{PROJECT_ID}",
            generator_model_id="sag-engine-retrieve-only",
            meta={
                "sag_top_k": top_k,
                "coverage_status": outcome.stats.get("coverage", {}).get("status"),
                "stage_latencies_ms": outcome.stats.get("stage_latencies_ms", {}),
            },
        )
        row = compute_row("sag_engine", q, ans)
        sag_rows.append(row)
        diagnostics_by_qid[q.id] = {
            "question_id": q.id,
            "tier": q.tier,
            "unanswerable": q.unanswerable,
            "expected_abstain": q.expected_abstain,
            "question": q.question,
            "ground_truth_citations": list(q.ground_truth_citations),
            "distractor_citations": list(q.distractor_citations),
            "retrieved_unique_docs": list(dict.fromkeys(c.source_path for c in citations)),
            "retrieval_source_recall": row.retrieval_source_recall,
            "retrieval_source_precision": row.retrieval_source_precision,
            "abstention_correctness": row.abstention_correctness,
            "latency_ms": round(latency_ms, 2),
            "sections": section_debug,
            "stats": {
                "semantic_candidates": outcome.stats.get("semantic_candidates"),
                "lexical_candidates": outcome.stats.get("lexical_candidates"),
                "coverage": outcome.stats.get("coverage"),
                "routing": outcome.stats.get("routing"),
                "stage_latencies_ms": outcome.stats.get("stage_latencies_ms"),
            },
        }
        if idx % 10 == 0 or idx == len(questions):
            print(f"  Evaluated {idx}/{len(questions)} questions...")

    return sag_rows, diagnostics_by_qid


def merge_and_save_reports(
    questions: list[QAItem],
    sag_rows: list[RunResult],
    diagnostics_by_qid: dict[str, dict[str, Any]],
) -> ComparisonReport:
    merged_baseline_path = BENCH_ROOT / "baselines" / "rag" / "bench_v0_merged.json"
    merged_base = ComparisonReport.model_validate_json(
        merged_baseline_path.read_text(encoding="utf-8")
    )

    other_rows = [r for r in merged_base.rows if r.system != "sag_engine"]
    all_rows = sag_rows + other_rows
    all_systems = ("sag_engine", *[s for s in merged_base.systems if s != "sag_engine"])

    by_sys_metric, by_sys_tier_metric = _aggregate(all_rows)

    question_ids = [q.id for q in questions]
    pairwise: list[PairwiseDelta] = []
    for metric in ("retrieval_source_recall", "retrieval_source_precision"):
        for i, sys_a in enumerate(all_systems):
            for sys_b in all_systems[i + 1 :]:
                a_vals = _aligned_metric_values(all_rows, sys_a, metric, question_ids)
                b_vals = _aligned_metric_values(all_rows, sys_b, metric, question_ids)
                if a_vals is None or b_vals is None or not a_vals:
                    continue
                mean_a = statistics.fmean(a_vals)
                mean_b = statistics.fmean(b_vals)
                ci_low, ci_high = paired_bootstrap_ci(
                    a_vals, b_vals, n_resamples=2000, alpha=0.05
                )
                pairwise.append(
                    PairwiseDelta(
                        metric=metric,
                        system_a=sys_a,
                        system_b=sys_b,
                        mean_a=mean_a,
                        mean_b=mean_b,
                        mean_diff=mean_a - mean_b,
                        ci_low=ci_low,
                        ci_high=ci_high,
                        alpha=0.05,
                        n=len(a_vals),
                        significant=(ci_low > 0) or (ci_high < 0),
                    )
                )

    combined_report = ComparisonReport(
        systems=all_systems,
        n_questions=merged_base.n_questions,
        n_per_tier=merged_base.n_per_tier,
        rows=all_rows,
        by_system_metric=by_sys_metric,
        by_system_tier_metric=by_sys_tier_metric,
        pairwise=pairwise,
    )

    out_json = BENCH_ROOT / "baselines" / "rag" / "bench_v0_with_sag.json"
    out_html = BENCH_ROOT / "baselines" / "rag" / "bench_v0_with_sag.html"
    out_diag = BENCH_ROOT / "baselines" / "rag" / "bench_v0_sag_diagnostics.json"

    out_json.write_text(combined_report.model_dump_json(indent=2), encoding="utf-8")
    write_html_report(
        out_html,
        title="RetrievalCI Bench-v0 (2026) — SAG Engine vs Big Tech Hosted RAG",
        rag_report=combined_report,
        primary_metric="retrieval_source_recall",
    )
    out_diag.write_text(json.dumps(diagnostics_by_qid, indent=2), encoding="utf-8")

    print("\n" + "=" * 80)
    print("RETRIEVALCI BENCH-V0 (2026) OFFICIAL SCORECARD")
    print("=" * 80)
    print(render_scorecard_markdown(combined_report))

    hosted_and_sag = (
        "sag_engine",
        "azure_ai_search",
        "vertex_ai_rag",
        "bedrock_kb",
        "openai_file_search",
    )
    print("\n--- Per-Tier Recall / Precision Breakdown ---")
    for sys_name in hosted_and_sag:
        m = combined_report.by_system_metric.get(sys_name, {})
        rec = m.get("retrieval_source_recall", 0.0)
        prec = m.get("retrieval_source_precision", 0.0)
        score = 100.0 * (0.7 * rec + 0.3 * prec)
        abs_corr = m.get("abstention_correctness", 0.0)
        t_metrics = combined_report.by_system_tier_metric.get(sys_name, {})
        sh_r = t_metrics.get("single_hop", {}).get("retrieval_source_recall", 0.0)
        sh_p = t_metrics.get("single_hop", {}).get("retrieval_source_precision", 0.0)
        mh_r = t_metrics.get("multi_hop", {}).get("retrieval_source_recall", 0.0)
        mh_p = t_metrics.get("multi_hop", {}).get("retrieval_source_precision", 0.0)
        ct_r = t_metrics.get("contradiction", {}).get("retrieval_source_recall", 0.0)
        ct_p = t_metrics.get("contradiction", {}).get("retrieval_source_precision", 0.0)
        print(
            f"{sys_name:20s} | Score={score:5.1f} | R={rec*100:5.1f}% P={prec*100:5.1f}% Abs={abs_corr*100:5.1f}% "
            f"| SH(R={sh_r*100:5.1f}%,P={sh_p*100:5.1f}%) "
            f"| MH(R={mh_r*100:5.1f}%,P={mh_p*100:5.1f}%) "
            f"| CT(R={ct_r*100:5.1f}%,P={ct_p*100:5.1f}%)"
        )

    print("\n--- SAG Engine Question-Level Bottleneck Audit ---")
    missed_recall = []
    low_precision = []
    unanswerable_audit = []
    for q in questions:
        d = diagnostics_by_qid[q.id]
        if q.unanswerable or q.expected_abstain:
            unanswerable_audit.append(d)
        else:
            if (d["retrieval_source_recall"] or 0.0) < 1.0:
                missed_recall.append(d)
            if (d["retrieval_source_precision"] or 0.0) < 0.5:
                low_precision.append(d)

    print(f"Answerable questions with Recall < 1.0: {len(missed_recall)} / 45")
    for d in missed_recall:
        truth_set = set(d["ground_truth_citations"])
        got_set = set(d["retrieved_unique_docs"])
        missing = sorted(truth_set - got_set)
        print(
            f"  - {d['question_id']} ({d['tier']}): Recall={d['retrieval_source_recall']:.3f}, "
            f"Precision={d['retrieval_source_precision']:.3f} | Missing={len(missing)}: "
            f"{[Path(m).name for m in missing]}"
        )
    print(f"Unanswerable questions (n={len(unanswerable_audit)}):")
    for d in unanswerable_audit:
        print(
            f"  - {d['question_id']}: abstention_correctness={d['abstention_correctness']}, "
            f"precision={d['retrieval_source_precision']}, retrieved_docs={len(d['retrieved_unique_docs'])}"
        )

    return combined_report


async def async_main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-index", action="store_true", help="Reuse existing indexed schema & Qdrant collection")
    parser.add_argument("--top-k", type=int, default=5, help="Top-K chunks to retrieve (default: 5, matching hosted baselines)")
    args = parser.parse_args()

    corpus_dir = BENCH_ROOT / "examples" / "rag_eval" / "bench_v0" / "corpus"
    questions_path = BENCH_ROOT / "examples" / "rag_eval" / "bench_v0" / "questions.jsonl"
    corpus_files = sorted(corpus_dir.glob("*.md"))
    corpus_hash = _compute_corpus_hash(corpus_files)
    questions = load_questions(questions_path)

    engine_manager = _CanonicalRuntime()
    try:
        if args.skip_index:
            doc_id_to_rel_path = await load_doc_id_to_rel_path()
            print(f"Loaded {len(doc_id_to_rel_path)} existing documents from `{SCHEMA_NAME}`.")
        else:
            doc_id_to_rel_path = await index_bench_v0_corpus(engine_manager, corpus_dir)

        sag_rows, diagnostics_by_qid = await evaluate_sag_on_bench_v0(
            engine_manager, questions, doc_id_to_rel_path, corpus_hash, top_k=args.top_k
        )
        merge_and_save_reports(questions, sag_rows, diagnostics_by_qid)
    finally:
        if hasattr(engine_manager, "shutdown"):
            await engine_manager.shutdown()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(async_main())
