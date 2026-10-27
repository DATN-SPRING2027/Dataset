"""Persistent, project-scoped bookkeeping shared by the two SAG dataset runners."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine


class BenchmarkRun:
    def __init__(self, key: str, root: Path, database_url: str) -> None:
        self.key, self.root = key, root
        self.id = os.getenv('SAG_BENCHMARK_RUN_ID') or f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{uuid.uuid4().hex[:6]}"
        self.schema = os.getenv('SAG_BENCHMARK_SCHEMA', 'sag')
        if not re.fullmatch(r'[a-z_][a-z0-9_]{0,62}', self.schema):
            raise ValueError('Benchmark schema must be a valid PostgreSQL schema identifier')
        if self.schema != 'sag':
            raise ValueError('SAG benchmarks must use the application schema sag')
        self.project_id = os.getenv('SAG_BENCHMARK_PROJECT_ID') or uuid.uuid4().hex[:24]
        if not re.fullmatch(r'[a-fA-F0-9]{24}', self.project_id):
            raise ValueError('Benchmark project ID must be a 24-character identifier')
        self.user_id = os.getenv('SAG_BENCHMARK_USER_ID', '')
        self.organization_id = os.getenv('SAG_BENCHMARK_ORGANIZATION_ID', '')
        self.source_id = os.getenv('SAG_BENCHMARK_SOURCE_ID') or uuid.uuid4().hex[:24]
        self.mapping_id = uuid.uuid4().hex[:24]
        self.source_config_id = os.getenv('SAG_BENCHMARK_SOURCE_CONFIG_ID') or f'bench-{key}-{uuid.uuid4().hex[:12]}'
        self.collection = f'search_units_{self.project_id}'
        self.output_dir = Path(os.getenv('SAG_BENCHMARK_OUTPUT_DIR') or root / 'reports' / self.id).resolve()
        parsed = make_url(database_url)
        if parsed.drivername != 'postgresql+asyncpg':
            raise ValueError('Persistent SAG benchmarks require PostgreSQL')
        query = dict(parsed.query)
        search_path = query.pop('search_path', None)
        options = {'server_settings': {'search_path': search_path}} if search_path else {}
        self.registry = create_async_engine(parsed.set(query=query), connect_args=options, pool_pre_ping=True)
        self.database_url = parsed.set(query={**query, 'search_path': self.schema}).render_as_string(hide_password=False)
        self.started = False
        self.manifest: dict = {}

    async def start(self, corpus: list[Path], questions: Path, models: dict) -> None:
        if not self.user_id or not self.organization_id:
            raise ValueError('Set SAG_BENCHMARK_USER_ID and SAG_BENCHMARK_ORGANIZATION_ID to the existing account/scope')
        if '--skip-index' in sys.argv and not all(os.getenv('SAG_BENCHMARK_' + name) for name in ('SCHEMA', 'PROJECT_ID', 'SOURCE_ID', 'SOURCE_CONFIG_ID')):
            raise ValueError('--skip-index requires the schema, project ID, source ID and source config ID from a previous run manifest')
        self.output_dir.mkdir(parents=True, exist_ok=False)
        async with self.registry.begin() as connection:
            if await connection.scalar(text('SELECT current_schema()')) != self.schema:
                raise ValueError('Benchmark data must use the configured application schema; select the same schema explicitly')
            account = (await connection.execute(text('SELECT id,name,is_active FROM users WHERE id=:id'), {'id': self.user_id})).mappings().one_or_none()
            if not account or not account['is_active']:
                raise ValueError('Benchmark owner must be an existing active SAG account')
            existing = await connection.scalar(text('SELECT EXISTS(SELECT 1 FROM source_project_mappings WHERE project_id=:project)'), {'project': self.project_id})
            if '--skip-index' not in sys.argv and existing:
                raise ValueError('Benchmark project already has data; choose a fresh project or explicitly reuse its index')
            if '--skip-index' in sys.argv:
                mapping = await connection.scalar(text('SELECT organization_id FROM source_project_mappings WHERE project_id=:project AND source_id=:source'), {'project': self.project_id, 'source': self.source_id})
                if mapping != self.organization_id:
                    raise ValueError('Reused source does not belong to the benchmark organization/project')
            await connection.execute(text('''CREATE TABLE IF NOT EXISTS benchmark_runs (
                id varchar(64) PRIMARY KEY,
                benchmark_key varchar(64) NOT NULL,
                user_id varchar(36) NOT NULL REFERENCES users(id),
                organization_id varchar(64) NOT NULL,
                project_id varchar(64) NOT NULL,
                source_id varchar(36) NOT NULL,
                data_schema varchar(63) NOT NULL,
                qdrant_collection varchar(128) NOT NULL,
                status varchar(16) NOT NULL,
                started_at timestamptz NOT NULL DEFAULT now(),
                finished_at timestamptz,
                manifest_json jsonb NOT NULL,
                results_json jsonb,
                diagnostics_json jsonb,
                error_type varchar(128)
            )'''))
            question_lines = [line for line in questions.read_text(encoding='utf-8').splitlines() if line.strip()]
            self.manifest = {
                'run_id': self.id, 'benchmark': self.key, 'user_id': self.user_id,
                'user_name': account['name'], 'organization_id': self.organization_id,
                'project_id': self.project_id, 'source_id': self.source_id, 'schema': self.schema,
                'source_config_id': self.source_config_id,
                'collection': self.collection, 'documents': len(corpus), 'questions': len(question_lines),
                'questions_sha256': hashlib.sha256(questions.read_bytes()).hexdigest(),
                'corpus_sha256': {str(p.relative_to(self.root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in corpus},
                'started_at_utc': datetime.now(timezone.utc).isoformat(), 'models': models,
                'status': 'RUNNING', 'output_dir': str(self.output_dir),
                'environment': {'python': sys.version, 'platform': platform.platform(),
                                'cpu_count': os.cpu_count(), 'network': 'loopback API; remote model/Qdrant providers'},
                'harness_sha256': {
                    str(path): hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in (Path(sys.argv[0]).resolve(), Path(__file__).resolve(),
                                 Path(__file__).with_name('sag_benchmark_runtime.py'),
                                 Path(__file__).with_name('benchmark_http_client.py'),
                                 Path(__file__).with_name('benchmark_quality.py'),
                                 Path(__file__).with_name('international_references.json'))
                    if path.is_file()
                },
            }
            repository = Path(__file__).resolve().parents[1] / 'sag-laya-integration'
            self.manifest['git_commit'] = subprocess.check_output(['git', '-C', str(repository), 'rev-parse', 'HEAD'], text=True).strip()
            self.manifest['git_worktree_diff_sha256'] = hashlib.sha256(subprocess.check_output(
                ['git', '-C', str(repository), 'diff', '--binary', 'HEAD', '--', 'SAG/apps/api', 'SAG/apps/web'])).hexdigest()
            self.manifest['api_source_sha256'] = {
                path.relative_to(repository).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted((repository/'SAG/apps/api/sag_api').rglob('*.py'))
            }
            await connection.execute(text('''INSERT INTO benchmark_runs
                (id,benchmark_key,user_id,organization_id,project_id,source_id,data_schema,qdrant_collection,status,manifest_json)
                VALUES (:id,:key,:user,:org,:project,:source,:schema,:collection,'RUNNING',CAST(:manifest AS jsonb))'''),
                {'id': self.id, 'key': self.key, 'user': self.user_id, 'org': self.organization_id,
                 'project': self.project_id, 'source': self.source_id, 'schema': self.schema,
                 'collection': self.collection, 'manifest': json.dumps(self.manifest, ensure_ascii=False)})
        self.started = True
        self._write_manifest()
        print(f'RUN_ID={self.id} OWNER={self.user_id} PROJECT={self.project_id} SCHEMA={self.schema}', flush=True)

    async def validate_data_scope(self, engine) -> None:
        async with engine.connect() as connection:
            if await connection.scalar(text('SELECT current_schema()')) != self.schema:
                raise ValueError('Unexpected application data schema')
            if not await connection.scalar(text("SELECT to_regclass('documents')")):
                raise ValueError('Application database must be initialized before benchmarking')

    async def require_new_collection(self, client) -> None:
        response = await client.get(f'/collections/{self.collection}')
        if response.status_code != 404:
            raise ValueError('Benchmark collection already exists or cannot be checked; refusing to overwrite it')

    async def checkpoint(self, results, diagnostics=None) -> None:
        async with self.registry.begin() as connection:
            await connection.execute(text('''UPDATE benchmark_runs SET results_json=CAST(:results AS jsonb),
                diagnostics_json=CAST(:diagnostics AS jsonb) WHERE id=:id AND status='RUNNING' '''),
                {'id': self.id, 'results': json.dumps(results, ensure_ascii=False, allow_nan=False),
                 'diagnostics': json.dumps(diagnostics, ensure_ascii=False, allow_nan=False)})

    async def complete(self, results, diagnostics=None) -> None:
        await self.checkpoint(results, diagnostics)
        self.manifest.update(status='COMPLETED', finished_at_utc=datetime.now(timezone.utc).isoformat())
        async with self.registry.begin() as connection:
            await connection.execute(text('''UPDATE benchmark_runs SET status='COMPLETED',finished_at=now(),
                manifest_json=CAST(:manifest AS jsonb) WHERE id=:id AND status='RUNNING' '''),
                {'id': self.id, 'manifest': json.dumps(self.manifest, ensure_ascii=False)})
        self._write_manifest()

    async def fail(self, error: BaseException) -> None:
        if not self.started or self.manifest.get('status') != 'RUNNING':
            return
        self.manifest.update(status='FAILED', error_type=type(error).__name__, finished_at_utc=datetime.now(timezone.utc).isoformat())
        async with self.registry.begin() as connection:
            await connection.execute(text('''UPDATE benchmark_runs SET status='FAILED',finished_at=now(),
                error_type=:error,manifest_json=CAST(:manifest AS jsonb) WHERE id=:id AND status='RUNNING' '''),
                {'id': self.id, 'error': type(error).__name__, 'manifest': json.dumps(self.manifest, ensure_ascii=False)})
        self._write_manifest()

    async def close(self) -> None:
        await self.registry.dispose()

    def _write_manifest(self) -> None:
        (self.output_dir / 'run_manifest.json').write_text(json.dumps(self.manifest, ensure_ascii=False, indent=2), encoding='utf-8')
