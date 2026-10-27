"""Read persisted benchmark inputs and measure graph CPU without writing application data."""
import asyncio
import copy
import cProfile
import json
import os
from pathlib import Path
import pstats
import sys
import time

from sqlalchemy import select, text
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parent
SAG = Path('D:/DoAnTotnghiep/sag-laya-integration/SAG')
os.chdir(SAG)
sys.path.insert(0, str(SAG / 'apps/api'))
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
    assert len(units) == 677
    results = {'units': len(units), 'database_writes': 0, 'measurements': []}
    lag = []
    stopped = False

    async def heartbeat():
        while not stopped:
            start = time.perf_counter()
            await asyncio.sleep(.02)
            lag.append(max(0, time.perf_counter() - start - .02))

    ticker = asyncio.create_task(heartbeat())
    await asyncio.sleep(.05)
    for name, inputs in [('actual_dense', units), ('same_units_without_dense', [copy.copy(u) for u in units])]:
        if name == 'same_units_without_dense':
            for unit in inputs:
                unit.features_json = {**unit.features_json, 'dense': []}
        before = len(lag)
        start, cpu = time.perf_counter(), time.process_time()
        payload = graph_payload(inputs)
        measurement = {'mode': name, 'wall_seconds': time.perf_counter()-start,
                       'cpu_seconds': time.process_time()-cpu, 'edges': len(payload['edges']),
                       'candidate_pairs': sum(c['pair_count'] for c in payload['calibrations'].values())}
        await asyncio.sleep(.05)
        measurement['max_event_loop_lag_seconds'] = max(lag[before:], default=0)
        results['measurements'].append(measurement)
        (ROOT/'graph_measurements.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
        print(json.dumps(measurement), flush=True)
    stopped = True
    await ticker
    profiler = cProfile.Profile()
    profiler.runcall(graph_payload, units[:128])
    profiler.dump_stats(str(ROOT/'graph_128.prof'))
    with (ROOT/'graph_profile.txt').open('w', encoding='utf-8') as output:
        pstats.Stats(profiler, stream=output).sort_stats('cumulative').print_stats(18)
    print('Profile saved; no application data changed.', flush=True)


asyncio.run(main())
