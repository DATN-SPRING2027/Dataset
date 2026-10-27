"""Run the complete local VN fixture using real SAG ingestion, workers and streamed Q&A.
This 130-document/50-query fixture is not the full public MTEB leaderboard.
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
from benchmark_quality import extended_evaluation, ir_metrics
BENCH_RUN = BenchmarkRun('vn_mteb', BENCH_ROOT, settings.database_url)
settings.database_url = BENCH_RUN.database_url
async def evaluate_vn_benchmark():
    parser = argparse.ArgumentParser()
    parser.parse_args()
    files = sorted((BENCH_ROOT / 'corpus').glob('*.md'))
    question_path = BENCH_ROOT / 'data/questions.jsonl'
    questions = [json.loads(line) for line in question_path.read_text(encoding='utf-8').splitlines() if line.strip()]
    runtime = SAGBenchmark(BENCH_RUN, SAG_ROOT)
    rows = []
    try:
        await BENCH_RUN.start(files, question_path, {'mode': 'real_sag_application'})
        async with runtime.serve():
            await runtime.ingest(files)
            await runtime.wait_ready()
            for index, q in enumerate(questions, 1):
                measured = await runtime.ask(q['question'])
                result = measured['response'] or {}
                ranked = list(dict.fromkeys(Path(runtime.documents[s['document_id']]).name for s in result.get('sections', [])))
                relevant = set(q['relevant_doc_ids'])
                rows.append({**q, **measured, 'retrieved_docs': ranked,
                             'metrics': {'5': ir_metrics(ranked, relevant, 5)}})
                await BENCH_RUN.checkpoint({'questions': rows, 'stage': 'qa'})
                print(f'Asked {index}/{len(questions)} {q["question_id"]}: status={result.get("answer_status")} error={measured["error"]}', flush=True)
            if any(r['error'] for r in rows):
                raise RuntimeError('SAG Q&A produced execution errors; see checkpoint results')
            extended = await extended_evaluation(runtime,
                [{'id': q['question_id'], 'question': q['question']} for q in questions],
                {r['question_id']: r for r in rows})
            if any(r['error'] for r in extended['warm_attempts']):
                raise RuntimeError('SAG Q&A replay produced execution errors; see quality_latency.json')
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
                'questions': rows, 'pipeline': pipeline, 'quality_latency': extended,
                'subsets': {subset: {str(k): {m: statistics.fmean(r['metrics'][str(k)][m] for r in rows if r['subset']==subset)
                                           for m in ('recall','precision','mrr','map','ndcg')} for k in (5,)}
                            for subset in sorted({r['subset'] for r in rows})},
            }
            (BENCH_RUN.output_dir / 'vn_mteb_sag_results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
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
