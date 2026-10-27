import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.engine import make_url

sys.path.insert(0, str(Path(__file__).parent))
from benchmark_support import BenchmarkRun

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
    assert a.user_id == b.user_id
    assert a.organization_id == b.organization_id
    assert a.schema == b.schema == 'sag'
    assert a.project_id != b.project_id
    assert a.source_id != b.source_id
    assert a.collection != b.collection
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


@pytest.mark.asyncio
async def test_refuses_to_reset_existing_project(monkeypatch, tmp_path):
    scope = BenchmarkRun('vn_mteb', tmp_path, URL)
    await scope.registry.dispose()
    connection = AsyncMock()
    connection.scalar.side_effect = ['sag', True]
    result = MagicMock()
    result.mappings.return_value.one_or_none.return_value = {'id': scope.user_id, 'name': 'Benchmark owner', 'is_active': True}
    connection.execute.return_value = result
    context = MagicMock()
    context.__aenter__ = AsyncMock(return_value=connection)
    context.__aexit__ = AsyncMock(return_value=False)
    scope.registry = MagicMock()
    scope.registry.begin.return_value = context
    with pytest.raises(ValueError, match='already has data'):
        await scope.start([], tmp_path / 'unused.jsonl', {})
    assert connection.execute.await_count == 1  # Only the account read ran; no DDL or writes.


@pytest.mark.asyncio
async def test_never_deletes_existing_collection(tmp_path):
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
