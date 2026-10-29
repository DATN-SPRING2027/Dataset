"""Run the complete local VN fixture using real SAG ingestion, workers and streamed Q&A.
This 130-document/50-query fixture is not the full public MTEB leaderboard.
"""
from __future__ import annotations
import asyncio
import argparse
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
from benchmark_quality import extended_evaluation, ir_metrics

BENCH_RUN = BenchmarkRun('vn_mteb', BENCH_ROOT, settings.database_url)
settings.database_url = BENCH_RUN.database_url


def _print_token_usage_summary(token_report: dict[str, Any], doc_count: int, q_count: int) -> None:
    print("\n" + "=" * 80)
    print("SAG VN-MTEB BENCHMARK TOKEN USAGE & COST SUMMARY")
    print("=" * 80)
    for label, key in (
        (f"Ingestion & Knowledge ({doc_count} files)", "ingestion_and_knowledge"),
        (f"Query & Answer Generation ({q_count} Qs)", "query_and_generation"),
        ("GRAND TOTAL", "grand_total"),
    ):
        section = token_report.get(key) or {}
        totals = section.get("totals") or {}
        print(
            f"{label:38s} | Total={int(totals.get('total_tokens', 0)):9,d} tok "
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


async def evaluate_vn_benchmark():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-index", action="store_true")
    args = parser.parse_args()
    files = sorted((BENCH_ROOT / 'corpus').glob('*.md'))
    question_path = BENCH_ROOT / 'data/questions.jsonl'
    questions = [json.loads(line) for line in question_path.read_text(encoding='utf-8').splitlines() if line.strip()]
    runtime = SAGBenchmark(BENCH_RUN, SAG_ROOT, require_dense_graph=True)
    rows = []
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
                measured = await runtime.ask(q['question'])
                result = measured['response'] or {}
                q_token_usage = ((result.get('stats') or {}).get('token_usage')) if isinstance(result, dict) else None
                q_totals = (q_token_usage.get('totals') or {}) if isinstance(q_token_usage, dict) else {}
                q_tokens_used = int(q_totals.get('total_tokens', 0) or 0)
                ranked = list(dict.fromkeys(Path(runtime.documents[s['document_id']]).name for s in result.get('sections', [])))
                relevant = set(q['relevant_doc_ids'])
                rows.append({
                    **q,
                    **measured,
                    'retrieved_docs': ranked,
                    'token_usage': q_token_usage,
                    'metrics': {'5': ir_metrics(ranked, relevant, 5)},
                })
                await BENCH_RUN.checkpoint({'questions': rows, 'stage': 'qa'})
                print(
                    f'Asked {index}/{len(questions)} {q["question_id"]}: status={result.get("answer_status")} '
                    f'tokens={q_tokens_used} error={measured["error"]}',
                    flush=True,
                )
            if any(r['error'] for r in rows):
                raise RuntimeError('SAG Q&A produced execution errors; see checkpoint results')
            extended = await extended_evaluation(
                runtime,
                [{'id': q['question_id'], 'question': q['question']} for q in questions],
                {r['question_id']: r for r in rows},
            )
            if any(r['error'] for r in extended['warm_attempts']):
                raise RuntimeError('SAG Q&A replay produced execution errors; see quality_latency.json')
            token_report = await runtime.token_usage_report()
            token_report['questions'] = [
                {
                    'question_id': r['question_id'],
                    'subset': r.get('subset'),
                    'answer_status': ((r.get('response') or {}).get('answer_status')),
                    'token_usage': r.get('token_usage'),
                }
                for r in rows
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
            pipeline = await runtime.state()
            report = {
                'protocol': {'name': 'real_sag_application', 'top_k': runtime.policy['top_k'],
                             'latency': 'first pass without explicit query prewarming; real HTTP including generation',
                             'public_leaderboard_comparable': False},
                'summary': {
                    'documents': len(files), 'questions': len(rows),
                    'retrieval': {str(k): {m: statistics.fmean(r['metrics'][str(k)][m] for r in rows)
                                          for m in ('recall', 'precision', 'mrr', 'map', 'ndcg')} for k in (5,)},
                    'answered': sum((r['response'] or {}).get('answer_status') == 'answered' and not r['error'] for r in rows),
                    'execution_errors': sum(bool(r['error']) for r in rows),
                    'retrieval_p50_ms': statistics.median(r['retrieval_latency_ms'] for r in rows if r['retrieval_latency_ms'] is not None),
                    'qa_p50_ms': statistics.median(r['latency_ms'] for r in rows),
                },
                'token_usage': BENCH_RUN.manifest['token_usage'],
                'questions': rows, 'pipeline': pipeline, 'quality_latency': extended,
                'subsets': {subset: {str(k): {m: statistics.fmean(r['metrics'][str(k)][m] for r in rows if r['subset']==subset)
                                           for m in ('recall','precision','mrr','map','ndcg')} for k in (5,)}
                            for subset in sorted({r['subset'] for r in rows})},
            }
            (BENCH_RUN.output_dir / 'vn_mteb_sag_results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
            _print_token_usage_summary(token_report, len(files), len(rows))
            BENCH_RUN.manifest['pipeline_after_questions'] = pipeline
            await BENCH_RUN.complete(report, pipeline)
            print(json.dumps(report['summary'], ensure_ascii=False, indent=2), flush=True)
    except BaseException as error:
        await BENCH_RUN.fail(error)
        raise
    finally:
        await BENCH_RUN.close()


if __name__ == '__main__':
    asyncio.run(evaluate_vn_benchmark())
