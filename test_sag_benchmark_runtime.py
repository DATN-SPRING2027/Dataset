import asyncio
import unittest
import os
import threading
import time
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from types import SimpleNamespace
from collections import namedtuple

from sag_benchmark_runtime import (
    SAGBenchmark,
    configure_full_benchmark_settings,
    frontend_policy,
    parse_frame,
)


class RuntimeContractTests(unittest.IsolatedAsyncioTestCase):
    async def test_ping_after_result_keeps_idle_alive_like_the_web_client(self):
        from benchmark_http_client import measure_search

        class Response:
            def raise_for_status(self): pass
            async def aiter_lines(self):
                yield 'event: result'
                yield 'data: {"sections":[]}'
                yield ''
                for _ in range(8):
                    await asyncio.sleep(.015)
                    yield ': ping'
                    yield ''
                yield 'event: completed'
                yield 'data: {"answer_status":"answered"}'
                yield ''
        class Stream:
            async def __aenter__(self): return Response()
            async def __aexit__(self,*args): pass
        class Client:
            def stream(self,*args,**kwargs): return Stream()

        measured = await measure_search(Client(), 'auth', 'source',
            {'first_result_seconds':.05, 'stream_idle_seconds':.05}, 'q')
        self.assertIsNone(measured['error'])
        self.assertEqual(measured['response']['answer_status'], 'answered')
        self.assertGreater(measured['latency_ms'],100)

    async def test_pipeline_probe_reads_mapped_job_payload_and_filters_project(self):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'sag-laya-integration/SAG/apps/api'))
        from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
        from sag_api.core import db
        from sag_api.db.base import Base
        from sag_api.db.models import Job
        from sag_api.enums import JobStatus, JobType

        engine = create_async_engine('sqlite+aiosqlite:///:memory:')
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            async with sessions() as session:
                for project in ('project', 'other-project'):
                    session.add(Job(type=JobType.REBUILD_UNIVERSE_TREE, status=JobStatus.FAILED,
                                    payload={'tenant_id':'tenant','project_ids':[project]}, error='TimeoutError'))
                await session.commit()
            runtime = SAGBenchmark.__new__(SAGBenchmark)
            runtime.run = SimpleNamespace(project_id='project', organization_id='tenant')
            with patch.object(db, 'SessionLocal', sessions):
                state = await runtime.state()
            self.assertEqual(len(state['tree_jobs']), 1)
            self.assertEqual(state['tree_jobs'][0]['status'], JobStatus.FAILED.value)
        finally:
            await engine.dispose()

    async def test_exhausted_tree_job_fails_readiness_instead_of_waiting_forever(self):
        runtime = SAGBenchmark.__new__(SAGBenchmark)
        runtime.documents = {'doc':'path'}
        runtime.run = SimpleNamespace(checkpoint=AsyncMock())
        runtime.state = AsyncMock(return_value={
            'ingestion':{'READY':1}, 'units':{'total':1}, 'jobs':[], 'tree':[],
            'tree_jobs':[{'status':'failed'}], 'tree_matches_current':False,
            'ready_versions':[{'search_status':'SEARCH_READY','knowledge_status':'DATA_READY'}]})
        with self.assertRaisesRegex(RuntimeError, 'tree rebuild exhausted'):
            await runtime.wait_ready()

    async def test_readiness_waits_for_matching_tree_and_running_tree_jobs(self):
        runtime = SAGBenchmark.__new__(SAGBenchmark)
        runtime.documents = {'doc': 'path'}
        runtime.run = SimpleNamespace(checkpoint=AsyncMock(), manifest={}, _write_manifest=MagicMock())
        base = {'ingestion': {'READY': 1}, 'units': {'total': 1}, 'jobs': [],
                'tree': [{'status': 'ACTIVE'}],
                'ready_versions': [{'search_status': 'SEARCH_READY', 'knowledge_status': 'DATA_READY'}]}
        stale = {**base, 'tree_matches_current': False, 'tree_jobs': [{'status': 'succeeded'}]}
        building = {**base, 'tree_matches_current': True, 'tree_jobs': [{'status': 'running'}]}
        current = {**base, 'tree_matches_current': True, 'tree_jobs': [{'status': 'succeeded'}]}
        runtime.state = AsyncMock(side_effect=[stale, building] + [current] * 6)
        with patch('sag_benchmark_runtime.asyncio.sleep', new_callable=AsyncMock):
            result = await runtime.wait_ready()
        self.assertTrue(result['tree_matches_current'])
        self.assertEqual(runtime.state.await_count, 3)

    async def test_failed_foundation_job_fails_readiness_closed(self):
        runtime = SAGBenchmark.__new__(SAGBenchmark)
        runtime.documents = {'doc': 'path'}
        runtime.run = SimpleNamespace(checkpoint=AsyncMock())
        runtime.state = AsyncMock(return_value={
            'ingestion': {'READY': 1}, 'units': {'total': 1, 'with_dense': 1},
            'jobs': [{'kind': 'FOUNDATION', 'status': 'FAILED', 'error_code': 'TimeoutError'}],
            'tree': [{'status': 'ACTIVE'}], 'tree_jobs': [], 'tree_matches_current': True,
            'ready_versions': [{'search_status': 'SEARCH_READY', 'knowledge_status': 'DATA_READY'}],
        })
        with self.assertRaisesRegex(RuntimeError, 'foundation job exhausted'):
            await runtime.wait_ready()

    async def test_upload_uses_project_http_api(self):
        import tempfile
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'sag-laya-integration/SAG/apps/api'))
        from sag_api.core import db

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            file = root / 'document.md'
            file.write_text('Example document', encoding='utf-8')
            source = namedtuple('SourceRow', 'id sag_source_config_id')('source', 'config')
            session = MagicMock()
            query = MagicMock()
            query.one.return_value = source
            session.execute = AsyncMock(return_value=query)
            session.commit = AsyncMock()
            session_context = MagicMock()
            session_context.__aenter__ = AsyncMock(return_value=session)
            session_context.__aexit__ = AsyncMock(return_value=False)
            registry_context = MagicMock()
            registry_context.__aenter__ = AsyncMock(return_value=SimpleNamespace(execute=AsyncMock()))
            registry_context.__aexit__ = AsyncMock(return_value=False)
            registry = MagicMock()
            registry.begin.return_value = registry_context
            run = SimpleNamespace(project_id='project', organization_id='tenant', id='run', root=root,
                                  registry=registry, manifest={}, _write_manifest=MagicMock(),
                                  checkpoint=AsyncMock())
            runtime = SAGBenchmark.__new__(SAGBenchmark)
            runtime.run = run
            runtime.documents = {}
            runtime.authorization = 'Bearer token'
            runtime.principal = SimpleNamespace(allowed_project_ids={'project'}, allowed_partition_ids={'project'},
                                                tenant_id='tenant', organization_id='tenant', subject='user')
            response = MagicMock(status_code=201)
            response.json.return_value = {'document_id': 'doc', 'is_duplicate': False}
            runtime.client = SimpleNamespace(post=AsyncMock(return_value=response))
            with patch.object(db, 'SessionLocal', return_value=session_context):
                await runtime.ingest([file])
            call = runtime.client.post.await_args
            self.assertEqual(call.args[0], '/api/v1/projects/project/documents/upload')
            self.assertEqual(call.kwargs['data']['logical_source_id'], 'document.md')
            self.assertEqual(call.kwargs['files']['file'][1], b'Example document')
            self.assertEqual(runtime.documents, {'doc': 'document.md'})

    async def test_query_process_deadline_survives_parent_loop_stall(self):
        from benchmark_http_client import QueryClientProcess

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                self.rfile.read(int(self.headers.get('Content-Length', '0')))
                self.send_response(200)
                self.send_header('Content-Type', 'text/event-stream')
                self.end_headers()
                self.wfile.write(b': ping\n\n')
                self.wfile.flush()
                time.sleep(.3)
                self.close_connection = True

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        remote = QueryClientProcess(f'http://127.0.0.1:{server.server_port}')
        options = dict(authorization='test', source_id='source', query='q',
                       policy={'first_result_seconds': .08, 'stream_idle_seconds': .1})
        try:
            await remote.ask(options)
            request = asyncio.create_task(remote.ask(options))
            await asyncio.sleep(.02)
            time.sleep(.4)
            result = await request
            self.assertEqual(result['error']['code'], 'TimeoutError')
            self.assertLess(result['latency_ms'], 300)
            self.assertNotEqual(result['http_client_pid'], os.getpid())
        finally:
            await remote.close()
            await asyncio.to_thread(server.shutdown)
            server.server_close()

    def test_reads_current_ui_contract(self):
        policy = frontend_policy(Path(__file__).resolve().parents[1] / 'sag-laya-integration/SAG')
        self.assertEqual(policy['top_k'], 5)
        self.assertGreater(policy['load_more_step'], 0)
        self.assertGreater(policy['stream_idle_seconds'], 0)

    def test_sse_comments_are_not_results(self):
        self.assertEqual(parse_frame([': ping']), ('', None))
        self.assertEqual(parse_frame(['event: result', 'data: {"sections": []}']),
                         ('result', {'sections': []}))

    async def test_ping_does_not_extend_first_result_deadline(self):
        class Response:
            def raise_for_status(self):
                pass

            async def aiter_lines(self):
                while True:
                    yield ': ping'
                    yield ''
                    await asyncio.sleep(.001)

        class Stream:
            async def __aenter__(self):
                return Response()

            async def __aexit__(self, *args):
                pass

        class Client:
            def stream(self, *args, **kwargs):
                return Stream()

        class Run:
            source_id = 'source'

        runtime = SAGBenchmark.__new__(SAGBenchmark)
        runtime.run = Run()
        runtime.client = Client()
        runtime.authorization = 'test'
        runtime.login = AsyncMock()
        runtime.policy = {'top_k': 12, 'first_result_seconds': .02, 'stream_idle_seconds': .04}
        result = await runtime.ask('question')
        self.assertEqual(result['error']['code'], 'TimeoutError')
        self.assertIsNone(result['response'])
        self.assertLess(result['latency_ms'], 1000)

    def test_configure_full_benchmark_settings_enforces_foundation_dense_graph_without_e2(self):
        cfg = SimpleNamespace(
            knowledge_worker_enabled=False,
            knowledge_concurrency=4,
            knowledge_queue_capacity=256,
            embedding_api_key='emb-key',
            embedding_model='Qwen/Qwen3-Embedding-0.6B',
        )
        configure_full_benchmark_settings(cfg)
        self.assertTrue(cfg.knowledge_worker_enabled)
        self.assertEqual(cfg.knowledge_concurrency, 8)
        self.assertEqual(cfg.knowledge_queue_capacity, 512)
        self.assertFalse(hasattr(cfg, 'knowledge_e2_url'))

        missing_dense = SimpleNamespace(
            knowledge_worker_enabled=True,
            embedding_api_key='',
            embedding_model='',
        )
        with self.assertRaisesRegex(RuntimeError, 'Full DenseGraph is required'):
            configure_full_benchmark_settings(missing_dense)

    async def test_full_dense_graph_readiness_gate_verifies_vectors_and_edges(self):
        runtime = SAGBenchmark.__new__(SAGBenchmark)
        runtime.require_dense_graph = True
        runtime.documents = {f'doc-{i}': f'doc-{i}.md' for i in range(8)}
        runtime.run = SimpleNamespace(checkpoint=AsyncMock(), manifest={}, _write_manifest=MagicMock())
        versions = [{'search_status': 'SEARCH_READY', 'knowledge_status': 'DATA_READY'} for _ in range(8)]

        running_foundation = {
            'ingestion': {'READY': 8},
            'units': {'total': 20, 'with_dense': 20},
            'evidence': {'E0': 10, 'E1': 30},
            'dense_graph': {'build_id': 'g1', 'total_edges': 50, 'semantic_dense_edges': 40},
            'jobs': [{'kind': 'FOUNDATION', 'status': 'RUNNING', 'count': 1}],
            'tree': [{'status': 'ACTIVE', 'tree_version': 't1'}],
            'tree_jobs': [{'status': 'succeeded'}],
            'tree_matches_current': True,
            'ready_versions': versions,
        }
        ready_foundation = {
            **running_foundation,
            'jobs': [{'kind': 'FOUNDATION', 'status': 'SUCCEEDED', 'count': 8}],
        }
        runtime.state = AsyncMock(side_effect=[running_foundation, ready_foundation])
        with patch('sag_benchmark_runtime.asyncio.sleep', new_callable=AsyncMock):
            result = await runtime.wait_ready()
        self.assertNotIn('E2', result['evidence'])
        self.assertEqual(result['dense_graph']['semantic_dense_edges'], 40)
        self.assertEqual(runtime.state.await_count, 2)

        missing_dense_vectors = {
            **ready_foundation,
            'units': {'total': 20, 'with_dense': 18},
        }
        runtime.state = AsyncMock(return_value=missing_dense_vectors)
        with self.assertRaisesRegex(RuntimeError, 'Full DenseGraph verification failed'):
            await runtime.wait_ready()


if __name__ == '__main__':
    unittest.main()
