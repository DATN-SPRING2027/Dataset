"""Differential checks against the captured pre-fix implementations; no database/provider writes."""
import asyncio
import importlib.util
import json
import os
import random
import sys
import time
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
SAG = HERE.parents[2]/'sag-laya-integration/SAG'
sys.path.insert(0, str(SAG/'apps/api'))
os.chdir(SAG)
from sag_api.sag import RetrievedSection
from sag_api.services import cpu_worker, dedup_and_temporal_service as dedup
from sag_api.services import retrieval_service as retrieval, routing_tree_service as routing

def load(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE/file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def timed(call):
    start = time.perf_counter()
    result = call()
    return result, time.perf_counter()-start

async def main():
    old_retrieval = load('old_mmr_reference', 'retrieval_service_before_mmr_fix.py')
    old_routing = load('old_routing_reference', 'routing_service_before_fix.py')
    old_dedup = load('old_dedup_reference', 'dedup_service_before_fix.py')
    rng = random.Random(42)
    sections = [RetrievedSection(chunk_id=str(i), document_id=f'doc-{i % 3}', heading='Upload policy',
                    content=' '.join(f'fact{rng.randrange(10000)}' for _ in range(220)), score=.95, rank=i)
                for i in range(100)]
    mmr_cases = []
    for query, limit in [('Upload policy', None), ('Compare all policies PR-12345', 30), ('policy', 5)]:
        before, old_seconds = timed(lambda: old_retrieval.select_diverse_sections(query, sections, limit=limit))
        after, new_seconds = timed(lambda: retrieval.select_diverse_sections(query, sections, limit=limit))
        same = ([s.model_dump() for s in before[0]], before[1]) == ([s.model_dump() for s in after[0]], after[1])
        assert same
        mmr_cases.append(dict(query=query, limit=limit, equal=same, old_seconds=old_seconds, new_seconds=new_seconds))
        print('MMR', mmr_cases[-1], flush=True)
    inputs = [routing.KnowledgeUnitInput(str(i),'tenant','project','partition',
                dense=tuple(rng.uniform(-1,1) for _ in range(64)), sparse=(('policy',1.0),)) for i in range(96)]
    old_inputs = [old_routing.KnowledgeUnitInput(**{k:getattr(u,k) for k in routing.KnowledgeUnitInput.__dataclass_fields__})
                  for u in inputs]
    before, old_seconds = timed(lambda: old_routing.build_routing_snapshot(old_inputs))
    after, new_seconds = timed(lambda: routing.build_routing_snapshot(inputs))
    assert before.manifest_json == after.manifest_json
    tree = dict(equal=True, units=len(inputs), old_seconds=old_seconds, new_seconds=new_seconds)
    print('Routing',tree,flush=True)

    class Result:
        def __init__(self, rows): self.rows = rows
        def scalars(self): return self
        def all(self): return self.rows
        def first(self): return next(iter(self.rows), None)
    class Session:
        def __init__(self, current, prior): self.results = iter([[],current,prior])
        async def execute(self, query): return Result(next(self.results))
        def add(self, row): pass
    current = [SimpleNamespace(id='exact',document_version_id='new',normalized_text='same text',
                   content_hash='same',block_type='paragraph',dedup_signature_json=None),
               SimpleNamespace(id='contrast',document_version_id='new',normalized_text='not permitted',
                   content_hash='different',block_type='paragraph',dedup_signature_json=None)]
    prior = [SimpleNamespace(id=f'p{i}',document_version_id='old',normalized_text='permitted',
                 content_hash='same' if i == 0 else f'h{i}',block_type='paragraph',dedup_signature_json=None)
             for i in range(10)]
    embedder = SimpleNamespace(batch_generate=lambda texts: None)
    async def embed(texts): return [[1.0,0.0] for _ in texts]
    embedder.batch_generate = embed
    before = await old_dedup.run_dedup_and_temporal_stage(Session(current,prior),
        document_version=SimpleNamespace(id='new',file_hash='new',metadata_json={}), document_id='d',
        project_id='project',embedder=embedder)
    real_cpu = cpu_worker.run_cpu
    async def direct(operation,payload): return cpu_worker._calculate(operation,payload)
    cpu_worker.run_cpu = direct
    try:
        after = await dedup.run_dedup_and_temporal_stage(Session(current,prior),
            document_version=SimpleNamespace(id='new',file_hash='new',metadata_json={}), document_id='d',
            project_id='project',embedder=embedder)
    finally:
        cpu_worker.run_cpu = real_cpu
    assert before == after
    output = dict(mmr=mmr_cases, routing=tree, dedup=dict(equal=True,result=after))
    (HERE/'fixed_math_parity.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Dedup exact/semantic/contradiction outcomes equal',flush=True)

if __name__ == '__main__': asyncio.run(main())
