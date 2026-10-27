"""Read retained benchmark scope and emit compact progress, never credentials or source text."""
import argparse
import asyncio
import json
import os
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SAG = ROOT.parent/'sag-laya-integration/SAG'
sys.path.insert(0,str(SAG/'apps/api'))
os.chdir(SAG)
from sag_api.core.config import settings
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

async def main(path):
    manifest = json.loads(path.read_text(encoding='utf-8'))
    schema = manifest['schema']
    assert re.fullmatch(r'sag(?:_bench_[a-z0-9_]+)?',schema)
    url = make_url(settings.database_url)
    engine = create_async_engine(url.set(query={k:v for k,v in url.query.items() if k != 'search_path'}),
                                 connect_args={'server_settings':{'search_path':schema}})
    try:
        async with engine.connect() as conn:
            row = (await conn.execute(text('SELECT status,results_json,diagnostics_json FROM benchmark_runs WHERE id=:id'),
                                      {'id':manifest['run_id']})).mappings().one()
            data = row['results_json'] or {}
            diagnostics = row['diagnostics_json'] or {}
            if isinstance(data,str): data=json.loads(data)
            if isinstance(diagnostics,str): diagnostics=json.loads(diagnostics)
            samples = list(diagnostics.values()) if diagnostics and all(isinstance(v,dict) for v in diagnostics.values()) else []
            samples = [v for v in samples if 'latency_ms' in v]
            summary = {'run_id':manifest['run_id'],'status':row['status'],'questions_done':len(samples),
                'errors':sum(bool(v.get('error')) for v in samples)}
            for key in ('retrieval_latency_ms','first_token_ms','latency_ms'):
                values = [v[key] for v in samples if v.get(key) is not None]
                summary[key+'_p50'] = statistics.median(values) if values else None
            summary['tree_jobs'] = [dict(r) for r in (await conn.execute(text('''SELECT id,status,attempts,error FROM jobs
                WHERE type='REBUILD_UNIVERSE_TREE' AND payload_json->>'tenant_id'=:tenant
                AND CAST(payload_json->'project_ids' AS jsonb) @> CAST(:projects AS jsonb)'''),
                {'tenant':manifest['organization_id'],'projects':json.dumps([manifest['project_id']])})).mappings().all()]
            summary['graphs'] = [dict(r) for r in (await conn.execute(text('''SELECT id,json_array_length(manifest_json->'units') AS units,
                json_array_length(manifest_json->'edges') AS edges FROM knowledge_graph_builds WHERE project_id=:project'''),
                {'project':manifest['project_id']})).mappings().all()]
            print(json.dumps(summary,ensure_ascii=False,indent=2))
    finally:
        await engine.dispose()

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('manifest',type=Path)
    args=parser.parse_args()
    asyncio.run(main(args.manifest.resolve()))
