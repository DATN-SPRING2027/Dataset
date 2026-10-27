"""Demonstrate production-sized graph work delaying 30s/60s timers; no provider calls or DB writes."""
import asyncio
import json
import os
from pathlib import Path
import sys
import time

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
    report = {'units': len(units), 'database_writes': 0, 'provider_calls': 0,
              'graph_tasks': [], 'timers': []}

    async def timer(seconds):
        start = time.perf_counter()
        status = 'completed'
        try:
            async with asyncio.timeout(seconds):
                await asyncio.sleep(.1)
        except TimeoutError:
            status = 'TimeoutError'
        report['timers'].append({'deadline_seconds': seconds, 'intended_wait_seconds': .1,
                                 'actual_seconds': time.perf_counter()-start, 'status': status})

    async def graph(index):
        await asyncio.sleep(.02)
        start = time.perf_counter()
        graph_payload(units)
        report['graph_tasks'].append({'task': index, 'seconds': time.perf_counter()-start})
        print('graph', index, report['graph_tasks'][-1]['seconds'], flush=True)

    await asyncio.gather(timer(30), timer(60), *(graph(i) for i in range(3)))
    (ROOT/'loop_timeout_reproduction.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    assert len(report['graph_tasks']) == 3
    assert all(row['status'] == 'TimeoutError' for row in report['timers']), report
    print(json.dumps(report), flush=True)


asyncio.run(main())
