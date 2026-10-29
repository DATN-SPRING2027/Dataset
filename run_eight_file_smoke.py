"""Run eight fresh files and one full search through the real SAG application (`FOUNDATION + DenseGraph`)."""
import asyncio
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parent
BENCH = ROOT / 'RetrievalCI_Bench_v0_2026'
SAG = ROOT.parent / 'sag-laya-integration' / 'SAG'
sys.path[:0] = [str(SAG / 'apps/api'), str(ROOT)]
os.chdir(SAG)

from sag_api.core.config import settings
from benchmark_support import BenchmarkRun
from sag_benchmark_runtime import SAGBenchmark


async def main():
    questions = BENCH / 'examples/rag_eval/bench_v0/questions.jsonl'
    question = json.loads(questions.read_text(encoding='utf-8').splitlines()[0])
    first = BENCH / question['ground_truth_citations'][0]
    corpus = sorted((BENCH / 'examples/rag_eval/bench_v0/corpus').glob('*.md'))
    files = [first] + [p for p in corpus if p != first][:7]
    run = BenchmarkRun('eight_file_e2e_smoke', BENCH, settings.database_url)
    settings.database_url = run.database_url
    started = time.perf_counter()
    try:
        await run.start(
            files,
            questions,
            {
                'mode': 'eight_file_real_sag_e2e',
                'top_k': 5,
                'dense_graph': True,
                'e2_enrichment': False,
            },
        )
        if run.cleaned_projects != [run.project_id]:
            raise RuntimeError(
                f'8-file E2E must clean only its own project {run.project_id}, got {run.cleaned_projects}'
            )
        runtime = SAGBenchmark(run, SAG, require_dense_graph=True)
        async with runtime.serve():
            qdrant = await runtime.app.state.engine_manager.get_search_unit_qdrant_client()
            await run.require_new_collection(qdrant)
            await runtime.ingest(files)
            state = await asyncio.wait_for(runtime.wait_ready(), timeout=900)
            units = state['units']
            evidence = state['evidence']
            dense_graph = state['dense_graph']
            if units['with_dense'] != units['total'] or dense_graph['semantic_dense_edges'] <= 0:
                raise RuntimeError(f'DenseGraph incomplete in 8-file E2E: units={units}, graph={dense_graph}')
            if evidence.get('E2', 0) != 0:
                raise RuntimeError(f'Unexpected E2 enrichment evidence in FOUNDATION-only pipeline: evidence={evidence}')
            response = await runtime.ask(question['question'])
            token_report = await runtime.token_usage_report()
            (run.output_dir / 'token_usage_report.json').write_text(
                json.dumps(token_report, ensure_ascii=False, indent=2), encoding='utf-8'
            )
            run.manifest['token_usage'] = {
                'ingestion_and_knowledge': token_report.get('ingestion_and_knowledge'),
                'query_and_generation': token_report.get('query_and_generation'),
                'grand_total': token_report.get('grand_total'),
            }
            result = {
                'elapsed_seconds': round(time.perf_counter() - started, 3),
                'file_count': len(files),
                'cleanup': run.manifest.get('cleanup'),
                'pipeline': state,
                'query': response,
                'token_usage': run.manifest['token_usage'],
            }
            (run.output_dir / 'smoke_result.json').write_text(
                json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
            if response['error'] is not None:
                raise RuntimeError(f"Search failed: {response['error']}")
            await run.complete(result)
            print('SMOKE_COMPLETE', run.output_dir, flush=True)
    except BaseException as error:
        await run.fail(error)
        raise
    finally:
        await run.close()


if __name__ == '__main__':
    asyncio.run(main())
