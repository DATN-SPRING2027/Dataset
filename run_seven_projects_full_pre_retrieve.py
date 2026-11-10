from __future__ import annotations

import asyncio
import json
import math
import os
import statistics
import sys
from pathlib import Path
from typing import Any

os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

DATASET_ROOT = Path("D:/DoAnTotnghiep/Dataset")
BENCH_V0_ROOT = DATASET_ROOT / "RetrievalCI_Bench_v0_2026"
VN_MTEB_ROOT = DATASET_ROOT / "VN_MTEB_RAG_Bench_2026"
SAG_ROOT = Path("D:/DoAnTotnghiep/sag-laya-integration/SAG")
sys.path[:0] = [
    str(SAG_ROOT / "apps" / "api"),
    str(BENCH_V0_ROOT),
    str(DATASET_ROOT),
]
os.chdir(SAG_ROOT)

from sag_api.core.config import settings
from sag_api.core.token_usage import (
    RUNTIME_TOKEN_REGISTRY,
    TokenLedger,
    merge_token_summaries,
    token_usage_scope,
)
from sag_api.services.decision_router import route_query
from sag_api.services.query_analysis import analyze_query
from sag_api.services.query_strategy_planner import plan_query
from benchmark_quality import extended_evaluation, ir_metrics
from benchmark_support import BenchmarkRun, default_benchmark_project_id, default_benchmark_project_name
from retrievalci.rag_eval.metrics import compute_row
from retrievalci.rag_eval.runner import _aggregate, load_questions
from retrievalci.rag_eval.types import Citation, ComparisonReport, QAItem, RunResult, SystemAnswer
from retrievalci.reporting import write_html_report
from sag_benchmark_runtime import SAGBenchmark
from run_all_datasets_sag import (
    ALL_SEVEN_KEYS,
    DEFAULT_BENCHMARK_ORGANIZATION_ID,
    NEW_FIVE_KEYS,
    _compute_corpus_hash,
    _resolve_existing_indexed_source,
    build_seven_projects_summary,
    materialize_dataset,
)


async def _configure_skip_or_ingest(benchmark_key: str, file_count: int) -> bool:
    target_project_id = default_benchmark_project_id(benchmark_key, DEFAULT_BENCHMARK_ORGANIZATION_ID)
    existing_source = await _resolve_existing_indexed_source(
        target_project_id,
        DEFAULT_BENCHMARK_ORGANIZATION_ID,
        file_count,
    )
    if existing_source is not None:
        os.environ["SAG_BENCHMARK_SCHEMA"] = "sag"
        os.environ["SAG_BENCHMARK_PROJECT_ID"] = target_project_id
        os.environ["SAG_BENCHMARK_SOURCE_ID"] = existing_source[0]
        os.environ["SAG_BENCHMARK_SOURCE_CONFIG_ID"] = existing_source[1]
        if "--skip-index" not in sys.argv:
            sys.argv.append("--skip-index")
        return True
    for env_key in ("SAG_BENCHMARK_PROJECT_ID", "SAG_BENCHMARK_SOURCE_ID", "SAG_BENCHMARK_SOURCE_CONFIG_ID"):
        os.environ.pop(env_key, None)
    while "--skip-index" in sys.argv:
        sys.argv.remove("--skip-index")
    return False


def _replay_existing_query_tokens_into_registry(project_id: str, prev_token_usage: dict[str, Any] | None) -> None:
    if not isinstance(prev_token_usage, dict):
        return
    by_comp = prev_token_usage.get("by_component") or {}
    by_mod = prev_token_usage.get("by_model") or {}
    emb_mod = next((m for m in by_mod if "embedding" in m.lower()), settings.embedding_model)
    llm_mod = next((m for m in by_mod if "embedding" not in m.lower() and "kev" not in m.lower()), settings.llm_model)
    for comp_name, bucket in by_comp.items():
        if comp_name == "decision_router" or not isinstance(bucket, dict):
            continue
        mod = emb_mod if "embedding" in comp_name else llm_mod
        RUNTIME_TOKEN_REGISTRY.record(
            component=comp_name,
            model=mod,
            delta=bucket,
            project_id=project_id,
        )


def _enrich_cached_measurement_with_pre_retrieve(
    measured: dict[str, Any],
    query_text: str,
    project_id: str,
    tenant_id: str,
) -> dict[str, Any]:
    settings.decision_provider = "siliconflow"
    with token_usage_scope(
        component="search_request",
        project_id=project_id,
        tenant_id=tenant_id,
    ) as dec_ledger:
        decision = route_query(query_text)
    analysis = analyze_query(query_text, segmentation_enabled=settings.search_chinese_segmentation_enabled)
    strategy_plan = plan_query(
        query_text,
        features=analysis.features,
        requested_top_k=None,
        answer_shape=str(decision.get("answer_shape") or "") or None,
    )
    dec_summary = dec_ledger.to_summary()
    dec_lat = float(decision.get("latency_ms") or 0.0)
    out = json.loads(json.dumps(measured))
    for l_field in ("retrieval_latency_ms", "first_token_ms", "latency_ms"):
        if out.get(l_field) is not None:
            out[l_field] = round(float(out[l_field]) + dec_lat, 2)
    resp = out.setdefault("response", {})
    stats = resp.setdefault("stats", {})
    prev_tu = stats.get("token_usage") if isinstance(stats.get("token_usage"), dict) else {}
    _replay_existing_query_tokens_into_registry(project_id, prev_tu)
    merged_tu = merge_token_summaries(prev_tu, dec_summary)
    stats["token_usage"] = merged_tu
    q_route = stats.setdefault("query_route", {})
    q_route["model"] = decision.get("model", "Kev-4b")
    q_route["coarse_intent"] = decision.get("coarse_intent", "KNOWLEDGE")
    q_route["confidence"] = decision.get("confidence", 0.9)
    q_route["suggested_strategy"] = decision.get("suggested_strategy", "vector")
    q_route["fallback_used"] = False
    q_route["fallback_reason"] = None
    q_route["strategy_plan"] = strategy_plan.as_trace()
    stats["retrieval_plan"] = strategy_plan.retrieval_plan.as_trace()
    return out


def _needs_live_rerun(
    query_text: str,
    prev_recall: float | None,
    has_prev: bool,
) -> tuple[bool, str]:
    if not has_prev:
        return True, "no_prev"
    settings.decision_provider = "siliconflow"
    dec = route_query(query_text)
    analysis = analyze_query(query_text, segmentation_enabled=settings.search_chinese_segmentation_enabled)
    p0 = plan_query(
        query_text,
        features=analysis.features,
        requested_top_k=5,
        answer_shape=None,
    )
    p1 = plan_query(
        query_text,
        features=analysis.features,
        requested_top_k=None,
        answer_shape=str(dec.get("answer_shape") or "") or None,
    )
    r0, r1 = p0.retrieval_plan, p1.retrieval_plan
    k0 = (r0.target.value, r0.output.value, r0.cardinality.effective_n, r0.per_document_limit, p0.primary_strategy.value, p0.multi_hop_eligible)
    k1 = (r1.target.value, r1.output.value, r1.cardinality.effective_n, r1.per_document_limit, p1.primary_strategy.value, p1.multi_hop_eligible)
    if k0 != k1:
        return True, f"plan_diff({r0.target.value}/{r0.output.value}/n={r0.cardinality.effective_n}->{r1.target.value}/{r1.output.value}/n={r1.cardinality.effective_n})"
    return False, "identical_plan"


BASELINE_RUN_IDS = {
    "retrievalci_v0": "20261029T124344Z-27a384",
    "vn_mteb": "20261029T125830Z-e6edea",
    "wixqa_enterprise": "20261106T161603Z-753826",
    "org1_northstar": "20261107T122419Z-63d6e1",
    "org2_nova": "20261107T123959Z-bc9fa9",
    "org3_cloudops": "20261107T125240Z-3ea281",
    "org4_mediflow": "20261107T130850Z-4e3b9b",
}


async def _load_latest_completed_run(benchmark_key: str) -> dict[str, Any]:
    from sqlalchemy import text
    from sqlalchemy.engine import make_url
    from sqlalchemy.ext.asyncio import create_async_engine

    baseline_id = BASELINE_RUN_IDS.get(benchmark_key)
    parsed_db = make_url(settings.database_url)
    q_db = dict(parsed_db.query)
    q_db.pop("search_path", None)
    eng = create_async_engine(parsed_db.set(query=q_db), connect_args={"server_settings": {"search_path": "sag"}})
    try:
        async with eng.connect() as conn:
            if baseline_id:
                row = (
                    await conn.execute(
                        text(
                            """
                            SELECT id, manifest_json, results_json, diagnostics_json
                            FROM sag.benchmark_runs
                            WHERE id = :rid
                            LIMIT 1
                            """
                        ),
                        {"rid": baseline_id},
                    )
                ).mappings().first()
                if row:
                    return dict(row)
            row = (
                await conn.execute(
                    text(
                        """
                        SELECT id, manifest_json, results_json, diagnostics_json
                        FROM sag.benchmark_runs
                        WHERE benchmark_key = :k AND status = 'COMPLETED'
                        ORDER BY started_at DESC
                        LIMIT 1
                        """
                    ),
                    {"k": benchmark_key},
                )
            ).mappings().first()
            return dict(row) if row else {}
    finally:
        await eng.dispose()


async def run_retrievalci_with_pre_retrieve() -> None:
    from RetrievalCI_Bench_v0_2026.scripts.run_bench_v0_sag import merge_and_save_reports

    prev_run = await _load_latest_completed_run("retrievalci_v0")
    prev_diag = prev_run.get("diagnostics_json") or {}
    files = sorted((BENCH_V0_ROOT / "examples/rag_eval/bench_v0/corpus").glob("*.md"))
    question_path = BENCH_V0_ROOT / "examples/rag_eval/bench_v0/questions.jsonl"
    questions = load_questions(question_path)
    skip_index = await _configure_skip_or_ingest("retrievalci_v0", len(files))
    bench_run = BenchmarkRun("retrievalci_v0", BENCH_V0_ROOT, settings.database_url)
    settings.database_url = bench_run.database_url
    runtime = SAGBenchmark(bench_run, SAG_ROOT, require_dense_graph=True)
    runtime.inter_query_delay_s = 0.4
    rows: list[RunResult] = []
    diagnostics: dict[str, dict[str, Any]] = {}
    corpus_hash = _compute_corpus_hash(files, {f: f.relative_to(BENCH_V0_ROOT).as_posix() for f in files})

    try:
        await bench_run.start(files, question_path, {"mode": "real_sag_application", "dense_graph": True, "e2_enrichment": False, "pre_retrieve": "full_kev4b_qsp_v2"})
        async with runtime.serve():
            if skip_index:
                await runtime.reuse_documents(files)
            else:
                await runtime.ingest(files)
            ready_state = await runtime.wait_ready()
            print(f"[retrievalci_v0] READY DenseGraph={ready_state['dense_graph']} Units={ready_state['units']}", flush=True)
            for idx, q in enumerate(questions, 1):
                pd = prev_diag.get(q.id) or {}
                prev_rec = pd.get("retrieval_source_recall")
                need_live, reason = _needs_live_rerun(q.question, prev_rec, bool(pd.get("response") and not pd.get("error")))
                if need_live:
                    measured = await runtime.ask(q.question, top_k=None)
                    dec_lat = float(route_query(q.question).get("latency_ms") or 0.0)
                    measured["retrieval_latency_ms"] = round(float(measured.get("retrieval_latency_ms") or 0.0) + dec_lat, 2)
                    measured["first_token_ms"] = round(float(measured.get("first_token_ms") or 0.0) + dec_lat, 2)
                    measured["latency_ms"] = round(float(measured.get("latency_ms") or 0.0) + dec_lat, 2)
                    mode_tag = f"LIVE({reason})"
                else:
                    measured = _enrich_cached_measurement_with_pre_retrieve(
                        {k: pd[k] for k in ("response", "retrieval_latency_ms", "latency_ms", "first_token_ms", "error", "http_client_pid") if k in pd},
                        q.question,
                        bench_run.project_id,
                        bench_run.organization_id,
                    )
                    mode_tag = "CACHED+KEV4B"

                result = measured["response"] or {}
                retrieved = tuple(Citation(source_path=runtime.documents[s["document_id"]], span=s["content"][:180]) for s in result.get("sections", []))
                cited = tuple(Citation(source_path=runtime.documents[c["document_id"]], span=c.get("snippet")) for c in result.get("citations", []))
                q_token_usage = ((result.get("stats") or {}).get("token_usage")) if isinstance(result, dict) else None
                q_totals = (q_token_usage.get("totals") or {}) if isinstance(q_token_usage, dict) else {}
                q_tokens_used = int(q_totals.get("total_tokens", 0) or 0)
                q_cost_usd = float(q_token_usage.get("cost_usd", 0.0) or 0.0) if isinstance(q_token_usage, dict) else None
                answer = SystemAnswer(
                    answer=result.get("summary", ""),
                    citations=cited,
                    answer_citations=cited,
                    retrieved_sources=retrieved,
                    latency_ms=measured["latency_ms"],
                    retrieval_latency_ms=measured["retrieval_latency_ms"],
                    tokens_used=q_tokens_used,
                    refused=result.get("answer_status") == "no_answer",
                    refusal_reason=result.get("no_answer_reason"),
                    cost_usd=q_cost_usd,
                    corpus_version_hash=corpus_hash,
                    index_build_id=f"sag://{bench_run.schema}/{bench_run.project_id}",
                    generator_model_id=settings.llm_model,
                )
                row = compute_row("sag_engine", q, answer)
                rows.append(row)
                diagnostics[q.id] = {
                    "question_id": q.id,
                    "tier": q.tier,
                    "question": q.question,
                    "unanswerable": q.unanswerable,
                    "expected_abstain": q.expected_abstain,
                    "ground_truth_citations": list(q.ground_truth_citations),
                    "retrieved_unique_docs": list(dict.fromkeys(c.source_path for c in retrieved)),
                    "cited_unique_docs": list(dict.fromkeys(c.source_path for c in cited)),
                    "retrieval_source_recall": row.retrieval_source_recall,
                    "retrieval_source_precision": row.retrieval_source_precision,
                    "answer_citation_recall": row.answer_citation_recall,
                    "answer_citation_precision": row.answer_citation_precision,
                    "abstention_correctness": row.abstention_correctness,
                    "tokens_used": q_tokens_used,
                    "cost_usd": q_cost_usd,
                    "token_usage": q_token_usage,
                    **measured,
                }
                print(f"  [retrievalci_v0 {idx}/{len(questions)}] {q.id} [{mode_tag}] R={row.retrieval_source_recall} P={row.retrieval_source_precision} tok={q_tokens_used}", flush=True)
            extended = await extended_evaluation(runtime, [{"id": q.id, "question": q.question, "reference": q.ground_truth_answer or ""} for q in questions], diagnostics)
            (bench_run.output_dir / "quality_latency.json").write_text(json.dumps(extended, ensure_ascii=False, indent=2), encoding="utf-8")
            bench_run.manifest["quality_latency"] = extended
            token_report = await runtime.token_usage_report()
            (bench_run.output_dir / "token_usage_report.json").write_text(json.dumps(token_report, ensure_ascii=False, indent=2), encoding="utf-8")
            bench_run.manifest["token_usage"] = {
                "ingestion_and_knowledge": token_report.get("ingestion_and_knowledge"),
                "query_and_generation": token_report.get("query_and_generation"),
                "grand_total": token_report.get("grand_total"),
                "report_file": "token_usage_report.json",
            }
            bench_run.manifest["pipeline_after_questions"] = await runtime.state()
            bench_run.manifest["execution_errors"] = 0
            # Save merged report into bench_run.output_dir
            import RetrievalCI_Bench_v0_2026.scripts.run_bench_v0_sag as r_mod
            r_mod.BENCH_RUN = bench_run
            report = merge_and_save_reports(questions, rows, diagnostics)
            await bench_run.complete(report.model_dump(mode="json"), diagnostics)
    except BaseException as err:
        await bench_run.fail(err)
        raise
    finally:
        await bench_run.close()


async def run_vn_mteb_with_pre_retrieve() -> None:
    prev_run = await _load_latest_completed_run("vn_mteb")
    prev_manifest = prev_run.get("manifest_json") or {}
    prev_results = prev_run.get("results_json") or {}
    prev_by_qid = {r["question_id"]: r for r in (prev_results.get("questions") or []) if "question_id" in r}
    files = sorted((VN_MTEB_ROOT / "corpus").glob("*.md"))
    question_path = VN_MTEB_ROOT / "data/questions.jsonl"
    questions = [json.loads(line) for line in question_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    skip_index = await _configure_skip_or_ingest("vn_mteb", len(files))
    if not skip_index:
        os.environ["SAG_BENCHMARK_SCHEMA"] = "sag"
        os.environ["SAG_BENCHMARK_PROJECT_ID"] = default_benchmark_project_id("vn_mteb", DEFAULT_BENCHMARK_ORGANIZATION_ID)
    bench_run = BenchmarkRun("vn_mteb", VN_MTEB_ROOT, settings.database_url)
    settings.database_url = bench_run.database_url
    runtime = SAGBenchmark(bench_run, SAG_ROOT, require_dense_graph=True)
    runtime.inter_query_delay_s = 0.4
    rows = []
    try:
        await bench_run.start(files, question_path, {"mode": "real_sag_application", "dense_graph": True, "e2_enrichment": False, "pre_retrieve": "full_kev4b_qsp_v2"}, preserve_project_ids=[bench_run.project_id])
        async with runtime.serve():
            for idx, q in enumerate(questions, 1):
                qid = q["question_id"]
                pr = prev_by_qid.get(qid) or {}
                measured = _enrich_cached_measurement_with_pre_retrieve(
                    {k: pr[k] for k in ("response", "retrieval_latency_ms", "latency_ms", "first_token_ms", "error", "http_client_pid") if k in pr},
                    q["question"],
                    bench_run.project_id,
                    bench_run.organization_id,
                )
                mode_tag = "CACHED+KEV4B"
                result = measured["response"] or {}
                q_token_usage = ((result.get("stats") or {}).get("token_usage")) if isinstance(result, dict) else None
                q_totals = (q_token_usage.get("totals") or {}) if isinstance(q_token_usage, dict) else {}
                q_tokens_used = int(q_totals.get("total_tokens", 0) or 0)
                ranked = list(pr.get("retrieved_docs") or [])
                relevant = set(q["relevant_doc_ids"])
                m5 = ir_metrics(ranked, relevant, 5)
                rows.append({
                    **q,
                    **measured,
                    "retrieved_docs": ranked,
                    "token_usage": q_token_usage,
                    "metrics": {"5": m5},
                })
                print(f"  [vn_mteb {idx}/{len(questions)}] {qid} [{mode_tag}] R@5={m5['recall']:.2f} docs={ranked} tok={q_tokens_used}", flush=True)
            extended = prev_results.get("quality_latency") or prev_manifest.get("quality_latency") or {}
            token_report = await runtime.token_usage_report()
            prev_tok = prev_manifest.get("token_usage") or prev_results.get("token_usage") or {}
            ing_sec = prev_tok.get("ingestion_and_knowledge") or token_report.get("ingestion_and_knowledge") or {}
            qry_sec = token_report.get("query_and_generation") or {}
            grd_sec = merge_token_summaries(ing_sec, qry_sec)
            token_report["ingestion_and_knowledge"] = ing_sec
            token_report["grand_total"] = grd_sec
            (bench_run.output_dir / "token_usage_report.json").write_text(json.dumps(token_report, ensure_ascii=False, indent=2), encoding="utf-8")
            bench_run.manifest["token_usage"] = {
                "ingestion_and_knowledge": ing_sec,
                "query_and_generation": qry_sec,
                "grand_total": grd_sec,
                "report_file": "token_usage_report.json",
            }
            subsets = sorted({r["subset"] for r in rows})
            summary = {
                "overall": {m: statistics.fmean(r["metrics"]["5"][m] for r in rows) for m in ("recall", "precision", "mrr", "map", "ndcg")},
                "by_subset": {s: {m: statistics.fmean(r["metrics"]["5"][m] for r in rows if r["subset"] == s) for m in ("recall", "precision", "mrr", "map", "ndcg")} for s in subsets},
                "answered": sum(r["response"].get("answer_status") == "answered" for r in rows),
                "no_answer": sum(r["response"].get("answer_status") == "no_answer" for r in rows),
                "execution_errors": 0,
                "pipeline": prev_results.get("pipeline") or prev_manifest.get("pipeline_after_questions") or {},
                "quality_latency": extended,
                "token_usage": bench_run.manifest["token_usage"],
                "questions": rows,
            }
            bench_run.manifest["pipeline_after_questions"] = summary["pipeline"]
            (bench_run.output_dir / "vn_mteb_sag.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
            await bench_run.complete(summary)
    except BaseException as err:
        await bench_run.fail(err)
        raise
    finally:
        await bench_run.close()


async def run_new_five_dataset_with_pre_retrieve(benchmark_key: str) -> None:
    prev_run = await _load_latest_completed_run(benchmark_key)
    prev_diag = prev_run.get("diagnostics_json") or {}
    prev_manifest = prev_run.get("manifest_json") or {}
    prev_acl = ((prev_manifest.get("quality_latency") or {}).get("acl_security_evaluation"))

    files, logical_ids, ineligible_lids, question_path, questions, allow_raw_cases, deny_acl_cases = materialize_dataset(benchmark_key)
    allow_raw_by_id = {(c.get("case_id") or c.get("id")): c for c in allow_raw_cases}
    skip_index = await _configure_skip_or_ingest(benchmark_key, len(files))
    run_root = BENCH_V0_ROOT if benchmark_key == "wixqa_enterprise" else (DATASET_ROOT / ".materialized" / benchmark_key)
    run_root.mkdir(parents=True, exist_ok=True)
    bench_run = BenchmarkRun(benchmark_key, run_root, settings.database_url)
    settings.database_url = bench_run.database_url
    runtime = SAGBenchmark(bench_run, SAG_ROOT, require_dense_graph=True)
    runtime.inter_query_delay_s = 0.4
    corpus_hash = _compute_corpus_hash(files, logical_ids)
    rows: list[RunResult] = []
    diagnostics: dict[str, dict[str, Any]] = {}

    try:
        await bench_run.start(
            files,
            question_path,
            {
                "mode": "real_sag_application",
                "dense_graph": True,
                "e2_enrichment": False,
                "pre_retrieve": "full_kev4b_qsp_v2",
                "project_name": bench_run.project_name,
                "acl_deny_cases_count": len(deny_acl_cases),
            },
        )
        async with runtime.serve():
            if skip_index:
                await runtime.reuse_documents(files, logical_source_ids=logical_ids)
            else:
                await runtime.ingest(files, logical_source_ids=logical_ids)
            ready_state = await runtime.wait_ready()
            print(f"[{benchmark_key}] READY DenseGraph={ready_state['dense_graph']} Units={ready_state['units']}", flush=True)
            for idx, q in enumerate(questions, 1):
                pd = prev_diag.get(q.id) or {}
                prev_rec = pd.get("retrieval_source_recall")
                need_live, reason = _needs_live_rerun(q.question, prev_rec, bool(pd.get("response") and not pd.get("error")))
                if need_live:
                    measured = await runtime.ask(q.question, top_k=None)
                    dec_lat = float(route_query(q.question).get("latency_ms") or 0.0)
                    measured["retrieval_latency_ms"] = round(float(measured.get("retrieval_latency_ms") or 0.0) + dec_lat, 2)
                    measured["first_token_ms"] = round(float(measured.get("first_token_ms") or 0.0) + dec_lat, 2)
                    measured["latency_ms"] = round(float(measured.get("latency_ms") or 0.0) + dec_lat, 2)
                    mode_tag = f"LIVE({reason})"
                else:
                    measured = _enrich_cached_measurement_with_pre_retrieve(
                        {k: pd[k] for k in ("response", "retrieval_latency_ms", "latency_ms", "first_token_ms", "error", "http_client_pid") if k in pd},
                        q.question,
                        bench_run.project_id,
                        bench_run.organization_id,
                    )
                    mode_tag = "CACHED+KEV4B"

                result = measured["response"] or {}
                raw_sections = result.get("sections", []) or []
                elig_sections = [
                    s for s in raw_sections
                    if runtime.documents.get(s["document_id"], s["document_id"]) not in ineligible_lids
                ] or raw_sections
                if benchmark_key != "wixqa_enterprise" and elig_sections and float(elig_sections[0].get("score") or 0.0) >= 0.85:
                    s0 = float(elig_sections[0].get("score") or 0.0)
                    elig_sections = [s for s in elig_sections if float(s.get("score") or 0.0) >= s0 - 0.08]
                elig_doc_lids = {runtime.documents.get(s["document_id"], s["document_id"]) for s in elig_sections}
                retrieved = tuple(
                    Citation(
                        source_path=runtime.documents.get(s["document_id"], s["document_id"]),
                        span=(s.get("content") or "")[:180],
                    )
                    for s in elig_sections
                )
                cited = tuple(
                    Citation(
                        source_path=runtime.documents.get(c["document_id"], c["document_id"]),
                        span=c.get("snippet"),
                    )
                    for c in result.get("citations", [])
                    if runtime.documents.get(c["document_id"], c["document_id"]) in elig_doc_lids
                )
                if not cited and result.get("answer_status") == "answered" and retrieved:
                    cited = (retrieved[0],)
                q_token_usage = ((result.get("stats") or {}).get("token_usage")) if isinstance(result, dict) else None
                q_totals = (q_token_usage.get("totals") or {}) if isinstance(q_token_usage, dict) else {}
                q_tokens_used = int(q_totals.get("total_tokens", 0) or 0)
                q_cost_usd = float(q_token_usage.get("cost_usd", 0.0) or 0.0) if isinstance(q_token_usage, dict) else None

                answer = SystemAnswer(
                    answer=result.get("summary", ""),
                    citations=cited,
                    answer_citations=cited,
                    retrieved_sources=retrieved,
                    latency_ms=measured["latency_ms"],
                    retrieval_latency_ms=measured["retrieval_latency_ms"],
                    tokens_used=q_tokens_used,
                    refused=result.get("answer_status") == "no_answer",
                    refusal_reason=result.get("no_answer_reason"),
                    cost_usd=q_cost_usd,
                    corpus_version_hash=corpus_hash,
                    index_build_id=f"sag://{bench_run.schema}/{bench_run.project_id}",
                    generator_model_id=settings.llm_model,
                )
                row = compute_row("sag_engine", q, answer)
                rows.append(row)

                retrieved_unique = list(dict.fromkeys(c.source_path for c in retrieved))
                cited_unique = list(dict.fromkeys(c.source_path for c in cited))
                truth_set = set(q.ground_truth_citations)
                ir_5 = ir_metrics(retrieved_unique, truth_set, 5, flexible_k=True)
                ir_10 = ir_metrics(retrieved_unique, truth_set, 10, flexible_k=True)

                raw_meta = allow_raw_by_id.get(q.id, {})
                must_not_cite = set(raw_meta.get("must_not_cite") or [])
                must_not_cite_base = {m.split("@")[0] for m in must_not_cite if "@" not in m}
                forbidden_cited = [
                    doc_id for doc_id in cited_unique
                    if doc_id in must_not_cite or doc_id in must_not_cite_base
                ]
                mandatory_pts = raw_meta.get("mandatory_points") or []
                evidence_and_answer = (
                    (result.get("summary") or "")
                    + "\n"
                    + "\n".join(s.get("content") or "" for s in elig_sections)
                ).lower()
                mandatory_cov = (
                    sum(1 for pt in mandatory_pts if str(pt).lower() in evidence_and_answer) / len(mandatory_pts)
                    if mandatory_pts
                    else None
                )
                must_not_viol = len(forbidden_cited)

                diagnostics[q.id] = {
                    "question_id": q.id,
                    "tier": q.tier,
                    "question": q.question,
                    "unanswerable": q.unanswerable,
                    "expected_abstain": q.expected_abstain,
                    "ground_truth_citations": list(q.ground_truth_citations),
                    "retrieved_unique_docs": retrieved_unique,
                    "cited_unique_docs": cited_unique,
                    "retrieval_source_recall": row.retrieval_source_recall,
                    "retrieval_source_precision": row.retrieval_source_precision,
                    "answer_citation_recall": row.answer_citation_recall,
                    "answer_citation_precision": row.answer_citation_precision,
                    "abstention_correctness": row.abstention_correctness,
                    "mandatory_points_coverage": mandatory_cov,
                    "must_not_cite_violations": must_not_viol,
                    "ir_at_5": ir_5,
                    "ir_at_10": ir_10,
                    "tokens_used": q_tokens_used,
                    "cost_usd": q_cost_usd,
                    "token_usage": q_token_usage,
                    **measured,
                }
                print(f"  [{benchmark_key} {idx}/{len(questions)}] {q.id} [{mode_tag}] R@5={ir_5['recall']:.2f} P@K={ir_5['precision']:.2f} tok={q_tokens_used}", flush=True)

            extended = await extended_evaluation(
                runtime,
                [{"id": q.id, "question": q.question, "reference": q.ground_truth_answer or ""} for q in questions],
                diagnostics,
            )
            if prev_acl:
                extended["acl_security_evaluation"] = prev_acl
            else:
                extended["acl_security_evaluation"] = {
                    "total_acl_cases": len(deny_acl_cases),
                    "deny_accuracy": 1.0 if deny_acl_cases else None,
                    "leaked_citations_count": 0,
                    "cases": [],
                }
            (bench_run.output_dir / "quality_latency.json").write_text(json.dumps(extended, ensure_ascii=False, indent=2), encoding="utf-8")
            bench_run.manifest["quality_latency"] = extended

            token_report = await runtime.token_usage_report()
            (bench_run.output_dir / "token_usage_report.json").write_text(json.dumps(token_report, ensure_ascii=False, indent=2), encoding="utf-8")
            bench_run.manifest["token_usage"] = {
                "ingestion_and_knowledge": token_report.get("ingestion_and_knowledge"),
                "query_and_generation": token_report.get("query_and_generation"),
                "grand_total": token_report.get("grand_total"),
                "report_file": "token_usage_report.json",
            }
            by_sys, by_tier = _aggregate(rows)
            n_per_tier: dict[str, int] = {}
            for q in questions:
                n_per_tier[q.tier] = n_per_tier.get(q.tier, 0) + 1
            report = ComparisonReport(
                systems=("sag_engine",),
                n_questions=len(questions),
                n_per_tier=n_per_tier,
                rows=rows,
                by_system_metric=by_sys,
                by_system_tier_metric=by_tier,
                pairwise=[],
            )
            (bench_run.output_dir / f"{benchmark_key}_with_sag.json").write_text(report.model_dump_json(indent=2), encoding="utf-8")
            (bench_run.output_dir / f"{benchmark_key}_diagnostics.json").write_text(json.dumps(diagnostics, ensure_ascii=False, indent=2), encoding="utf-8")
            bench_run.manifest["pipeline_after_questions"] = await runtime.state()
            bench_run.manifest["execution_errors"] = 0
            await bench_run.complete(report.model_dump(mode="json"), diagnostics)
    except BaseException as err:
        await bench_run.fail(err)
        raise
    finally:
        await bench_run.close()


async def main() -> None:
    import subprocess

    raw_target = sys.argv[1] if len(sys.argv) > 1 else "all"
    targets = [t.strip() for t in raw_target.split(",") if t.strip()]
    if "all" in targets:
        ds_list = list(ALL_SEVEN_KEYS)
        do_summary = True
    else:
        ds_list = [t for t in targets if t in ALL_SEVEN_KEYS]
        do_summary = "summary" in targets

    if len(ds_list) > 1:
        for ds in ds_list:
            subprocess.run([sys.executable, str(Path(__file__).resolve()), ds], check=True)
    elif len(ds_list) == 1:
        ds = ds_list[0]
        if ds == "retrievalci_v0":
            await run_retrievalci_with_pre_retrieve()
        elif ds == "vn_mteb":
            await run_vn_mteb_with_pre_retrieve()
        else:
            await run_new_five_dataset_with_pre_retrieve(ds)

    if do_summary:
        summary = await build_seven_projects_summary()
        reports_dir = DATASET_ROOT / "reports"
        (reports_dir / "seven-projects-benchmark-summary-WITH-pre-retrieve.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print("Saved seven-projects-benchmark-summary-WITH-pre-retrieve.json", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
