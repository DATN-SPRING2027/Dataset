"""Preserve the diagnostic run/checkpoints, explicitly marking it superseded."""
import asyncio
import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SAG = ROOT.parent / 'sag-laya-integration/SAG'
sys.path.insert(0, str(SAG/'apps/api'))
os.chdir(SAG)
from sag_api.core.config import settings
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

async def main(path):
    path = path.resolve()
    assert path.is_relative_to(ROOT/'reports') and path.name == 'run_manifest.json'
    manifest = json.loads(path.read_text(encoding='utf-8'))
    schema = manifest['schema']
    assert re.fullmatch(r'sag_bench_[a-z0-9_]+',schema)
    manifest.update(status='ABORTED', finished_at_utc=datetime.now(timezone.utc).isoformat(),
                    stop_reason='Superseded diagnostic/protocol run; corrected web idle contract and final workflow code require a new run. Corpus, index and partial checkpoints retained.')
    url = make_url(settings.database_url)
    engine = create_async_engine(url.set(query={k:v for k,v in url.query.items() if k != 'search_path'}))
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text(f'''UPDATE "{schema}".benchmark_runs
                SET status='ABORTED', finished_at=now(), error_type='SupersededDiagnostic',
                manifest_json=CAST(:manifest AS jsonb) WHERE id=:id AND status='RUNNING' '''),
                {'manifest':json.dumps(manifest,ensure_ascii=False),'id':manifest['run_id']})
            assert result.rowcount == 1
        path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
        (path.parents[1]/'private-connection.json').unlink(missing_ok=True)
        print('Diagnostic run ABORTED; documents, index and partial results preserved')
    finally:
        await engine.dispose()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('manifest',type=Path)
    asyncio.run(main(parser.parse_args().manifest))
