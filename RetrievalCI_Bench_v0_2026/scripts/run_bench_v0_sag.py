"""Run the RetrievalCI fixture through the real SAG runtime and retain official scoring.
Historical retrieve-only providers are reference data, not matched fresh runs.
"""
from __future__ import annotations
import asyncio
import argparse
import hashlib
import json
import os
import statistics
import sys
from pathlib import Path
from typing import Any

BENCH_ROOT = Path(__file__).resolve().parents[1]
SAG_ROOT = BENCH_ROOT.parents[1] / 'sag-laya-integration/SAG'
sys.path[:0] = [str(SAG_ROOT / 'apps/api'), str(BENCH_ROOT), str(BENCH_ROOT.parent)]
os.chdir(SAG_ROOT)
from sag_api.core.config import settings
from benchmark_support import BenchmarkRun
from sag_benchmark_runtime import SAGBenchmark
from benchmark_quality import extended_evaluation
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

BENCH_RUN = BenchmarkRun('retrievalci_v0', BENCH_ROOT, settings.database_url)
settings.database_url = BENCH_RUN.database_url
def _compute_corpus_hash(corpus_files: list[Path]) -> str:
    h = hashlib.sha256()
    for p in sorted(corpus_files, key=lambda x: x.name):
        rel = p.relative_to(BENCH_ROOT).as_posix()
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(p.read_bytes())
        h.update(b"\0")
    return h.hexdigest()


def _print_token_usage_summary(token_report: dict[str, Any]) -> None:
    print("\n" + "=" * 80)
    print("SAG BENCHMARK TOKEN USAGE & COST SUMMARY")
    print("=" * 80)
    for label, key in (
        ("Ingestion & Knowledge (81 files)", "ingestion_and_knowledge"),
        ("Query & Answer Generation (50 Qs)", "query_and_generation"),
        ("GRAND TOTAL", "grand_total"),
    ):
        section = token_report.get(key) or {}
        totals = section.get("totals") or {}
        print(
            f"{label:36s} | Total={int(totals.get('total_tokens', 0)):9,d} tok "
            f"(EmbIn={int(totals.get('embedding_input_tokens', 0)):8,d}, "
            f"LLMIn={int(totals.get('llm_input_tokens', 0)):8,d}, "
            f"LLMOut={int(totals.get('llm_output_tokens', 0)):8,d}) "
            f"| Cost=${float(section.get('cost_usd', 0.0)):.6f}"
        )
    grand = token_report.get("grand_total") or {}
    by_comp = grand.get("by_component") or {}
    if by_comp:
        print("\n--- Breakdown by SAG Component ---")
        for comp, bucket in sorted(by_comp.items()):
            print(
                f"  {comp:34s} | Total={int(bucket.get('total_tokens', 0)):9,d} "
                f"| EmbIn={int(bucket.get('embedding_input_tokens', 0)):8,d} "
                f"| LLMIn={int(bucket.get('llm_input_tokens', 0)):8,d} "
                f"| LLMOut={int(bucket.get('llm_output_tokens', 0)):8,d} "
                f"| Calls(Emb={int(bucket.get('embedding_calls', 0))},LLM={int(bucket.get('llm_calls', 0))},Cache={int(bucket.get('cache_hits', 0))}) "
                f"| Cost=${float(bucket.get('cost_usd', 0.0)):.6f}"
            )


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

    out_json = BENCH_RUN.output_dir / "bench_v0_with_sag.json"
    out_html = BENCH_RUN.output_dir / "bench_v0_with_sag.html"
    out_diag = BENCH_RUN.output_dir / "bench_v0_sag_diagnostics.json"

    out_json.write_text(combined_report.model_dump_json(indent=2), encoding="utf-8")
    write_html_report(
        out_html,
        title="RetrievalCI Bench-v0 (2026) — SAG application (Top-K from UI) and historical hosted references",
        rag_report=combined_report,
        primary_metric="retrieval_source_recall",
    )
    out_diag.write_text(json.dumps(diagnostics_by_qid, indent=2), encoding="utf-8")

    print("\n" + "=" * 80)
    print("RETRIEVALCI BENCH-V0 (2026) SAG APPLICATION RUN — HISTORICAL BASELINES ARE NOT RERUN")
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



async def async_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-index", action="store_true"); args = parser.parse_args()
    files = sorted((BENCH_ROOT / 'examples/rag_eval/bench_v0/corpus').glob('*.md'))
    question_path = BENCH_ROOT / 'examples/rag_eval/bench_v0/questions.jsonl'
    questions = load_questions(question_path)
    runtime = SAGBenchmark(BENCH_RUN, SAG_ROOT, require_dense_graph=True)
    rows, diagnostics, prev_diag, rerun_qids = [], {}, {}, {x.strip() for x in os.getenv('SAG_BENCHMARK_RERUN_QIDS', '').split(',') if x.strip()}
    corpus_hash = _compute_corpus_hash(files)
    try:
        await BENCH_RUN.start(files, question_path, {'mode': 'real_sag_application', 'dense_graph': True, 'e2_enrichment': False})
        if not args.skip_index and BENCH_RUN.cleaned_projects != [BENCH_RUN.project_id]:
            raise RuntimeError(
                f"Benchmark must clean and reuse only its dedicated project {BENCH_RUN.project_id}, got {BENCH_RUN.cleaned_projects}"
            )
        async with runtime.serve():
            await (runtime.reuse_documents(files) if args.skip_index else runtime.ingest(files))
            ready_state = await runtime.wait_ready()
            print(f"READY DenseGraph={ready_state['dense_graph']} Units={ready_state['units']} Evidence={ready_state['evidence']}", flush=True)
            for index, q in enumerate(questions, 1):
                if index == 1 and os.getenv('SAG_BENCHMARK_RESUME_FROM_RUN_ID'):
                    from sqlalchemy import text as _sql_text
                    async with BENCH_RUN.registry.connect() as _conn:
                        prev_diag = (await _conn.scalar(_sql_text('SELECT diagnostics_json FROM benchmark_runs WHERE id=:id'), {'id': os.environ['SAG_BENCHMARK_RESUME_FROM_RUN_ID']})) or {}
                measured = ({k: prev_diag[q.id][k] for k in ('response', 'retrieval_latency_ms', 'latency_ms', 'first_token_ms', 'error', 'http_client_pid') if k in prev_diag[q.id]}
                            if q.id in prev_diag and not prev_diag[q.id].get('error') and q.id not in rerun_qids
                            else await runtime.ask(q.question))
                result = measured['response'] or {}
                retrieved = tuple(Citation(source_path=runtime.documents[s['document_id']], span=s['content'][:180])
                                  for s in result.get('sections', []))
                cited = tuple(Citation(source_path=runtime.documents[c['document_id']], span=c.get('snippet'))
                              for c in result.get('citations', []))
                q_token_usage = ((result.get('stats') or {}).get('token_usage')) if isinstance(result, dict) else None
                q_totals = (q_token_usage.get('totals') or {}) if isinstance(q_token_usage, dict) else {}
                q_tokens_used = int(q_totals.get('total_tokens', 0) or 0)
                q_cost_usd = float(q_token_usage.get('cost_usd', 0.0) or 0.0) if isinstance(q_token_usage, dict) else None
                answer = SystemAnswer(
                    answer=result.get('summary', ''), citations=cited, answer_citations=cited,
                    retrieved_sources=retrieved, latency_ms=measured['latency_ms'],
                    retrieval_latency_ms=measured['retrieval_latency_ms'], tokens_used=q_tokens_used,
                    refused=result.get('answer_status') == 'no_answer',
                    refusal_reason=result.get('no_answer_reason'), cost_usd=q_cost_usd,
                    corpus_version_hash=corpus_hash,
                    index_build_id=f'sag://{BENCH_RUN.schema}/{BENCH_RUN.project_id}',
                    generator_model_id=settings.llm_model,
                    meta={
                        'execution_error': measured['error'],
                        'token_usage_measured': bool(isinstance(q_token_usage, dict)),
                        'token_usage': q_token_usage,
                    },
                )
                row = compute_row('sag_engine', q, answer)
                rows.append(row)
                diagnostics[q.id] = {
                    'question_id': q.id, 'question': q.question, 'tier': q.tier,
                    'unanswerable': q.unanswerable, 'expected_abstain': q.expected_abstain,
                    'ground_truth_citations': list(q.ground_truth_citations),
                    'retrieved_unique_docs': list(dict.fromkeys(c.source_path for c in retrieved)),
                    'retrieval_source_recall': row.retrieval_source_recall,
                    'retrieval_source_precision': row.retrieval_source_precision,
                    'abstention_correctness': row.abstention_correctness,
                    'token_usage': q_token_usage,
                    **measured,
                }
                await BENCH_RUN.checkpoint({'rows': [r.model_dump(mode='json') for r in rows]}, diagnostics)
                print(
                    f'Asked {index}/{len(questions)} {q.id}: status={result.get("answer_status")} '
                    f'tokens={q_tokens_used} error={measured["error"]}',
                    flush=True,
                )
            if any(d['error'] for d in diagnostics.values()):
                raise RuntimeError('SAG Q&A produced execution errors; see checkpoint diagnostics')
            extended = await extended_evaluation(runtime,
                [{'id': q.id, 'question': q.question, 'reference': q.ground_truth_answer} for q in questions],
                {qid: {'response': d['response'], 'error': d['error'], 'retrieval_latency_ms': d['retrieval_latency_ms'],
                       'first_token_ms': d['first_token_ms'], 'latency_ms': d['latency_ms']} for qid, d in diagnostics.items()})
            if any(r['error'] for r in extended['warm_attempts']):
                raise RuntimeError('SAG Q&A replay produced execution errors; see quality_latency.json')
            rows = [row.model_copy(update={name: extended['quality'][row.question_id].get(name, {}).get('score')
                                         for name in ('faithfulness', 'relevance')}) for row in rows]
            matched = [row.model_copy(update={'system': 'sag_engine_top5'}) for row in rows]
            historical = ComparisonReport.model_validate_json((BENCH_ROOT/'baselines/rag/bench_v0_merged.json').read_text(encoding='utf-8'))
            reference = [r for r in historical.rows if r.system in ('vertex_ai_rag','bedrock_kb','openai_file_search','azure_ai_search')]
            aggregates, tiers = _aggregate(matched + reference)
            extended['hosted_top5_comparison'] = {
                'protocol': 'SAG first-pass full Q&A with Top-5; hosted references historical, latency conditions not matched',
                'rows': [r.model_dump(mode='json') for r in matched + reference],
                'by_system_metric': aggregates, 'by_system_tier_metric': tiers}
            (BENCH_RUN.output_dir/'quality_latency.json').write_text(json.dumps(extended,ensure_ascii=False,indent=2),encoding='utf-8')
            BENCH_RUN.manifest['quality_latency'] = extended
            token_report = await runtime.token_usage_report()
            token_report['questions'] = [
                {
                    'question_id': q.id,
                    'tier': q.tier,
                    'unanswerable': q.unanswerable,
                    'answer_status': ((diagnostics[q.id].get('response') or {}).get('answer_status')),
                    'token_usage': diagnostics[q.id].get('token_usage'),
                }
                for q in questions
            ]
            (BENCH_RUN.output_dir / 'token_usage_report.json').write_text(
                json.dumps(token_report, ensure_ascii=False, indent=2),
                encoding='utf-8',
            )
            BENCH_RUN.manifest['token_usage'] = {
                'file_count': token_report.get('file_count'),
                'pricing_per_1m_usd': token_report.get('pricing_per_1m_usd'),
                'ingestion_and_knowledge': token_report.get('ingestion_and_knowledge'),
                'query_and_generation': token_report.get('query_and_generation'),
                'grand_total': token_report.get('grand_total'),
                'report_file': 'token_usage_report.json',
            }
            report = merge_and_save_reports(questions, rows, diagnostics)
            _print_token_usage_summary(token_report)
            BENCH_RUN.manifest['pipeline_after_questions'] = await runtime.state()
            BENCH_RUN.manifest['execution_errors'] = sum(bool(d['error']) for d in diagnostics.values())
            await BENCH_RUN.complete(report.model_dump(mode='json'), diagnostics)
    except BaseException as error:
        await BENCH_RUN.fail(error)
        raise
    finally:
        await BENCH_RUN.close()

if __name__ == '__main__':
    asyncio.run(async_main())
