"""Run the canonical dataset script unchanged in an isolated application schema."""
import asyncio,os,re,runpy,sys
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine
sag=Path('D:/DoAnTotnghiep/sag-laya-integration/SAG')
root=Path(__file__).resolve().parent
sys.path[:0]=[str(sag/'apps/api'),'D:/DoAnTotnghiep/Dataset']
os.chdir(sag)
from sag_api.core.config import settings
schema=os.environ['SAG_BENCHMARK_SCHEMA']
assert re.fullmatch(r'[a-z_][a-z0-9_]{0,62}',schema)
original=make_url(settings.database_url)
base=original.set(query={k:v for k,v in original.query.items() if k!='search_path'})
async def create_schema():
 admin=create_async_engine(base)
 async with admin.begin() as connection:
  await connection.execute(text(f'CREATE SCHEMA "{schema}"'))
 await admin.dispose()
asyncio.run(create_schema())
settings.database_url=base.set(query={'search_path':schema}).render_as_string(hide_password=False)
settings.data_dir=str(root/'engine')
settings.upload_dir=str(root/'uploads')
settings.dsh_connection_file=str(root/'private-connection.json')
from sag_api.core.db import engine,init_db,publish_lock_engine
async def initialize():
 await init_db()
 async with engine.begin() as connection:
  copied=await connection.execute(text(f'INSERT INTO "{schema}".users SELECT * FROM sag.users WHERE id=:id AND is_active=true'),{'id':os.environ['SAG_BENCHMARK_USER_ID']})
  assert copied.rowcount==1,'Existing active account required'
 await engine.dispose()
 await publish_lock_engine.dispose()
asyncio.run(initialize())
script=Path('D:/DoAnTotnghiep/Dataset/RetrievalCI_Bench_v0_2026/scripts/run_bench_v0_sag.py')
sys.argv=[str(script)]
try:
 runpy.run_path(str(script),run_name='__main__')
finally:
 Path(settings.dsh_connection_file).unlink(missing_ok=True)
