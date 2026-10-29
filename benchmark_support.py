"""Persistent, project-scoped bookkeeping and fail-closed DB/Qdrant cleanup for SAG benchmarks."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import uuid
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

_LOCAL_DB_HOSTS = frozenset({'localhost', '127.0.0.1', '::1'})
_PROJECT_ID_RE = re.compile(r'^[a-fA-F0-9]{24}$')
_SAFE_COLLECTION_RE = re.compile(r'^(?:search_units|session_units)_[a-fA-F0-9]{24}$')
_SAFE_SOURCE_DIR_RE = re.compile(r'^[A-Za-z0-9_-]{8,64}$')


def assert_local_database(database_url: str) -> None:
    parsed = make_url(database_url)
    if parsed.drivername != 'postgresql+asyncpg':
        raise ValueError('Persistent SAG benchmarks require PostgreSQL')
    host = (parsed.host or '').strip().lower()
    if host not in _LOCAL_DB_HOSTS:
        raise ValueError(f'Benchmark cleanup refuses non-local PostgreSQL host: {host or "<empty>"}')


def _knowledge_stable_id(*parts: str) -> str:
    digest = hashlib.sha256(
        json.dumps(parts, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()
    ).hexdigest()
    return str(uuid.uuid5(uuid.NAMESPACE_URL, 'sag:knowledge:' + digest))


async def clean_projects_in_local_db(
    connection,
    *,
    organization_id: str,
    project_ids: Sequence[str],
    recorded_source_ids: Sequence[str] = (),
) -> dict:
    projects = sorted({pid for pid in project_ids if pid})
    if not projects:
        return {'projects': [], 'exclusive_sources': [], 'deleted_rows': {}}
    for pid in projects:
        if not _PROJECT_ID_RE.fullmatch(pid):
            raise ValueError(f'Invalid benchmark project ID for cleanup: {pid}')

    existing_tables = set(
        (
            await connection.scalars(
                text('SELECT table_name FROM information_schema.tables WHERE table_schema = current_schema()')
            )
        ).all()
    )

    foreign_checks = []
    if 'documents' in existing_tables:
        foreign_checks.append('SELECT project_id, tenant_id AS org_id FROM documents WHERE project_id = ANY(:projects)')
    if 'source_project_mappings' in existing_tables:
        foreign_checks.append(
            'SELECT project_id, organization_id AS org_id FROM source_project_mappings WHERE project_id = ANY(:projects)'
        )
    if foreign_checks:
        foreign_projects = (
            await connection.scalars(
                text(f"SELECT DISTINCT project_id FROM ({' UNION ALL '.join(foreign_checks)}) scoped WHERE org_id <> :org"),
                {'projects': projects, 'org': organization_id},
            )
        ).all()
        if foreign_projects:
            raise PermissionError(
                f"Refusing to clean project owned by another organization: {', '.join(sorted(foreign_projects))}"
            )

    candidate_sources: set[str] = {sid for sid in recorded_source_ids if sid}
    if 'documents' in existing_tables:
        rows = (
            await connection.scalars(
                text(
                    'SELECT DISTINCT source_id FROM documents '
                    'WHERE project_id = ANY(:projects) AND tenant_id = :org AND source_id IS NOT NULL'
                ),
                {'projects': projects, 'org': organization_id},
            )
        ).all()
        candidate_sources.update(rows)
    if 'source_project_mappings' in existing_tables:
        rows = (
            await connection.scalars(
                text(
                    'SELECT DISTINCT source_id FROM source_project_mappings '
                    'WHERE project_id = ANY(:projects) AND organization_id = :org AND source_id IS NOT NULL'
                ),
                {'projects': projects, 'org': organization_id},
            )
        ).all()
        candidate_sources.update(rows)
    if 'sources' in existing_tables:
        rows = (
            await connection.scalars(
                text(
                    "SELECT DISTINCT id FROM sources "
                    "WHERE COALESCE(config_json::jsonb->>'project_id', '') = ANY(:projects) "
                    "  AND COALESCE(config_json::jsonb->>'tenant_id', '') = :org"
                ),
                {'projects': projects, 'org': organization_id},
            )
        ).all()
        candidate_sources.update(rows)

    exclusive_sources: list[str] = []
    exclusive_configs: list[str] = []
    if candidate_sources and 'sources' in existing_tables:
        source_rows = (
            await connection.execute(
                text(
                    '''
                    SELECT s.id, s.sag_source_config_id
                    FROM sources s
                    WHERE s.id = ANY(:sources)
                      AND NOT EXISTS (
                          SELECT 1 FROM documents d
                          WHERE d.source_id = s.id
                            AND NOT (d.project_id = ANY(:projects) AND d.tenant_id = :org)
                      )
                      AND NOT EXISTS (
                          SELECT 1 FROM source_project_mappings m
                          WHERE m.source_id = s.id
                            AND NOT (m.project_id = ANY(:projects) AND m.organization_id = :org)
                      )
                    '''
                ),
                {'sources': sorted(candidate_sources), 'projects': projects, 'org': organization_id},
            )
        ).mappings().all()
        exclusive_sources = sorted({row['id'] for row in source_rows if row['id']})
        exclusive_configs = sorted(
            {row['sag_source_config_id'] for row in source_rows if row['sag_source_config_id']}
        )

    deleted_rows: dict[str, int] = {}
    params = {
        'projects': projects,
        'org': organization_id,
        'exclusive_sources': exclusive_sources,
        'exclusive_configs': exclusive_configs,
    }

    async def run_delete(table: str, sql: str, extra_params: dict | None = None) -> None:
        if table not in existing_tables:
            return
        result = await connection.execute(text(sql), {**params, **(extra_params or {})})
        count = int(result.rowcount or 0)
        if count:
            deleted_rows[table] = deleted_rows.get(table, 0) + count

    # 1. SearchUnits & SearchUnit graph edges (must precede canonical_blocks due to NO ACTION FKs).
    await run_delete('knowledge_graph_edges', 'DELETE FROM knowledge_graph_edges WHERE project_id = ANY(:projects)')
    if 'documents' in existing_tables and 'document_versions' in existing_tables:
        await run_delete(
            'search_units',
            '''
            DELETE FROM search_units
            WHERE document_version_id IN (
                SELECT v.id FROM document_versions v
                JOIN documents d ON d.id = v.document_id
                WHERE d.project_id = ANY(:projects) AND d.tenant_id = :org
            )
            ''',
        )

    # 2. Knowledge E0/E1/E2 evidence, jobs, DenseGraph builds/edges, and units.
    if 'knowledge_units' in existing_tables:
        await run_delete(
            'knowledge_evidence',
            '''
            DELETE FROM knowledge_evidence
            WHERE unit_id IN (
                SELECT id FROM knowledge_units WHERE project_id = ANY(:projects) AND tenant_id = :org
            )
            ''',
        )
    if 'documents' in existing_tables and 'document_versions' in existing_tables:
        await run_delete(
            'knowledge_jobs',
            '''
            DELETE FROM knowledge_jobs
            WHERE tenant_id = :org
              AND (
                  document_version_id IN (
                      SELECT v.id FROM document_versions v
                      JOIN documents d ON d.id = v.document_id
                      WHERE d.project_id = ANY(:projects) AND d.tenant_id = :org
                  )
                  OR unit_id IN (
                      SELECT id FROM knowledge_units WHERE project_id = ANY(:projects) AND tenant_id = :org
                  )
              )
            ''',
        )
    if 'knowledge_graph_builds' in existing_tables:
        await run_delete(
            'knowledge_unit_edges',
            '''
            DELETE FROM knowledge_unit_edges
            WHERE build_id IN (
                SELECT id FROM knowledge_graph_builds WHERE project_id = ANY(:projects) AND tenant_id = :org
            )
            ''',
        )
    await run_delete(
        'knowledge_graph_builds',
        'DELETE FROM knowledge_graph_builds WHERE project_id = ANY(:projects) AND tenant_id = :org',
    )
    await run_delete(
        'knowledge_units',
        'DELETE FROM knowledge_units WHERE project_id = ANY(:projects) AND tenant_id = :org',
    )

    # 3. Leiden routing trees, profiles, leases, quality assessments, and research tasks.
    if 'tree_manifests' in existing_tables:
        await run_delete(
            'tree_routing_profiles',
            '''
            DELETE FROM tree_routing_profiles
            WHERE project_id = ANY(:projects)
               OR tree_version IN (SELECT tree_version FROM tree_manifests WHERE project_id = ANY(:projects))
            ''',
        )
        await run_delete(
            'tree_snapshot_leases',
            '''
            DELETE FROM tree_snapshot_leases
            WHERE project_id = ANY(:projects)
               OR tree_version IN (SELECT tree_version FROM tree_manifests WHERE project_id = ANY(:projects))
            ''',
        )
        await run_delete(
            'knowledge_tree_nodes',
            '''
            DELETE FROM knowledge_tree_nodes
            WHERE tree_version IN (SELECT tree_version FROM tree_manifests WHERE project_id = ANY(:projects))
            ''',
        )
    if 'ingestion_runs' in existing_tables and 'research_tasks' in existing_tables:
        await connection.execute(
            text(
                'UPDATE ingestion_runs SET research_task_id = NULL '
                'WHERE project_id = ANY(:projects) AND tenant_id = :org AND research_task_id IS NOT NULL'
            ),
            params,
        )
    await run_delete('research_tasks', 'DELETE FROM research_tasks WHERE project_id = ANY(:projects) AND tenant_id = :org')
    if 'knowledge_quality_assessments' in existing_tables and 'knowledge_gaps' in existing_tables:
        await run_delete(
            'knowledge_gap_questions',
            '''
            DELETE FROM knowledge_gap_questions
            WHERE gap_id IN (
                SELECT g.id FROM knowledge_gaps g
                JOIN knowledge_quality_assessments a ON a.id = g.assessment_id
                WHERE a.project_id = ANY(:projects) AND a.tenant_id = :org
            )
            ''',
        )
        await run_delete(
            'knowledge_gaps',
            '''
            DELETE FROM knowledge_gaps
            WHERE assessment_id IN (
                SELECT id FROM knowledge_quality_assessments WHERE project_id = ANY(:projects) AND tenant_id = :org
            )
            ''',
        )
    await run_delete(
        'knowledge_quality_assessments',
        'DELETE FROM knowledge_quality_assessments WHERE project_id = ANY(:projects) AND tenant_id = :org',
    )
    await run_delete(
        'knowledge_query_demand_daily',
        'DELETE FROM knowledge_query_demand_daily WHERE project_id = ANY(:projects) AND tenant_id = :org',
    )
    await run_delete('project_search_state', 'DELETE FROM project_search_state WHERE project_id = ANY(:projects)')
    await run_delete('tree_manifests', 'DELETE FROM tree_manifests WHERE project_id = ANY(:projects)')

    # 4. Session context tables scoped to project.
    await run_delete('session_graph_edges', 'DELETE FROM session_graph_edges WHERE project_id = ANY(:projects) AND tenant_id = :org')
    await run_delete('session_decision_ledger', 'DELETE FROM session_decision_ledger WHERE project_id = ANY(:projects) AND tenant_id = :org')
    await run_delete('session_unit_messages', 'DELETE FROM session_unit_messages WHERE project_id = ANY(:projects) AND tenant_id = :org')
    await run_delete('session_units', 'DELETE FROM session_units WHERE project_id = ANY(:projects) AND tenant_id = :org')

    # 5. Ingestion runs, idempotency keys, background jobs, canonical blocks, document versions, documents, mappings.
    await run_delete(
        'upload_idempotency_keys',
        'DELETE FROM upload_idempotency_keys WHERE project_id = ANY(:projects) AND tenant_id = :org',
    )
    if 'ingestion_runs' in existing_tables:
        await run_delete(
            'stage_runs',
            '''
            DELETE FROM stage_runs
            WHERE run_id IN (
                SELECT id FROM ingestion_runs WHERE project_id = ANY(:projects) AND tenant_id = :org
            )
            ''',
        )
    await run_delete('ingestion_runs', 'DELETE FROM ingestion_runs WHERE project_id = ANY(:projects) AND tenant_id = :org')
    if 'documents' in existing_tables:
        await run_delete(
            'jobs',
            '''
            DELETE FROM jobs
            WHERE document_id IN (
                SELECT id FROM documents WHERE project_id = ANY(:projects) AND tenant_id = :org
            )
               OR (cardinality(CAST(:exclusive_sources AS varchar[])) > 0 AND source_id = ANY(:exclusive_sources))
               OR (
                   type = 'REBUILD_UNIVERSE_TREE'
                   AND COALESCE(payload_json::jsonb->>'tenant_id', '') = :org
                   AND jsonb_array_length(COALESCE(payload_json::jsonb->'project_ids', '[]'::jsonb)) > 0
                   AND NOT EXISTS (
                       SELECT 1
                       FROM jsonb_array_elements_text(COALESCE(payload_json::jsonb->'project_ids', '[]'::jsonb)) AS pid
                       WHERE NOT (pid = ANY(:projects))
                   )
               )
            ''',
        )
    if 'documents' in existing_tables and 'document_versions' in existing_tables:
        await run_delete(
            'canonical_blocks',
            '''
            DELETE FROM canonical_blocks
            WHERE document_version_id IN (
                SELECT v.id FROM document_versions v
                JOIN documents d ON d.id = v.document_id
                WHERE d.project_id = ANY(:projects) AND d.tenant_id = :org
            )
            ''',
        )
        await run_delete(
            'source_snapshots',
            '''
            DELETE FROM source_snapshots
            WHERE document_version_id IN (
                SELECT v.id FROM document_versions v
                JOIN documents d ON d.id = v.document_id
                WHERE d.project_id = ANY(:projects) AND d.tenant_id = :org
            )
            ''',
        )
        if 'knowledge_queue_control' in existing_tables:
            await run_delete(
                'knowledge_queue_control',
                '''
                DELETE FROM knowledge_queue_control
                WHERE id IN (
                    SELECT 'version:' || v.id
                    FROM document_versions v
                    JOIN documents d ON d.id = v.document_id
                    WHERE d.project_id = ANY(:projects) AND d.tenant_id = :org
                )
                ''',
            )
        await run_delete(
            'document_versions',
            '''
            DELETE FROM document_versions
            WHERE document_id IN (
                SELECT id FROM documents WHERE project_id = ANY(:projects) AND tenant_id = :org
            )
            ''',
        )
    await run_delete('documents', 'DELETE FROM documents WHERE project_id = ANY(:projects) AND tenant_id = :org')
    await run_delete(
        'source_project_mappings',
        'DELETE FROM source_project_mappings WHERE project_id = ANY(:projects) AND organization_id = :org',
    )

    # 6. Exclusive legacy data_source / sources rows (only when not referenced by any other project).
    if exclusive_configs:
        if 'source_event' in existing_tables or 'entity' in existing_tables:
            await run_delete(
                'event_entity',
                '''
                DELETE FROM event_entity
                WHERE event_id IN (SELECT id FROM source_event WHERE data_source_id = ANY(:exclusive_configs))
                   OR entity_id IN (SELECT id FROM entity WHERE data_source_id = ANY(:exclusive_configs))
                ''',
            )
        await run_delete('source_event', 'DELETE FROM source_event WHERE data_source_id = ANY(:exclusive_configs)')
        await run_delete('entity', 'DELETE FROM entity WHERE data_source_id = ANY(:exclusive_configs)')
        await run_delete('entity_type', 'DELETE FROM entity_type WHERE data_source_id = ANY(:exclusive_configs)')
        await run_delete('source_chunk', 'DELETE FROM source_chunk WHERE data_source_id = ANY(:exclusive_configs)')
        await run_delete('article', 'DELETE FROM article WHERE data_source_id = ANY(:exclusive_configs)')
        await run_delete('chat_conversation', 'DELETE FROM chat_conversation WHERE data_source_id = ANY(:exclusive_configs)')
        await run_delete('kb_document', 'DELETE FROM kb_document WHERE data_source_id = ANY(:exclusive_configs)')
        await run_delete('sag_operation', 'DELETE FROM sag_operation WHERE data_source_id = ANY(:exclusive_configs)')
        await run_delete('sag_source_manifest', 'DELETE FROM sag_source_manifest WHERE data_source_id = ANY(:exclusive_configs)')
        await run_delete(
            'sag_data_source_manifest',
            'DELETE FROM sag_data_source_manifest WHERE data_source_id = ANY(:exclusive_configs)',
        )
        await run_delete('data_source', 'DELETE FROM data_source WHERE id = ANY(:exclusive_configs)')

    if exclusive_sources:
        await run_delete(
            'agent_bindings',
            "DELETE FROM agent_bindings WHERE target_type = 'SOURCE' AND target_id = ANY(:exclusive_sources)",
        )
        await run_delete(
            'universe_dirty_sources',
            'DELETE FROM universe_dirty_sources WHERE source_id = ANY(:exclusive_sources)',
        )
        await run_delete(
            'universe_partitions',
            'DELETE FROM universe_partitions WHERE source_id = ANY(:exclusive_sources)',
        )
        await run_delete('sources', 'DELETE FROM sources WHERE id = ANY(:exclusive_sources)')

    # 7. Per-project queue control rows (`project:...` and `project-input:...`) so re-runs start completely clean.
    if 'knowledge_queue_control' in existing_tables:
        for pid in projects:
            prefix = f'project:{_knowledge_stable_id(organization_id, pid)}:%'
            project_input_id = f'project-input:{organization_id}:{pid}'
            await run_delete(
                'knowledge_queue_control',
                'DELETE FROM knowledge_queue_control WHERE id LIKE :prefix OR id = :project_input_id',
                {'prefix': prefix, 'project_input_id': project_input_id},
            )

    # 8. Post-cleanup verification assertion (fail-closed).
    verification_queries = (
        ('documents', 'SELECT count(*) FROM documents WHERE project_id = ANY(:projects)'),
        ('knowledge_units', 'SELECT count(*) FROM knowledge_units WHERE project_id = ANY(:projects)'),
        ('tree_manifests', 'SELECT count(*) FROM tree_manifests WHERE project_id = ANY(:projects)'),
        ('project_search_state', 'SELECT count(*) FROM project_search_state WHERE project_id = ANY(:projects)'),
        ('source_project_mappings', 'SELECT count(*) FROM source_project_mappings WHERE project_id = ANY(:projects)'),
    )
    for table, sql in verification_queries:
        if table in existing_tables:
            remaining = int((await connection.scalar(text(sql), {'projects': projects})) or 0)
            if remaining != 0:
                raise RuntimeError(f'Local DB cleanup incomplete for {table}: {remaining} rows remain')

    return {
        'projects': projects,
        'exclusive_sources': exclusive_sources,
        'exclusive_source_configs': exclusive_configs,
        'deleted_rows': deleted_rows,
    }


def default_benchmark_project_id(benchmark_key: str, organization_id: str = '') -> str:
    """Deterministic 24-hex project ID dedicated to a single benchmark within an organization."""
    scope = f"sag-benchmark-project:{organization_id.strip() or 'default'}:{benchmark_key.strip()}"
    return hashlib.sha256(scope.encode('utf-8')).hexdigest()[:24]


class BenchmarkRun:
    def __init__(self, key: str, root: Path, database_url: str) -> None:
        self.key, self.root = key, root
        self.id = os.getenv('SAG_BENCHMARK_RUN_ID') or f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{uuid.uuid4().hex[:6]}"
        self.schema = os.getenv('SAG_BENCHMARK_SCHEMA', 'sag')
        if not re.fullmatch(r'[a-z_][a-z0-9_]{0,62}', self.schema):
            raise ValueError('Benchmark schema must be a valid PostgreSQL schema identifier')
        if self.schema != 'sag':
            raise ValueError('SAG benchmarks must use the application schema sag')
        self.user_id = os.getenv('SAG_BENCHMARK_USER_ID', '')
        self.organization_id = os.getenv('SAG_BENCHMARK_ORGANIZATION_ID', '')
        self.project_id = os.getenv('SAG_BENCHMARK_PROJECT_ID') or default_benchmark_project_id(key, self.organization_id)
        if not _PROJECT_ID_RE.fullmatch(self.project_id):
            raise ValueError('Benchmark project ID must be a 24-character identifier')
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
        self.cleaned_projects: list[str] = []
        self.cleaned_sources: list[str] = []
        self.cleaned_collections_pending: list[str] = []

    async def start(
        self,
        corpus: list[Path],
        questions: Path,
        models: dict,
        *,
        preserve_project_ids: Sequence[str] = (),
    ) -> None:
        if not self.user_id or not self.organization_id:
            raise ValueError('Set SAG_BENCHMARK_USER_ID and SAG_BENCHMARK_ORGANIZATION_ID to the existing account/scope')
        skip_index = '--skip-index' in sys.argv
        if skip_index and not all(os.getenv('SAG_BENCHMARK_' + name) for name in ('SCHEMA', 'PROJECT_ID', 'SOURCE_ID', 'SOURCE_CONFIG_ID')):
            raise ValueError('--skip-index requires the schema, project ID, source ID and source config ID from a previous run manifest')
        if not skip_index:
            assert_local_database(self.database_url)
        self.output_dir.mkdir(parents=True, exist_ok=False)
        db_cleanup_report: dict | None = None
        async with self.registry.begin() as connection:
            if await connection.scalar(text('SELECT current_schema()')) != self.schema:
                raise ValueError('Benchmark data must use the configured application schema; select the same schema explicitly')
            account = (await connection.execute(text('SELECT id,name,is_active FROM users WHERE id=:id'), {'id': self.user_id})).mappings().one_or_none()
            if not account or not account['is_active']:
                raise ValueError('Benchmark owner must be an existing active SAG account')
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
            if skip_index:
                mapping = await connection.scalar(
                    text(
                        'SELECT COALESCE('
                        '(SELECT tenant_id FROM documents WHERE project_id=:project AND source_id=:source LIMIT 1), '
                        '(SELECT organization_id FROM source_project_mappings WHERE project_id=:project AND source_id=:source LIMIT 1))'
                    ),
                    {'project': self.project_id, 'source': self.source_id},
                )
                if mapping != self.organization_id:
                    raise ValueError('Reused source does not belong to the benchmark organization/project')
            else:
                preserved = set(preserve_project_ids)
                projects_to_clean = [] if self.project_id in preserved else [self.project_id]
                prior_rows = (
                    (
                        await connection.execute(
                            text(
                                '''
                                SELECT DISTINCT source_id, qdrant_collection
                                FROM benchmark_runs
                                WHERE organization_id = :org
                                  AND data_schema = :schema
                                  AND project_id = :project
                                '''
                            ),
                            {
                                'org': self.organization_id,
                                'schema': self.schema,
                                'project': self.project_id,
                            },
                        )
                    ).mappings().all()
                    if projects_to_clean
                    else []
                )
                recorded_sources = [row['source_id'] for row in prior_rows if row['source_id']]
                allowed_project_collections = {
                    f'search_units_{self.project_id}',
                    f'session_units_{self.project_id}',
                }
                recorded_collections = [
                    row['qdrant_collection']
                    for row in prior_rows
                    if row['qdrant_collection']
                    and row['qdrant_collection'] in allowed_project_collections
                    and _SAFE_COLLECTION_RE.fullmatch(row['qdrant_collection'])
                ]
                db_cleanup_report = await clean_projects_in_local_db(
                    connection,
                    organization_id=self.organization_id,
                    project_ids=projects_to_clean,
                    recorded_source_ids=recorded_sources,
                )
                self.cleaned_projects = db_cleanup_report['projects']
                self.cleaned_sources = db_cleanup_report['exclusive_sources']
                self.cleaned_collections_pending = (
                    sorted(allowed_project_collections | set(recorded_collections))
                    if self.cleaned_projects
                    else []
                )

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
                'cleanup': (
                    {'skipped': True, 'reason': '--skip-index'}
                    if skip_index
                    else {
                        'local_db': db_cleanup_report,
                        'qdrant_deleted_collections': [],
                        'qdrant_verified_absent': False,
                        'upload_dirs_removed': [],
                    }
                ),
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
        print(
            f'RUN_ID={self.id} OWNER={self.user_id} PROJECT={self.project_id} SCHEMA={self.schema} '
            f'CLEANED_PROJECTS={len(self.cleaned_projects)}',
            flush=True,
        )

    async def clean_qdrant_and_uploads(self, qdrant_client, upload_dir: str | Path | None = None) -> dict:
        collections = sorted(
            {
                col
                for col in (self.cleaned_collections_pending or [self.collection, f'session_units_{self.project_id}'])
                if _SAFE_COLLECTION_RE.fullmatch(col)
            }
        )
        deleted_collections: list[str] = []
        for col in collections:
            response = await qdrant_client.delete(f'/collections/{col}')
            if response.status_code == 200:
                deleted_collections.append(col)
            elif response.status_code != 404:
                raise RuntimeError(f'Failed to clean Qdrant collection {col}: HTTP {response.status_code}')
        await self.require_new_collection(qdrant_client)

        removed_dirs: list[str] = []
        if upload_dir:
            base = Path(upload_dir).resolve()
            if base.is_dir():
                for sid in sorted(set(self.cleaned_sources)):
                    if not _SAFE_SOURCE_DIR_RE.fullmatch(sid):
                        continue
                    candidate = (base / sid).resolve()
                    if candidate.parent == base and candidate.is_dir():
                        shutil.rmtree(candidate, ignore_errors=True)
                        removed_dirs.append(str(candidate))

        cleanup = self.manifest.setdefault('cleanup', {})
        cleanup['qdrant_checked_collections'] = collections
        cleanup['qdrant_deleted_collections'] = deleted_collections
        cleanup['qdrant_verified_absent'] = True
        cleanup['upload_dirs_removed'] = removed_dirs
        if self.started and self.output_dir.is_dir():
            self._write_manifest()
        return cleanup

    async def purge_current_project(self, qdrant_client=None, upload_dir: str | Path | None = None) -> dict:
        assert_local_database(self.database_url)
        async with self.registry.begin() as connection:
            db_report = await clean_projects_in_local_db(
                connection,
                organization_id=self.organization_id,
                project_ids=[self.project_id],
                recorded_source_ids=[self.source_id] if self.source_id else (),
            )
        self.cleaned_projects = db_report['projects']
        self.cleaned_sources = db_report['exclusive_sources']
        self.cleaned_collections_pending = [self.collection, f'session_units_{self.project_id}']
        qdrant_report = None
        if qdrant_client is not None:
            qdrant_report = await self.clean_qdrant_and_uploads(qdrant_client, upload_dir)
        return {'local_db': db_report, 'qdrant': qdrant_report}

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


async def clean_project_scope(
    database_url: str,
    *,
    organization_id: str,
    project_id: str,
    schema: str = 'sag',
    qdrant_client=None,
    upload_dir: str | Path | None = None,
) -> dict:
    """Clean one specific project in local PostgreSQL (+ Qdrant + exclusive uploads) without touching any other project."""
    assert_local_database(database_url)
    org = organization_id.strip()
    pid = project_id.strip()
    if not org:
        raise ValueError('organization_id is required for project-scoped cleanup')
    if not _PROJECT_ID_RE.fullmatch(pid):
        raise ValueError(f'Invalid 24-hex project_id: {pid}')
    if schema != 'sag':
        raise ValueError('SAG project cleanup must target schema sag')

    parsed = make_url(database_url)
    query = dict(parsed.query)
    query.pop('search_path', None)
    engine = create_async_engine(
        parsed.set(query=query),
        connect_args={'server_settings': {'search_path': schema}},
        pool_pre_ping=True,
    )
    try:
        async with engine.begin() as connection:
            if await connection.scalar(text('SELECT current_schema()')) != schema:
                raise ValueError('Benchmark schema search_path was not applied')
            recorded_sources: list[str] = []
            has_runs = await connection.scalar(text("SELECT to_regclass('benchmark_runs')"))
            if has_runs:
                rows = (
                    await connection.scalars(
                        text(
                            '''
                            SELECT DISTINCT source_id
                            FROM benchmark_runs
                            WHERE organization_id = :org
                              AND data_schema = :schema
                              AND project_id = :project
                              AND source_id IS NOT NULL
                            '''
                        ),
                        {'org': org, 'schema': schema, 'project': pid},
                    )
                ).all()
                recorded_sources = [sid for sid in rows if sid]
            db_report = await clean_projects_in_local_db(
                connection,
                organization_id=org,
                project_ids=[pid],
                recorded_source_ids=recorded_sources,
            )
    finally:
        await engine.dispose()

    collections = [f'search_units_{pid}', f'session_units_{pid}']
    deleted_collections: list[str] = []
    qdrant_verified_absent = False
    if qdrant_client is not None:
        for col in collections:
            if not _SAFE_COLLECTION_RE.fullmatch(col):
                raise ValueError(f'Unsafe Qdrant collection name: {col}')
            response = await qdrant_client.delete(f'/collections/{col}')
            if response.status_code == 200:
                deleted_collections.append(col)
            elif response.status_code != 404:
                raise RuntimeError(f'Failed to clean Qdrant collection {col}: HTTP {response.status_code}')
            check = await qdrant_client.get(f'/collections/{col}')
            if check.status_code != 404:
                raise RuntimeError(f'Qdrant collection {col} still exists after cleanup (HTTP {check.status_code})')
        qdrant_verified_absent = True

    removed_dirs: list[str] = []
    if upload_dir:
        base = Path(upload_dir).resolve()
        if base.is_dir():
            for sid in sorted(set(db_report['exclusive_sources'])):
                if not _SAFE_SOURCE_DIR_RE.fullmatch(sid):
                    continue
                candidate = (base / sid).resolve()
                if candidate.parent == base and candidate.is_dir():
                    shutil.rmtree(candidate, ignore_errors=True)
                    removed_dirs.append(str(candidate))

    return {
        'organization_id': org,
        'project_id': pid,
        'local_db': db_report,
        'qdrant_checked_collections': collections if qdrant_client is not None else [],
        'qdrant_deleted_collections': deleted_collections,
        'qdrant_verified_absent': qdrant_verified_absent,
        'upload_dirs_removed': removed_dirs,
    }


if __name__ == '__main__':
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(description='Project-scoped SAG benchmark cleanup utility.')
    parser.add_argument('--clean-project', required=True, help='24-hex project_id to clean in isolation.')
    parser.add_argument('--organization-id', default=os.getenv('SAG_BENCHMARK_ORGANIZATION_ID', ''))
    args = parser.parse_args()

    sag_root = Path(__file__).resolve().parents[1] / 'sag-laya-integration' / 'SAG'
    sys.path.insert(0, str(sag_root / 'apps' / 'api'))
    os.chdir(sag_root)
    from sag_api.core.config import settings as _sag_settings
    from sag_api.sag import EngineManager as _EngineManager

    async def _cli_main() -> None:
        org = args.organization_id or os.getenv('SAG_BENCHMARK_ORGANIZATION_ID', '')
        em = _EngineManager(_sag_settings)
        qdrant = await em.get_search_unit_qdrant_client()
        report = await clean_project_scope(
            _sag_settings.database_url,
            organization_id=org,
            project_id=args.clean_project,
            qdrant_client=qdrant,
            upload_dir=_sag_settings.upload_dir,
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))

    asyncio.run(_cli_main())
