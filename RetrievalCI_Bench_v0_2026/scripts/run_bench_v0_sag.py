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
    parser.parse_args()
    files = sorted((BENCH_ROOT / 'examples/rag_eval/bench_v0/corpus').glob('*.md'))
    question_path = BENCH_ROOT / 'examples/rag_eval/bench_v0/questions.jsonl'
    questions = load_questions(question_path)
    runtime = SAGBenchmark(BENCH_RUN, SAG_ROOT)
    rows, diagnostics = [], {}
    try:
        await BENCH_RUN.start(files, question_path, {'mode': 'real_sag_application'})
        async with runtime.serve():
            await runtime.ingest(files)
            await runtime.wait_ready()
            for index, q in enumerate(questions, 1):
                measured = await runtime.ask(q.question)
                result = measured['response'] or {}
                retrieved = tuple(Citation(source_path=runtime.documents[s['document_id']], span=s['content'][:180])
                                  for s in result.get('sections', []))
                cited = tuple(Citation(source_path=runtime.documents[c['document_id']], span=c.get('snippet'))
                              for c in result.get('citations', []))
                answer = SystemAnswer(
                    answer=result.get('summary', ''), citations=cited, answer_citations=cited,
                    retrieved_sources=retrieved, latency_ms=measured['latency_ms'],
                    retrieval_latency_ms=measured['retrieval_latency_ms'], tokens_used=0,
                    refused=result.get('answer_status') == 'no_answer',
                    refusal_reason=result.get('no_answer_reason'), cost_usd=None,
                    corpus_version_hash=_compute_corpus_hash(files),
                    index_build_id=f'sag://{BENCH_RUN.schema}/{BENCH_RUN.project_id}',
                    generator_model_id=settings.llm_model,
                    meta={'execution_error': measured['error'], 'token_usage_measured': False},
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
                    'abstention_correctness': row.abstention_correctness, **measured,
                }
                await BENCH_RUN.checkpoint({'rows': [r.model_dump(mode='json') for r in rows]}, diagnostics)
                print(f'Asked {index}/{len(questions)} {q.id}: status={result.get("answer_status")} error={measured["error"]}', flush=True)
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
            report = merge_and_save_reports(questions, rows, diagnostics)
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
