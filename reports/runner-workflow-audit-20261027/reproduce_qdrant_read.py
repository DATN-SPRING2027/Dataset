"""Read-only Qdrant count before/during CPU graph work. Never deletes or indexes points."""
import asyncio
import json
import os
from pathlib import Path
import sys
import time

import httpx
from sqlalchemy import select, text
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parent
SAG = Path('D:/DoAnTotnghiep/sag-laya-integration/SAG')
os.chdir(SAG)
sys.path.insert(0, str(SAG/'apps/api'))
from sag_api.core.config import settings

url = make_url(settings.database_url)
settings.database_url = url.set(query={**dict(url.query), 'search_path': 'sag_bench_ci_20261027030149'}).render_as_string(hide_password=False)
from sag_api.core.db import SessionLocal, engine
from sag_api.db.models import KnowledgeUnit
from sag_api.services.knowledge_service import graph_payload


async def main():
    async with SessionLocal() as session:
        await session.execute(text('SET TRANSACTION READ ONLY'))
        units = list((await session.scalars(select(KnowledgeUnit).where(
            KnowledgeUnit.project_id == '0924d58e249b4502b86dfdb9',
            KnowledgeUnit.is_current.is_(True),
        ).order_by(KnowledgeUnit.id))).all())
    await engine.dispose()
    report = {'units': len(units), 'database_writes': 0, 'qdrant_writes': 0, 'timeout_seconds': 30,
              'measurements': [], 'graph_seconds': []}
    headers = {'api-key': settings.sag_qdrant_api_key} if settings.sag_qdrant_api_key else {}
    async with httpx.AsyncClient(base_url=settings.sag_qdrant_url.rstrip('/'), headers=headers, timeout=30) as client:
        async def probe(mode):
            start = time.perf_counter()
            row = {'mode': mode}
            try:
                response = await client.post('/collections/search_units_0924d58e249b4502b86dfdb9/points/count', json={'exact': True})
                row['http_status'] = response.status_code
                row['count'] = response.json().get('result', {}).get('count')
            except Exception as error:
                row['exception_type'] = type(error).__name__
                row['message_is_empty'] = not bool(str(error))
            row['seconds'] = time.perf_counter()-start
            report['measurements'].append(row)
            print(json.dumps(row), flush=True)

        async def block_loop(index):
            await asyncio.sleep(.02)
            start = time.perf_counter()
            graph_payload(units)
            report['graph_seconds'].append(time.perf_counter()-start)
            print('graph completed', index, flush=True)

        await probe('idle_baseline')
        await asyncio.gather(probe('during_two_graph_tasks'), block_loop(0), block_loop(1))
        await probe('idle_after')
    (ROOT/'qdrant_read_reproduction.json').write_text(json.dumps(report, indent=2), encoding='utf-8')


asyncio.run(main())
