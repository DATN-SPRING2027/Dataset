"""Dataset I/O only; ingestion, workers, retrieval and generation belong to SAG.

Architectural Note — E2 LLM Enrichment Removed (2026-10-29):
------------------------------------------------------------
Benchmark and E2E runs enforce full Phase 5A FOUNDATION (`E0/E1` deterministic extraction +
`DenseGraph` embeddings + `Leiden` routing tree) with clean PostgreSQL + Qdrant isolation.
Phase 5B E2 LLM enrichment (`KnowledgeJob.kind == "E2"`) was permanently removed after
controlled A/B evaluation on the 81-file / 50-question RetrievalCI benchmark proved E2
yielded 0 recall gain (99.17% -> 99.17%), degraded overall score (93.64 -> 93.42), reduced
precision (80.73% -> 80.00%) and abstention (100% -> 80%), while adding 151,435 unnecessary
LLM tokens (+242% ingestion cost). See `sag-laya-integration/SAG/docs/adr-remove-e2-llm-enrichment.md`.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
import socket
import sys
import time
import unicodedata
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

import httpx
import uvicorn
from sqlalchemy import func, select, text
from starlette.requests import Request


def frontend_policy(sag_root: Path) -> dict:
    web = sag_root / 'apps/web'
    api = (web / 'lib/api.ts').read_text(encoding='utf-8')
    state = (web / 'components/features/search/search-state.ts').read_text(encoding='utf-8')

    def constant(source, name):
        match = re.search(rf'\b{re.escape(name)}\s*=\s*([\d_]+)\s*;', source)
        if not match:
            raise ValueError(f'Cannot resolve current frontend policy: {name}')
        return int(match[1].replace('_', ''))

    return {
        'top_k': constant(state, 'DEFAULT_SEARCH_TOP_K'),
        'load_more_step': constant(state, 'DEFAULT_SEARCH_TOP_K'),
        'first_result_seconds': constant(api, 'SEARCH_FIRST_RESULT_TIMEOUT_MS') / 1000,
        'stream_idle_seconds': constant(api, 'SEARCH_STREAM_IDLE_TIMEOUT_MS') / 1000,
        'stream_idle_activity': 'received data after result, including SSE ping comments',
    }


def configure_full_benchmark_settings(
    settings,
    *,
    require_dense_graph: bool = True,
) -> None:
    """Ensure Phase 5A FOUNDATION (`E0/E1` + full `DenseGraph` + `Leiden` tree) is enabled
    and configure RPM/TPM rate-limit protection for benchmark runs."""
    settings.knowledge_worker_enabled = True
    if hasattr(settings, 'knowledge_concurrency'):
        settings.knowledge_concurrency = max(int(settings.knowledge_concurrency or 4), 8)
    if hasattr(settings, 'knowledge_queue_capacity'):
        settings.knowledge_queue_capacity = max(int(settings.knowledge_queue_capacity or 256), 512)
    # Prevent extra SiliconFlow /systemone HTTP call per query (uses deterministic ECCE routing)
    if hasattr(settings, 'decision_provider'):
        settings.decision_provider = 'disabled'
    # Prevent SiliconFlow TPM pre-reservation spikes (reserve 512 output tokens instead of 4096/20000)
    if hasattr(settings, 'llm_max_tokens'):
        settings.llm_max_tokens = min(int(getattr(settings, 'llm_max_tokens', 512) or 512), 512)
    # Prevent LiteLLM internal burst retries from poisoning SiliconFlow's 60-second sliding RPM window
    if hasattr(settings, 'llm_max_retries'):
        settings.llm_max_retries = 0
    if require_dense_graph and not (
        getattr(settings, 'embedding_api_key', None) and getattr(settings, 'embedding_model', None)
    ):
        raise RuntimeError(
            'Full DenseGraph is required for SAG benchmarks; configure SAG_EMBEDDING_API_KEY and SAG_EMBEDDING_MODEL'
        )
    install_dual_key_llm_rate_limit_guard(settings)


def install_dual_key_llm_rate_limit_guard(settings) -> None:
    """Install round-robin dual-key rotation + failover retry on LLMClient._create_completion."""
    keys = [
        k for k in dict.fromkeys([
            getattr(settings, 'llm_api_key', None),
            getattr(settings, 'embedding_api_key', None),
            getattr(settings, 'siliconflow_api_key', None),
        ])
        if isinstance(k, str) and k.strip().startswith('sk-')
    ]
    if not keys:
        return

    try:
        from sag_api.generation.llm import LLMClient
    except ImportError:
        api_dir = Path(__file__).resolve().parents[1] / 'sag-laya-integration/SAG/apps/api'
        if api_dir.is_dir() and str(api_dir) not in sys.path:
            sys.path.insert(0, str(api_dir))
        try:
            from sag_api.generation.llm import LLMClient
        except ImportError:
            return

    if getattr(LLMClient._create_completion, '_sag_rate_limit_guarded', False):
        return

    orig_create = LLMClient._create_completion
    state = {
        'idx': 0,
        'cooldown_until': {k: 0.0 for k in keys},
        'lock': asyncio.Lock(),
    }

    async def _guarded_create_completion(self, messages, **kwargs):
        self._settings.llm_max_tokens = min(int(getattr(self._settings, 'llm_max_tokens', 512) or 512), 512)
        self._settings.llm_max_retries = 0
        last_err = None
        for attempt in range(1, 6):
            async with state['lock']:
                now = time.perf_counter()
                # Pick next key not in cooldown, or the key whose cooldown expires soonest
                chosen_key = None
                for _ in range(len(keys)):
                    candidate = keys[state['idx'] % len(keys)]
                    state['idx'] += 1
                    if state['cooldown_until'].get(candidate, 0.0) <= now:
                        chosen_key = candidate
                        break
                if chosen_key is None:
                    chosen_key = min(keys, key=lambda k: state['cooldown_until'].get(k, 0.0))
                wait_s = max(0.0, state['cooldown_until'].get(chosen_key, 0.0) - now)
            if wait_s > 0:
                await asyncio.sleep(wait_s)
            self._settings.llm_api_key = chosen_key
            try:
                return await orig_create(self, messages, **kwargs)
            except Exception as err:
                last_err = err
                err_str = str(err).lower()
                if any(tok in err_str for tok in ('ratelimit', 'rate limit', '429', 'rpm', 'tpm', 'timeout', '503')):
                    cooldown = 8.0 * attempt
                    async with state['lock']:
                        state['cooldown_until'][chosen_key] = time.perf_counter() + cooldown
                    print(
                        f'[LLM-RateGuard] Transient {type(err).__name__} on key[{keys.index(chosen_key)}], '
                        f'switching key & cooling {cooldown:.1f}s (attempt {attempt}/5)...',
                        flush=True,
                    )
                    if attempt > 1:
                        await asyncio.sleep(min(3.0 * attempt, 10.0))
                    continue
                raise
        raise last_err

    _guarded_create_completion._sag_rate_limit_guarded = True
    LLMClient._create_completion = _guarded_create_completion


def clear_in_memory_sag_caches() -> None:
    """Clear process-local retrieval/embedding/tree caches before a fresh benchmark or E2E run."""
    modules_and_attrs = (
        ('sag_api.services.search_index_service', '_SHARED_TEXT_EMBEDDING_CACHE'),
        ('sag_api.services.search_unit_retrieval_service', '_SCOPE_KNOWLEDGE_INDEX_CACHE'),
        ('sag_api.services.tree_routing_service', '_VERIFIED_TREE_MANIFEST_CACHE'),
        ('sag_api.services.universe_knowledge_service', '_SNAPSHOT_MEMBERSHIP_CACHE'),
        ('sag_api.services.universe_knowledge_service', '_MANIFEST_TREE_OUTPUT_CACHE'),
    )
    for mod_name, attr_name in modules_and_attrs:
        mod = sys.modules.get(mod_name)
        if mod is None:
            continue
        cache = getattr(mod, attr_name, None)
        if hasattr(cache, 'clear'):
            cache.clear()
    try:
        from sag_api.core.token_usage import reset_runtime_token_usage

        reset_runtime_token_usage()
    except Exception:
        pass


class SAGBenchmark:
    def __init__(
        self,
        run,
        sag_root: Path,
        *,
        require_dense_graph: bool = True,
    ):
        self.run = run
        self.policy = frontend_policy(sag_root)
        self.documents = {}
        self.require_dense_graph = require_dense_graph

    @asynccontextmanager
    async def serve(self):
        from sag_api.core.config import settings
        from sag_api.core.db import SessionLocal, engine
        from sag_api.jobs.knowledge import KnowledgeWorker
        from sag_api.main import app

        require_dense_graph = getattr(self, 'require_dense_graph', True)
        configure_full_benchmark_settings(
            settings,
            require_dense_graph=require_dense_graph,
        )
        clear_in_memory_sag_caches()
        await self.run.validate_data_scope(engine)
        # A real socket is required: ASGITransport buffers SSE and hides first-result timeouts.
        sock = socket.socket()
        sock.bind(('127.0.0.1', 0))
        self.base_url = f'http://127.0.0.1:{sock.getsockname()[1]}'
        server = uvicorn.Server(uvicorn.Config(app, log_level='warning', access_log=False,
                                              lifespan='off', timeout_graceful_shutdown=5))
        try:
            async with app.router.lifespan_context(app):
                self.app = app
                configure_full_benchmark_settings(
                    settings,
                    require_dense_graph=require_dense_graph,
                )
                if '--skip-index' not in sys.argv and hasattr(self.run, 'clean_qdrant_and_uploads'):
                    qdrant = await app.state.engine_manager.get_search_unit_qdrant_client()
                    await self.run.clean_qdrant_and_uploads(qdrant, settings.upload_dir)
                task = asyncio.create_task(server.serve(sockets=[sock]))
                try:
                    while not server.started:
                        if task.done():
                            await task
                            raise RuntimeError('Benchmark HTTP server did not start')
                        await asyncio.sleep(.05)
                    async with httpx.AsyncClient(base_url=self.base_url, timeout=30, trust_env=False) as client:
                        self.client = client
                        await self.login()
                        from benchmark_http_client import QueryClientProcess

                        self.query_client = QueryClientProcess(self.base_url)
                        worker = getattr(app.state, 'knowledge_worker', None) or KnowledgeWorker(SessionLocal, settings)
                        if not settings.knowledge_worker_enabled:
                            raise RuntimeError('The actual SAG knowledge worker is disabled')
                        dense_graph_enabled = bool(settings.embedding_api_key and settings.embedding_model)
                        if require_dense_graph and not dense_graph_enabled:
                            raise RuntimeError('Full DenseGraph embeddings are disabled in SAG benchmark runtime')
                        self.run.manifest['execution'] = {
                            'ingestion': 'HTTP POST /api/v1/projects/{project_id}/documents/upload',
                            'transport': 'loopback HTTP /api/v1/search/stream; separate client process',
                            'http_client_pid': self.query_client.process.pid,
                            'foundation_timeout_seconds': worker.foundation_timeout,
                            'runtime': 'sag_api.main.lifespan (FOUNDATION E0/E1 + full DenseGraph + Leiden tree; E2 enrichment removed)',
                            'authentication': 'Continuum BFF service context on project upload; scoped SAG session on search',
                            'query_replays': 0,
                            'frontend': self.policy,
                            'knowledge_queue': worker.policy.model_dump(mode='json'),
                            'dense_graph_enabled': dense_graph_enabled,
                            'require_dense_graph': require_dense_graph,
                            'e2_enabled': False,
                            'debug_logging': settings.debug,
                            'embedding_timeout_seconds': settings.embedding_timeout,
                            'llm_timeout_seconds': settings.llm_timeout_ms / 1000,
                            'llm_max_retries': settings.llm_max_retries,
                            'embedding_model': settings.embedding_model,
                            'document_event_extraction_enabled': settings.document_event_extraction_enabled,
                            'llm_model': settings.llm_model,
                        }
                        self.run._write_manifest()
                        yield self
                finally:
                    if getattr(self, 'query_client', None) is not None:
                        await self.query_client.close()
                    server.should_exit = True
                    await task
        finally:
            sock.close()

    async def login(self):
        from sag_api.core.config import settings
        from sag_api.core.principal_assertion import require_project_read_principal
        raw_name = str(self.run.manifest.get('user_name') or 'Continuum User')
        ascii_name = (
            unicodedata.normalize('NFKD', raw_name)
            .encode('ascii', 'ignore')
            .decode('ascii')
            .strip()
            or 'Continuum User'
        )
        response = await self.client.post('/api/v1/auth/continuum-login', headers={
            'X-SAG-BFF-Service-Token': settings.bff_service_token or '',
            'X-Continuum-User-Id': self.run.user_id,
            'X-Continuum-Name': ascii_name,
            'X-Continuum-Organization-Id': self.run.organization_id,
            'X-Continuum-Project-Id': self.run.project_id,
        }, json={'displayName': raw_name})
        response.raise_for_status()
        self.authorization = f"Bearer {response.json()['access_token']}"
        request = Request({'type': 'http', 'headers': [(b'authorization', self.authorization.encode())]})
        self.principal = await require_project_read_principal(request)

    async def ingest(self, files: list[Path], *, logical_source_ids: dict[Path, str] | None = None):
        from sag_api.core.config import settings
        from sag_api.core.db import SessionLocal
        p = self.principal
        if self.run.project_id not in p.allowed_project_ids or self.run.project_id not in p.allowed_partition_ids:
            raise PermissionError('Benchmark project is outside the authenticated scope')
        for index, path in enumerate(files, 1):
            suffix = path.suffix.lower()
            content_type = (
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                if suffix == '.docx'
                else 'text/markdown'
            )
            logical_id = (
                logical_source_ids[path]
                if logical_source_ids and path in logical_source_ids
                else path.relative_to(self.run.root).as_posix()
            )
            response = await self.client.post(
                f'/api/v1/projects/{self.run.project_id}/documents/upload',
                headers={
                    'X-SAG-BFF-Service-Token': settings.bff_service_token or '',
                    'X-Continuum-User-Id': getattr(self.run, 'user_id', getattr(p, 'subject', '')),
                    'X-Continuum-Organization-Id': self.run.organization_id,
                    'X-Continuum-Project-Id': self.run.project_id,
                    'X-Continuum-Security-Partition': self.run.project_id,
                    'Idempotency-Key': f'{self.run.id}-{index}',
                },
                data={'logical_source_id': logical_id},
                files={'file': (path.name, path.read_bytes(), content_type)},
            )
            response.raise_for_status()
            uploaded = response.json()
            if response.status_code != 201 or uploaded.get('is_duplicate'):
                raise RuntimeError('Fresh E2E ingestion unexpectedly reused a document')
            document_id = uploaded['document_id']
            self.documents[document_id] = logical_id
            if index == 1:
                project_name = getattr(self.run, 'project_name', None) or f'Project {self.run.project_id}'
                async with SessionLocal() as session:
                    source = (await session.execute(text('''SELECT s.id,s.sag_source_config_id FROM sources s
                        JOIN documents d ON d.source_id=s.id WHERE d.id=:id'''), {'id': document_id})).one()
                    if project_name:
                        await session.execute(
                            text(
                                'UPDATE sources SET name=:name, description=:desc WHERE id=:id'
                            ),
                            {
                                'id': source.id,
                                'name': project_name,
                                'desc': f'{project_name} (project {self.run.project_id}, tenant {self.run.organization_id})',
                            },
                        )
                        await session.commit()
                self.run.source_id, self.run.source_config_id = source
                self.run.manifest.update(
                    source_id=source.id,
                    source_config_id=source.sag_source_config_id,
                    project_name=project_name,
                )
                async with self.run.registry.begin() as conn:
                    await conn.execute(text('UPDATE benchmark_runs SET source_id=:source WHERE id=:id'),
                                       {'source': source.id, 'id': self.run.id})
            if index % 10 == 0 or index == len(files):
                self.run.manifest['document_paths'] = self.documents
                self.run._write_manifest()
                await self.run.checkpoint({'stage': 'upload', 'uploaded': len(self.documents)})
                print(f'Uploaded {index}/{len(files)} through SAG upload API', flush=True)

    async def reuse_documents(self, files: list[Path], *, logical_source_ids: dict[Path, str] | None = None):
        from sag_api.core.db import SessionLocal
        expected = {
            (
                logical_source_ids[p]
                if logical_source_ids and p in logical_source_ids
                else p.relative_to(self.run.root).as_posix()
            ): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in files
        }
        project_name = getattr(self.run, 'project_name', None)
        async with SessionLocal() as session:
            rows = (await session.execute(text('''SELECT d.id,d.logical_source_id,v.file_hash
                FROM documents d JOIN document_versions v ON v.document_id=d.id
                WHERE d.project_id=:project AND d.tenant_id=:tenant AND d.source_id=:source'''),
                {'project': self.run.project_id, 'tenant': self.run.organization_id, 'source': self.run.source_id})).all()
            if project_name and self.run.source_id:
                await session.execute(
                    text('UPDATE sources SET name=:name, description=:desc WHERE id=:id'),
                    {
                        'id': self.run.source_id,
                        'name': project_name,
                        'desc': f'{project_name} (project {self.run.project_id}, tenant {self.run.organization_id})',
                    },
                )
                await session.commit()
        actual = {r.logical_source_id: r.file_hash for r in rows}
        if actual != expected or len(rows) != len(files):
            raise ValueError('Reused corpus content/identity differs from the supplied dataset')
        self.documents = {r.id: r.logical_source_id for r in rows}
        self.run.manifest['document_paths'] = self.documents
        self.run.manifest['ingestion_reused'] = True
        if os.getenv('SAG_BENCHMARK_REUSE_RUN_ID'):
            self.run.manifest['ingestion_reused_from_run_id'] = os.environ['SAG_BENCHMARK_REUSE_RUN_ID']
            self.run.manifest['ingestion_reuse_manifest_sha256'] = os.environ.get('SAG_BENCHMARK_REUSE_MANIFEST_SHA256')
        self.run._write_manifest()

    async def state(self):
        from sag_api.core.db import SessionLocal
        from sag_api.db.models import (
            Job,
            KnowledgeGraphBuild,
            KnowledgeUnit,
            KnowledgeUnitEdge,
        )
        from sag_api.enums import JobType

        params = {'project': self.run.project_id, 'tenant': self.run.organization_id,
                  'now': datetime.now(timezone.utc)}
        async with SessionLocal() as session:
            versions = (await session.execute(text('''SELECT d.id,d.status,v.search_status,v.knowledge_status
                FROM documents d JOIN document_versions v ON v.document_id=d.id
                WHERE d.project_id=:project AND d.tenant_id=:tenant'''), params)).mappings().all()
            jobs = (await session.execute(text('''SELECT j.kind,j.status,j.error_code,count(*) AS count,
                max(j.attempts) AS attempts FROM knowledge_jobs j JOIN document_versions v ON v.id=j.document_version_id
                JOIN documents d ON d.id=v.document_id WHERE d.project_id=:project AND d.tenant_id=:tenant
                GROUP BY j.kind,j.status,j.error_code'''), params)).mappings().all()
            unit_features = (
                await session.scalars(
                    select(KnowledgeUnit.features_json).where(
                        KnowledgeUnit.project_id == self.run.project_id,
                        KnowledgeUnit.tenant_id == self.run.organization_id,
                        KnowledgeUnit.is_current.is_(True),
                    )
                )
            ).all()
            total_units = len(unit_features)
            with_dense = sum(
                1 for feat in unit_features if isinstance((feat or {}).get('dense'), list) and len(feat['dense']) > 0
            )
            units_summary = {
                'total': total_units,
                'with_dense': with_dense,
            }
            tiers = (await session.execute(text('''SELECT e.tier,count(*) AS count FROM knowledge_evidence e
                JOIN knowledge_units u ON u.id=e.unit_id WHERE u.project_id=:project AND u.tenant_id=:tenant
                AND u.is_current=true GROUP BY e.tier'''), params)).all()
            tree = (await session.execute(text('''SELECT status,tree_version,manifest_json FROM tree_manifests
                WHERE project_id=:project'''), params)).mappings().all()
            current_units = (await session.execute(text('''SELECT u.id,u.checksum FROM knowledge_units u
                JOIN document_versions v ON v.id=u.document_version_id
                JOIN documents d ON d.id=v.document_id
                WHERE u.project_id=:project AND u.tenant_id=:tenant AND u.is_current=true
                AND d.is_active=true AND v.search_status IN ('READY','SEARCH_READY')
                AND v.search_ready_at IS NOT NULL AND v.knowledge_status='DATA_READY'
                AND v.valid_from <= :now AND v.valid_to > :now ORDER BY u.id'''), params)).all()
            inputs = [[row.id, row.checksum] for row in current_units]
            matching_active_trees = [
                row
                for row in tree
                if row['status'] == 'ACTIVE' and (row['manifest_json'] or {}).get('knowledge_inputs') == inputs
            ]
            tree_matches_current = bool(inputs) and bool(matching_active_trees)
            active_tree_row = matching_active_trees[-1] if matching_active_trees else next(
                (row for row in tree if row['status'] == 'ACTIVE'), None
            )
            active_build_id = (
                ((active_tree_row['manifest_json'] or {}).get('knowledge_graph_build_id'))
                if active_tree_row is not None
                else None
            )
            total_edges = 0
            semantic_dense_edges = 0
            if active_build_id:
                graph_build = await session.get(KnowledgeGraphBuild, active_build_id)
                total_edges = int(
                    (
                        await session.scalar(
                            select(func.count())
                            .select_from(KnowledgeUnitEdge)
                            .where(KnowledgeUnitEdge.build_id == active_build_id)
                        )
                    )
                    or 0
                )
                manifest_edges = ((graph_build.manifest_json or {}).get('edges') or []) if graph_build else []
                semantic_dense_edges = sum(
                    1
                    for edge in manifest_edges
                    if float(((edge or {}).get('signals') or {}).get('semantic') or 0.0) > 0.0
                )
            dense_graph_summary = {
                'build_id': active_build_id,
                'total_edges': total_edges,
                'semantic_dense_edges': semantic_dense_edges,
            }
            ingestion = (await session.execute(text('''SELECT d.status,count(*) AS count FROM documents d
                WHERE d.project_id=:project AND d.tenant_id=:tenant GROUP BY d.status'''), params)).all()
            project_jobs = (await session.execute(select(Job.status, Job.attempts, Job.error, Job.payload).where(
                Job.type == JobType.REBUILD_UNIVERSE_TREE,
                Job.payload['tenant_id'].as_string() == self.run.organization_id))).mappings().all()
            tree_jobs = [{'status': getattr(row['status'], 'value', row['status']),
                          'attempts': row['attempts'], 'error': row['error']}
                         for row in project_jobs if self.run.project_id in ((row['payload'] or {}).get('project_ids') or [])]
        return {
            'ready_versions': [dict(v) for v in versions],
            'jobs': [dict(j) for j in jobs],
            'units': units_summary,
            'evidence': dict(tiers),
            'dense_graph': dense_graph_summary,
            'tree': [{'status': t['status'], 'tree_version': t['tree_version']} for t in tree],
            'tree_matches_current': tree_matches_current,
            'tree_jobs': [dict(j) for j in tree_jobs],
            'ingestion': dict(ingestion),
        }

    async def wait_ready(self):
        previous = None
        require_dense_graph = getattr(self, 'require_dense_graph', False)
        while True:
            state = await self.state()
            summary = (
                state.get('ingestion'),
                state.get('units'),
                state.get('evidence'),
                state.get('dense_graph'),
                state.get('jobs'),
                state.get('tree'),
                state.get('tree_jobs'),
                state.get('tree_matches_current'),
            )
            if summary != previous:
                print('Pipeline:', json.dumps(summary, ensure_ascii=False), flush=True)
                previous = summary
            await self.run.checkpoint({'stage': 'processing'}, state)
            versions = state['ready_versions']
            ready = len(versions) == len(self.documents) and all(
                v['search_status'] in ('READY', 'SEARCH_READY') and v['knowledge_status'] == 'DATA_READY'
                for v in versions
            )
            active = any(j['status'] in ('QUEUED', 'RUNNING', 'RETRY') for j in state['jobs'])
            if state['ingestion'].get('FAILED'):
                raise RuntimeError('Real SAG ingestion failed; inspect retained document/job errors')
            if any(j['kind'] == 'FOUNDATION' and j['status'] in ('FAILED', 'EXPIRED') for j in state['jobs']):
                raise RuntimeError('Real SAG foundation job exhausted its retry policy')
            units = state.get('units') or {}
            tree_active_jobs = any(j['status'] in ('queued', 'running') for j in state['tree_jobs'])
            if (
                ready
                and not active
                and not state['tree_matches_current']
                and not tree_active_jobs
                and state['tree_jobs']
                and all(j['status'] in ('failed', 'canceled') for j in state['tree_jobs'])
            ):
                raise RuntimeError('Real SAG tree rebuild exhausted its retry policy; inspect retained job errors')
            if ready and not active and not tree_active_jobs and state['tree_matches_current']:
                total_units = int(units.get('total', 0) or 0)
                if require_dense_graph and total_units > 0:
                    with_dense = int(units.get('with_dense', 0) or 0)
                    if with_dense != total_units:
                        raise RuntimeError(
                            f'Full DenseGraph verification failed: only {with_dense}/{total_units} units have dense vectors'
                        )
                    dense_graph = state.get('dense_graph') or {}
                    if total_units > 1 and (
                        not dense_graph.get('build_id') or int(dense_graph.get('semantic_dense_edges', 0) or 0) <= 0
                    ):
                        raise RuntimeError(
                            f'Full DenseGraph verification failed: semantic_dense_edges={dense_graph.get("semantic_dense_edges", 0)}'
                        )
                self.run.manifest['pipeline'] = state
                self.run._write_manifest()
                return state
            await asyncio.sleep(1)

    async def token_usage_report(self) -> dict:
        await self.login()
        response = await self.client.get(
            f'/api/v1/projects/{self.run.project_id}/documents/token-usage',
            headers={'Authorization': self.authorization},
        )
        response.raise_for_status()
        return response.json()

    async def ask(self, query: str, *, top_k: int | None = 5, retrieval_only: bool = False) -> dict:
        from benchmark_http_client import measure_search

        min_interval_s = float(getattr(self, 'inter_query_delay_s', 1.5))
        last_ts = getattr(self, '_last_ask_completed_at', 0.0)
        elapsed = time.perf_counter() - last_ts
        if last_ts > 0 and elapsed < min_interval_s:
            await asyncio.sleep(min_interval_s - elapsed)

        default_attempts = 5 if float((getattr(self, 'policy', None) or {}).get('first_result_seconds', 30)) >= 1.0 else 1
        max_attempts = int(getattr(self, 'ask_max_attempts', default_attempts))
        base_backoff_s = float(getattr(self, 'retry_backoff_s', 10.0))

        measured = None
        for attempt in range(1, max_attempts + 1):
            await self.login()  # Short-lived SAG sessions must not expire during a full dataset run.
            options = dict(
                authorization=self.authorization,
                source_id=self.run.source_id,
                policy=self.policy,
                query=query,
                top_k=top_k,
                retrieval_only=retrieval_only,
            )
            remote = getattr(self, 'query_client', None)
            if remote is not None:
                measured = await remote.ask(options)
            else:
                measured = await measure_search(self.client, **options)
            self._last_ask_completed_at = time.perf_counter()

            resp = (measured or {}).get('response') or {}
            summary = str(resp.get('summary') or '')
            has_err = bool((measured or {}).get('error'))
            is_fallback = (not retrieval_only) and summary.startswith('Based on directly relevant evidence:')
            if not has_err and not is_fallback:
                return measured
            if attempt < max_attempts:
                backoff_s = base_backoff_s * attempt
                print(
                    f'[SAGBenchmark.ask] Rate-limit fallback/error detected (error={measured.get("error")}, '
                    f'fallback={is_fallback}); cooling {backoff_s:.1f}s before retry {attempt + 1}/{max_attempts}...',
                    flush=True,
                )
                await asyncio.sleep(backoff_s)
        return measured


from benchmark_http_client import parse_frame
