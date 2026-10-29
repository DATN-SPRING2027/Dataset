import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.engine import make_url

sys.path.insert(0, str(Path(__file__).parent))
from benchmark_support import (
    BenchmarkRun,
    assert_local_database,
    clean_projects_in_local_db,
    default_benchmark_project_id,
)

URL = 'postgresql+asyncpg://sag:test-password@localhost/sag'


@pytest.mark.asyncio
async def test_completed_result_is_not_relabelled_when_shutdown_fails(tmp_path):
    run = BenchmarkRun('test', tmp_path, URL)
    run.started = True
    run.manifest = {'status': 'COMPLETED'}
    await run.fail(TimeoutError())
    assert run.manifest['status'] == 'COMPLETED'
    await run.close()


@pytest.fixture(autouse=True)
def clean_scope(monkeypatch):
    for key in ('RUN_ID', 'SCHEMA', 'PROJECT_ID', 'SOURCE_ID', 'SOURCE_CONFIG_ID', 'OUTPUT_DIR'):
        monkeypatch.delenv('SAG_BENCHMARK_' + key, raising=False)
    monkeypatch.setenv('SAG_BENCHMARK_USER_ID', '6acc9a5425f02c9d92a01012')
    monkeypatch.setenv('SAG_BENCHMARK_ORGANIZATION_ID', 'ORG-NSC')
    monkeypatch.setattr(sys, 'argv', ['test'])


def test_same_account_distinct_projects_and_collections(tmp_path):
    a = BenchmarkRun('retrievalci_v0', tmp_path, URL)
    b = BenchmarkRun('vn_mteb', tmp_path, URL)
    e2e = BenchmarkRun('eight_file_e2e_smoke', tmp_path, URL)
    e2e_repeat = BenchmarkRun('eight_file_e2e_smoke', tmp_path, URL)
    a_repeat = BenchmarkRun('retrievalci_v0', tmp_path, URL)
    assert a.user_id == b.user_id == e2e.user_id
    assert a.organization_id == b.organization_id == e2e.organization_id
    assert a.schema == b.schema == e2e.schema == 'sag'
    assert len({a.project_id, b.project_id, e2e.project_id}) == 3
    assert a.project_id == a_repeat.project_id == default_benchmark_project_id('retrievalci_v0', 'ORG-NSC')
    assert b.project_id == default_benchmark_project_id('vn_mteb', 'ORG-NSC')
    assert e2e.project_id == e2e_repeat.project_id == default_benchmark_project_id('eight_file_e2e_smoke', 'ORG-NSC')
    assert a.source_id != b.source_id
    assert len({a.collection, b.collection, e2e.collection}) == 3
    assert make_url(a.database_url).password == 'test-password'
    assert make_url(a.database_url).query['search_path'] == 'sag'


@pytest.mark.parametrize('schema', ['sag; DROP SCHEMA sag', 'public."bad"', 'a' * 64])
def test_rejects_invalid_schema(monkeypatch, tmp_path, schema):
    monkeypatch.setenv('SAG_BENCHMARK_SCHEMA', schema)
    with pytest.raises(ValueError, match='valid PostgreSQL'):
        BenchmarkRun('vn_mteb', tmp_path, URL)


def test_rejects_separate_benchmark_schema(monkeypatch, tmp_path):
    monkeypatch.setenv('SAG_BENCHMARK_SCHEMA', 'sag_bench_example')
    with pytest.raises(ValueError, match='application schema sag'):
        BenchmarkRun('vn_mteb', tmp_path, URL)


def test_rejects_non_local_database_for_cleanup():
    assert_local_database('postgresql+asyncpg://sag:pw@localhost:5432/sag')
    assert_local_database('postgresql+asyncpg://sag:pw@127.0.0.1:5432/sag')
    with pytest.raises(ValueError, match='non-local PostgreSQL host'):
        assert_local_database('postgresql+asyncpg://sag:pw@prod-db.example.com:5432/sag')


@pytest.mark.asyncio
async def test_refuses_to_clean_foreign_organization_project():
    pid = 'a' * 24
    connection = AsyncMock()
    scalars_tables = MagicMock()
    scalars_tables.all.return_value = ['documents', 'source_project_mappings']
    scalars_foreign = MagicMock()
    scalars_foreign.all.return_value = [pid]
    connection.scalars.side_effect = [scalars_tables, scalars_foreign]

    with pytest.raises(PermissionError, match='owned by another organization'):
        await clean_projects_in_local_db(
            connection,
            organization_id='ORG-NSC',
            project_ids=[pid],
        )
    connection.execute.assert_not_awaited()


@pytest.mark.asyncio
async def test_clean_qdrant_and_uploads_deletes_only_scoped_collections_and_sources(tmp_path):
    scope = BenchmarkRun('eight_file_e2e_smoke', tmp_path, URL)
    old_pid = 'b' * 24
    old_sid = 'c' * 24
    keep_sid = 'd' * 24
    uploads = tmp_path / 'uploads'
    (uploads / old_sid).mkdir(parents=True)
    (uploads / old_sid / 'doc.md').write_text('stale', encoding='utf-8')
    (uploads / keep_sid).mkdir(parents=True)
    (uploads / keep_sid / 'keep.md').write_text('keep', encoding='utf-8')

    scope.cleaned_projects = [scope.project_id, old_pid]
    scope.cleaned_sources = [old_sid]
    scope.cleaned_collections_pending = [
        f'search_units_{scope.project_id}',
        f'session_units_{scope.project_id}',
        f'search_units_{old_pid}',
    ]

    client = AsyncMock()
    client.delete.side_effect = [
        MagicMock(status_code=200),
        MagicMock(status_code=404),
        MagicMock(status_code=404),
    ]
    client.get.return_value = MagicMock(status_code=404)

    report = await scope.clean_qdrant_and_uploads(client, uploads)
    assert report['qdrant_verified_absent'] is True
    assert len(report['qdrant_deleted_collections']) == 1
    assert not (uploads / old_sid).exists()
    assert (uploads / keep_sid / 'keep.md').is_file()
    await scope.close()


@pytest.mark.asyncio
async def test_never_deletes_existing_collection_in_require_new_collection(tmp_path):
    scope = BenchmarkRun('vn_mteb', tmp_path, URL)
    client = AsyncMock()
    client.get.return_value.status_code = 200
    with pytest.raises(ValueError, match='refusing to overwrite'):
        await scope.require_new_collection(client)
    client.delete.assert_not_called()
    await scope.close()


@pytest.mark.asyncio
async def test_reuse_requires_explicit_scope(monkeypatch, tmp_path):
    scope = BenchmarkRun('vn_mteb', tmp_path, URL)
    monkeypatch.setattr(sys, 'argv', ['run', '--skip-index'])
    with pytest.raises(ValueError, match='requires the schema'):
        await scope.start([], tmp_path / 'unused.jsonl', {})
    await scope.close()


@pytest.mark.asyncio
async def test_start_cleans_only_target_benchmark_project_not_other_db_projects(monkeypatch, tmp_path):
    import benchmark_support

    questions = tmp_path / 'questions.jsonl'
    questions.write_text('{"id": "q1"}\n', encoding='utf-8')
    run = BenchmarkRun('vn_mteb', tmp_path, URL)

    cleaned_calls: list[dict] = []

    async def fake_clean_projects(connection, *, organization_id, project_ids, recorded_source_ids=()):
        cleaned_calls.append(
            {
                'organization_id': organization_id,
                'project_ids': list(project_ids),
                'recorded_source_ids': list(recorded_source_ids),
            }
        )
        return {
            'projects': list(project_ids),
            'exclusive_sources': ['src-vn-old'],
            'exclusive_source_configs': ['cfg-vn-old'],
            'deleted_rows': {'documents': 130},
        }

    monkeypatch.setattr(benchmark_support, 'clean_projects_in_local_db', fake_clean_projects)
    monkeypatch.setattr(benchmark_support.subprocess, 'check_output', lambda *a, **kw: 'deadbeef' if kw.get('text') else b'')

    connection = AsyncMock()
    connection.scalar.return_value = 'sag'

    account_result = MagicMock()
    account_result.mappings.return_value.one_or_none.return_value = {'id': run.user_id, 'name': 'Bench User', 'is_active': True}

    prior_result = MagicMock()
    prior_result.mappings.return_value.all.return_value = [
        {'source_id': 'src-vn-old', 'qdrant_collection': f'search_units_{run.project_id}'},
        # Even if a bogus foreign collection string appeared, it must never be queued for deletion
        {'source_id': 'src-vn-old', 'qdrant_collection': 'search_units_' + 'f' * 24},
    ]

    insert_result = MagicMock()
    connection.execute.side_effect = [account_result, MagicMock(), prior_result, insert_result]

    class _BeginCtx:
        async def __aenter__(self):
            return connection

        async def __aexit__(self, exc_type, exc, tb):
            return False

    fake_registry = MagicMock()
    fake_registry.begin.return_value = _BeginCtx()
    fake_registry.dispose = AsyncMock()
    await run.registry.dispose()
    run.registry = fake_registry

    await run.start([], questions, {'mode': 'test'})
    assert len(cleaned_calls) == 1
    assert cleaned_calls[0]['project_ids'] == [run.project_id]
    assert run.cleaned_projects == [run.project_id]
    assert run.cleaned_collections_pending == [
        f'search_units_{run.project_id}',
        f'session_units_{run.project_id}',
    ]
    await run.close()


@pytest.mark.asyncio
async def test_clean_project_scope_cleans_only_requested_project(monkeypatch, tmp_path):
    import benchmark_support

    target_pid = '43c17f3765f64e3f8f6e4c3f'
    cleaned_calls: list[dict] = []

    async def fake_clean_projects(connection, *, organization_id, project_ids, recorded_source_ids=()):
        cleaned_calls.append(
            {
                'organization_id': organization_id,
                'project_ids': list(project_ids),
                'recorded_source_ids': list(recorded_source_ids),
            }
        )
        return {
            'projects': list(project_ids),
            'exclusive_sources': ['675e9e4853aa4d81807e34878cbf56e4'],
            'exclusive_source_configs': ['tp_3c11715b0c036403735e8f437df6d2b5'],
            'deleted_rows': {'documents': 81},
        }

    connection = AsyncMock()
    connection.scalar.side_effect = ['sag', 'sag.benchmark_runs']
    scalars_result = MagicMock()
    scalars_result.all.return_value = ['675e9e4853aa4d81807e34878cbf56e4']
    connection.scalars.return_value = scalars_result

    class _BeginCtx:
        async def __aenter__(self):
            return connection

        async def __aexit__(self, exc_type, exc, tb):
            return False

    fake_engine = MagicMock()
    fake_engine.begin.return_value = _BeginCtx()
    fake_engine.dispose = AsyncMock()

    monkeypatch.setattr(benchmark_support, 'clean_projects_in_local_db', fake_clean_projects)
    monkeypatch.setattr(benchmark_support, 'create_async_engine', lambda *a, **kw: fake_engine)

    qdrant = AsyncMock()
    qdrant.delete.side_effect = [MagicMock(status_code=200), MagicMock(status_code=404)]
    qdrant.get.return_value = MagicMock(status_code=404)

    uploads = tmp_path / 'uploads'
    (uploads / '675e9e4853aa4d81807e34878cbf56e4').mkdir(parents=True)
    (uploads / 'keep_other_source').mkdir(parents=True)

    report = await benchmark_support.clean_project_scope(
        URL,
        organization_id='ORG-NSC',
        project_id=target_pid,
        qdrant_client=qdrant,
        upload_dir=uploads,
    )
    assert cleaned_calls == [
        {
            'organization_id': 'ORG-NSC',
            'project_ids': [target_pid],
            'recorded_source_ids': ['675e9e4853aa4d81807e34878cbf56e4'],
        }
    ]
    assert report['project_id'] == target_pid
    assert report['qdrant_deleted_collections'] == [f'search_units_{target_pid}']
    assert report['qdrant_verified_absent'] is True
    assert not (uploads / '675e9e4853aa4d81807e34878cbf56e4').exists()
    assert (uploads / 'keep_other_source').exists()
