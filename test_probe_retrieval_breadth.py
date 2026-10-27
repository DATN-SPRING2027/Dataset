import json
import sys
from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

import probe_retrieval_breadth as probe

sys.path.insert(0, str(probe.BENCH))
from retrievalci.rag_eval.runner import load_questions


@pytest.mark.asyncio
async def test_probe_pairs_modes_and_uses_dataset_metric(tmp_path):
    questions = {q.id: q for q in load_questions(probe.BENCH/'examples/rag_eval/bench_v0/questions.jsonl')}
    run = SimpleNamespace(output_dir=tmp_path, manifest={}, start=AsyncMock(), checkpoint=AsyncMock(),
                          complete=AsyncMock(), fail=AsyncMock(), close=AsyncMock(), _write_manifest=lambda: None)
    order = []

    class Runtime:
        documents = {'doc':'examples/rag_eval/bench_v0/corpus/unrelated.md'}

        @asynccontextmanager
        async def serve(self):
            yield self

        async def reuse_documents(self, files): pass
        async def wait_ready(self): pass

        async def ask(self, query, *, top_k, retrieval_only):
            assert retrieval_only
            order.append(top_k)
            return {'response':{'sections':[{'document_id':'doc','content':'evidence'}], 'stats':{}},
                    'latency_ms':10, 'retrieval_latency_ms':10, 'error':None}

    await probe.evaluate(run, Runtime(), [], questions)
    saved = json.loads((tmp_path/'paired_probe.json').read_text(encoding='utf-8'))
    assert len(saved['rows']) == 32
    assert order[:8] == [5,None,None,5,None,5,5,None]
    assert saved['summary']['top5']['requests'] == saved['summary']['auto']['requests'] == 16
    assert saved['summary']['top5']['retrieval_source_recall'] == 0
    run.complete.assert_awaited_once()
