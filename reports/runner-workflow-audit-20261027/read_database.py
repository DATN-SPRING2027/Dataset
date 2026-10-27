"""Read-only comparison of persisted successful and failed benchmark workloads."""
import asyncio
import json
import os
from pathlib import Path
import sys

from sqlalchemy import text

SAG = Path('D:/DoAnTotnghiep/sag-laya-integration/SAG')
ROOT = Path(__file__).resolve().parent
os.chdir(SAG)
sys.path.insert(0, str(SAG/'apps/api'))
from sag_api.core.db import engine

SCOPES = {
    'old_retrievalci_completed': ('sag', '08c89c865e2c481fb5ebbe02'),
    'old_vn_completed': ('sag', '9f1dfc0aab484447a0b1e5c1'),
    'new_isolated_failed': ('sag_bench_ci_20261027030149', '0924d58e249b4502b86dfdb9'),
}


async def main():
    result = {}
    async with engine.connect() as connection:
        await connection.execute(text('SET TRANSACTION READ ONLY'))
        for label, (schema, project) in SCOPES.items():
            queries = {
                'documents': f'SELECT status,count(*) AS n,sum(chunk_count) AS chunks,sum(event_count) AS events,sum(token_usage) AS extraction_tokens FROM {schema}.documents WHERE project_id=:p GROUP BY status',
                'versions': f'SELECT v.search_status,v.knowledge_status,count(*) AS n FROM {schema}.document_versions v JOIN {schema}.documents d ON d.id=v.document_id WHERE d.project_id=:p GROUP BY v.search_status,v.knowledge_status',
                'units': f"SELECT count(*) AS n,count(*) FILTER(WHERE jsonb_array_length(COALESCE(features_json::jsonb->'dense','[]'::jsonb))>0) AS dense_units,max(jsonb_array_length(COALESCE(features_json::jsonb->'dense','[]'::jsonb))) AS max_dimension FROM {schema}.knowledge_units WHERE project_id=:p AND is_current=true",
                'graph_builds': f"SELECT id,jsonb_array_length(manifest_json::jsonb->'units') AS n_units,jsonb_array_length(manifest_json::jsonb->'edges') AS n_edges FROM {schema}.knowledge_graph_builds WHERE project_id=:p ORDER BY id",
                'trees': f'SELECT status,tree_version FROM {schema}.tree_manifests WHERE project_id=:p',
                'knowledge_jobs': f'SELECT j.kind,j.status,j.error_code,count(*) AS n,max(j.attempts) AS attempts FROM {schema}.knowledge_jobs j JOIN {schema}.document_versions v ON v.id=j.document_version_id JOIN {schema}.documents d ON d.id=v.document_id WHERE d.project_id=:p GROUP BY j.kind,j.status,j.error_code',
                'document_jobs': f'SELECT j.type,j.status,j.attempts,j.error,d.filename FROM {schema}.jobs j JOIN {schema}.documents d ON d.id=j.document_id WHERE d.project_id=:p AND j.status<>\'SUCCEEDED\' ORDER BY j.created_at LIMIT 12',
                'index_stages': f'SELECT s.status,s.duration_ms,s.error_message FROM {schema}.stage_runs s JOIN {schema}.ingestion_runs r ON r.id=s.run_id WHERE r.project_id=:p AND s.stage=\'INDEX_SEARCH\'',
            }
            result[label] = {}
            for key, sql in queries.items():
                result[label][key] = [dict(row) for row in (await connection.execute(text(sql), {'p': project})).mappings()]
            print(label, json.dumps({k:v for k,v in result[label].items() if k not in {'document_jobs','index_stages','graph_builds'}}, default=str), flush=True)
            print(label, 'graph_build_count', len(result[label]['graph_builds']), flush=True)
    await engine.dispose()
    (ROOT/'database_comparison.json').write_text(json.dumps(result, indent=2, default=str, ensure_ascii=False), encoding='utf-8')


asyncio.run(main())


