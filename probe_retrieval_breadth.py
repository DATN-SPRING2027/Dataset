"""Small paired RetrievalCI diagnostic, using the existing SAG HTTP runtime and index."""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SAG = ROOT.parent / 'sag-laya-integration/SAG'
BENCH = ROOT / 'RetrievalCI_Bench_v0_2026'
QUESTION_IDS = ('qst_0343', 'qst_0344', 'qst_0348', 'qst_0350', 'qst_0354', 'qst_0005', 'qst_0015', 'qst_0001')


async def evaluate(run, runtime, files, questions):
    from retrievalci.rag_eval.metrics import compute_row
    from retrievalci.rag_eval.types import Citation, SystemAnswer

    rows = []
    try:
        await run.start(files, BENCH/'examples/rag_eval/bench_v0/questions.jsonl', {'mode':'paired_retrieval_probe'})
        async with runtime.serve():
            await runtime.reuse_documents(files)
            await runtime.wait_ready()
            run.manifest['probe_protocol'] = {
                'question_ids': list(QUESTION_IDS), 'repetitions_per_condition':2,
                'order':'ABBA per question, reversed for alternating questions',
                'A':'explicit top_k=5', 'B':'automatic top_k',
                'retrieval_only':True, 'scope':'diagnostic subset, not a full benchmark',
            }
            run._write_manifest()
            for index, qid in enumerate(QUESTION_IDS):
                question = questions[qid]
                order = [5, None, None, 5] if index % 2 == 0 else [None, 5, 5, None]
                for attempt, k in enumerate(order, 1):
                    measured = await runtime.ask(question.question, top_k=k, retrieval_only=True)
                    response = measured['response'] or {}
                    citations = tuple(Citation(source_path=runtime.documents[s['document_id']], span=s['content'][:180])
                                      for s in response.get('sections', []))
                    scored = compute_row('probe', question, SystemAnswer(
                        answer='', citations=(), retrieved_sources=citations, latency_ms=measured['latency_ms'],
                        retrieval_latency_ms=measured['retrieval_latency_ms'], tokens_used=0, cost_usd=None,
                    ))
                    rows.append({'question_id':qid, 'attempt':attempt, 'mode':'auto' if k is None else 'top5',
                                 'measurement':measured, 'score':scored.model_dump(mode='json')})
                    await run.checkpoint({'stage':'paired_probe', 'rows':rows})
                    print(f'Probe {len(rows)}/32 {qid} mode={rows[-1]["mode"]} error={measured["error"]}', flush=True)
            summary = {}
            for mode in ('top5','auto'):
                selected = [row for row in rows if row['mode'] == mode]
                summary[mode] = {'requests':len(selected),'errors':sum(bool(r['measurement']['error']) for r in selected)}
                for metric in ('retrieval_source_recall','retrieval_source_precision'):
                    values = [r['score'][metric] for r in selected if r['score'].get(metric) is not None]
                    summary[mode][metric] = statistics.fmean(values) if values else None
                values = [r['measurement']['retrieval_latency_ms'] for r in selected
                          if r['measurement']['retrieval_latency_ms'] is not None and not r['measurement']['error']]
                summary[mode]['retrieval_p50_ms'] = statistics.median(values) if values else None
            report = {'protocol':run.manifest['probe_protocol'], 'summary':summary, 'rows':rows}
            (run.output_dir/'paired_probe.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
            await run.complete(report)
            print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
    except BaseException as error:
        await run.fail(error)
        raise
    finally:
        await run.close()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--reuse-manifest', required=True, type=Path)
    args=parser.parse_args()
    source = args.reuse_manifest.resolve()
    old=json.loads(source.read_text(encoding='utf-8'))
    if old['benchmark'] != 'retrievalci_v0' or not re.fullmatch(r'sag_bench_[a-z0-9_]+',old['schema']):
        raise ValueError('Expected an isolated RetrievalCI run manifest')
    stamp=datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
    directory=ROOT/'reports'/f'retrievalci-paired-probe-{stamp}'
    directory.mkdir()
    for key in ('SCHEMA','PROJECT_ID','SOURCE_ID','SOURCE_CONFIG_ID'):
        os.environ['SAG_BENCHMARK_'+key]=str(old[key.lower()])
    os.environ['SAG_BENCHMARK_USER_ID']=old['user_id']
    os.environ['SAG_BENCHMARK_ORGANIZATION_ID']=old['organization_id']
    os.environ['SAG_BENCHMARK_OUTPUT_DIR']=str(directory/'result')
    os.environ['SAG_BENCHMARK_REUSE_RUN_ID']=old['run_id']
    os.environ['SAG_BENCHMARK_REUSE_MANIFEST_SHA256']=hashlib.sha256(source.read_bytes()).hexdigest()
    os.environ.pop('SAG_BENCHMARK_RUN_ID',None)
    sys.path[:0]=[str(SAG/'apps/api'),str(ROOT),str(BENCH)]
    os.chdir(SAG)
    from sqlalchemy.engine import make_url
    from sag_api.core.config import settings

    url=make_url(settings.database_url)
    settings.database_url=url.set(query={**url.query,'search_path':old['schema']}).render_as_string(hide_password=False)
    settings.data_dir=str(directory/'engine')
    settings.upload_dir=str(directory/'uploads')
    settings.dsh_connection_file=str(directory/'private-connection.json')
    from benchmark_support import BenchmarkRun
    from retrievalci.rag_eval.runner import load_questions
    from sag_benchmark_runtime import SAGBenchmark

    files=sorted((BENCH/'examples/rag_eval/bench_v0/corpus').glob('*.md'))
    questions={q.id:q for q in load_questions(BENCH/'examples/rag_eval/bench_v0/questions.jsonl')}
    if not set(QUESTION_IDS).issubset(questions):
        raise ValueError('Probe question missing from fixture')
    sys.argv=[str(Path(__file__).resolve()),'--skip-index']
    run=BenchmarkRun('retrievalci_v0', BENCH, settings.database_url)
    print(f'PROBE_OUTPUT={directory}',flush=True)
    try:
        asyncio.run(evaluate(run,SAGBenchmark(run,SAG),files,questions))
    finally:
        Path(settings.dsh_connection_file).unlink(missing_ok=True)


if __name__=='__main__':
    main()
