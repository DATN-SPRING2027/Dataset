"""Run eight fresh files and one full search through the real SAG application."""
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
        await run.start(files, questions, {'mode': 'eight_file_real_sag_e2e', 'top_k': 5})
        runtime = SAGBenchmark(run, SAG)
        async with runtime.serve():
            qdrant = await runtime.app.state.engine_manager.get_search_unit_qdrant_client()
            await run.require_new_collection(qdrant)
            await runtime.ingest(files)
            state = await asyncio.wait_for(runtime.wait_ready(), timeout=900)
            response = await runtime.ask(question['question'])
            result = {'elapsed_seconds': round(time.perf_counter() - started, 3),
                      'file_count': len(files), 'pipeline': state, 'query': response}
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
