"""Read completed canonical benchmark results back from SAG's database and verify isolation."""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SAG = ROOT.parent / 'sag-laya-integration/SAG'
os.chdir(SAG)
sys.path.insert(0, str(SAG / 'apps/api'))

import httpx
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sag_api.core.config import settings
from sag_api.core.db import engine
from sag_api.core.principal_assertion import VerifiedPrincipal
from sag_api.db.models import Source
from sag_api.services.search_unit_retrieval_service import _load_current_ready_versions_checked


async def main(run_ids: list[str]) -> None:
    async with engine.connect() as connection:
        schemas = (await connection.scalars(text('''SELECT table_schema FROM information_schema.tables
            WHERE table_name='benchmark_runs' AND (table_schema='sag' OR table_schema LIKE 'sag_bench_%')'''))).all()
        schemas = [schema for schema in schemas if re.fullmatch(r'sag(?:_bench_[a-z0-9_]+)?', schema)]
        records = []
        for run_id in run_ids:
            matches = []
            for schema in schemas:
                matches.extend((await connection.execute(text(f'SELECT * FROM "{schema}".benchmark_runs WHERE id=:id'),
                                                         {'id': run_id})).mappings().all())
            assert len(matches) == 1, f'{run_id}: expected exactly one registry record, found {len(matches)}'
            row = matches[0]
            assert row['status'] == 'COMPLETED', f'{run_id} is not complete'
            records.append(dict(row))
    assert len({r['user_id'] for r in records}) == 1
    assert {r['benchmark_key'] for r in records} == {'retrievalci_v0', 'vn_mteb'}
    assert len({r['project_id'] for r in records}) == len(records)
    assert len({r['source_id'] for r in records}) == len(records)
    assert len({r['qdrant_collection'] for r in records}) == len(records)
    batch = ROOT / 'reports' / ('verified-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    batch.mkdir(parents=True, exist_ok=False)
    checks = []
    lines = ['# Hai benchmark SAG — dữ liệu và kết quả đã lưu trong PostgreSQL', '',
             f"Account chung: `{records[0]['user_id']}`. Bảng kết quả: " + ', '.join(
                 f"`{r['data_schema']}.benchmark_runs`" for r in records) + '.', '',
             '| Benchmark | Project | Tài liệu | Câu SAG chạy mới | Trạng thái |',
             '|---|---|---:|---:|---|']
    now = int(time.time())
    principals = {r['project_id']: VerifiedPrincipal(
        subject=r['user_id'], organization_id=r['organization_id'], allowed_project_ids=frozenset({r['project_id']}),
        issuer='https://continuum.local', key_id='benchmark-verification', token_id=r['id'],
        issued_at=now-1, expires_at=now+600, tenant_id=r['organization_id'], allowed_partition_ids=frozenset({r['project_id']}),
    ) for r in records}
    headers = {'api-key': settings.sag_qdrant_api_key} if settings.sag_qdrant_api_key else {}
    async with httpx.AsyncClient(base_url=settings.sag_qdrant_url.rstrip('/'), headers=headers, timeout=30) as client:
        for row in records:
            manifest = row['manifest_json']
            directory = Path(manifest['output_dir'])
            ci = row['benchmark_key'] == 'retrievalci_v0'
            fixture_root = ROOT / ('RetrievalCI_Bench_v0_2026' if ci else 'VN_MTEB_RAG_Bench_2026')
            question_path = fixture_root / ('examples/rag_eval/bench_v0/questions.jsonl' if ci else 'data/questions.jsonl')
            assert hashlib.sha256(question_path.read_bytes()).hexdigest() == manifest['questions_sha256']
            assert all(hashlib.sha256((fixture_root/p).read_bytes()).hexdigest() == h for p,h in manifest['corpus_sha256'].items())
            output = directory / ('bench_v0_with_sag.json' if ci else 'vn_mteb_sag_results.json')
            report = json.loads(output.read_text(encoding='utf-8'))
            assert report == row['results_json'], 'File and persisted DB results differ'
            fresh = [r for r in report['rows'] if r['system']=='sag_engine'] if ci else report['questions']
            questions = [json.loads(s) for s in question_path.read_text(encoding='utf-8').splitlines() if s.strip()]
            assert len(fresh) == len(questions) == manifest['questions']
            assert {r['question_id'] for r in fresh} == {q['id' if ci else 'question_id'] for q in questions}
            schema = row['data_schema']
            assert re.fullmatch(r'sag(?:_bench_[a-z0-9_]+)?', schema)
            url = make_url(settings.database_url)
            scoped_engine = create_async_engine(url.set(query={k:v for k,v in url.query.items() if k != 'search_path'}),
                connect_args={'server_settings':{'search_path':schema}})
            try:
                async with async_sessionmaker(scoped_engine, expire_on_commit=False)() as session:
                    source = await session.get(Source, row['source_id'])
                    ready = await _load_current_ready_versions_checked(session, [source], principals[row['project_id']])
                    assert len(ready) == manifest['documents'], 'Not all project documents are searchable'
                    for other in records:
                        if other['project_id'] != row['project_id']:
                            blocked = await _load_current_ready_versions_checked(session, [source], principals[other['project_id']])
                            assert not blocked, 'Cross-project canonical scope was readable'
            finally:
                await scoped_engine.dispose()
            response = await client.post(f"/collections/{row['qdrant_collection']}/points/count", json={
                'exact': True, 'filter': {'must_not': [{'key':'project_id','match':{'value':row['project_id']}}]},
            })
            response.raise_for_status()
            assert response.json()['result']['count'] == 0, 'Collection has points belonging to another project'
            checks.append({'run_id':row['id'],'project_id':row['project_id'],'source_id':row['source_id'],
                           'user_id':row['user_id'],'documents_ready':len(ready),'fresh_queries':len(fresh),
                           'file_equals_db':True,'dataset_hashes_verified':True,'cross_project_read_blocked':True,'foreign_project_points':0})
            lines.append(f"| {row['benchmark_key']} | `{row['project_id']}` | {len(ready)} | {len(fresh)} | COMPLETED |")
    for row in records:
        report = row['results_json']
        manifest = row['manifest_json']
        lines += ['', '## ' + row['benchmark_key'], '', f"- Run ID: `{row['id']}`.",
                  f"- File report: `{manifest['output_dir']}`."]
        if row['benchmark_key'] == 'retrievalci_v0':
            metrics = report['by_system_metric']['sag_engine']
            lines += [f"- Recall: {100*metrics['retrieval_source_recall']:.2f}%; precision: {100*metrics['retrieval_source_precision']:.2f}%.",
                      f"- P50 retrieval: {metrics.get('retrieval_latency_ms_p50')} ms.",
                      '- Các row provider khác là tham chiếu lịch sử, không chạy lại và không bảo đảm cùng protocol.']
        elif 'summary' in report:
            summary = report['summary']
            lines += [f"- Recall@5: {100*summary['retrieval']['5']['recall']:.2f}%; nDCG@10: {100*summary['retrieval']['10']['ndcg']:.2f}%.",
                      f"- Answered: {summary['answered']}/{summary['questions']}; execution errors: {summary['execution_errors']}.",
                      f"- P50 retrieval: {summary['retrieval_p50_ms']:.2f} ms; P50 Q&A: {summary['qa_p50_ms']:.2f} ms."]
        else:
            lines += ['- Lượt legacy: xem report JSON theo protocol và audit đã lưu trong manifest.']
        execution = manifest.get('execution')
        if execution:
            lines += [f"- Runtime: `{execution['runtime']}`; transport: `{execution['transport']}`.",
                      f"- Frontend policy: `{json.dumps(execution['frontend'])}`.",
                      f"- E2 enabled: {execution['e2_enabled']}; policy: `{json.dumps(execution['knowledge_queue'])}`."]
        extended = manifest.get('quality_latency') or report.get('quality_latency')
        if extended:
            lines += ['', '### Chất lượng trả lời — judge độc lập', '',
                      f"Judge: `{extended['protocol']['judge_model']}`. Thang 1–5; không phải human accuracy.", '',
                      '| Metric | Mean | Số câu chấm được |', '|---|---:|---:|']
            for metric, value in extended.get('quality_summary', {}).items():
                lines.append(f"| {metric} | {value['mean']} | {value['n_scored']} |")
            lines += ['', '### Latency SAG', '',
                      '| Lượt | Request | Lỗi | Retrieval p50/p95 ms | First validated answer p50/p95 ms | Q&A p50/p95 ms |',
                      '|---|---:|---:|---|---|---|']
            for phase, value in extended['latency'].items():
                distributions = value['successful']
                cells = [f"{distributions[k]['p50_ms']} / {distributions[k]['p95_ms']}" for k in ('retrieval_latency_ms','first_token_ms','latency_ms')]
                lines.append(f"| {phase} | {value['requests']} | {value['errors']} | " + ' | '.join(cells) + ' |')
            lines += ['', 'Bảng latency trên dùng request thành công; JSON giữ cả phân phối tất cả attempts và lỗi. First pass không preload query; physical cold cache chưa xác minh. summary.delta chỉ được gửi sau kiểm chứng citation, nên first_token_ms không phải raw model TTFT.']
            hosted = extended.get('hosted_top5_comparison')
            if hosted:
                lines += ['', '### Top-5 retrieval so với hosted reference', '', hosted['protocol'], '',
                          '| Hệ thống | Recall | Precision | p50 retrieval ms |', '|---|---:|---:|---:|']
                for system, metrics in hosted['by_system_metric'].items():
                    lines.append(f"| {system} | {metrics.get('retrieval_source_recall')} | {metrics.get('retrieval_source_precision')} | {metrics.get('retrieval_latency_ms_p50')} |")
                lines += ['', 'Các hàng hosted là lịch sử, không có answer để chấm; thời gian đo/hạ tầng/cache khác SAG. Không kết luận hệ thống nào nhanh hơn từ bảng này.']
        else:
            lines += ['- Lượt legacy không có judge độc lập; xem protocol gốc.']
    references = json.loads((ROOT/'international_references.json').read_text(encoding='utf-8'))
    lines += ['', '## Tham chiếu VN quốc tế — khác corpus local', '', references['protocol'], '',
              f"Nguồn chính: {references['primary_source']}", '',
              '| Mô hình | HotpotQA-VN reported retrieval score | Latency |', '|---|---:|---|']
    for reference in references['hotpotqa_vn']:
        lines.append(f"| {reference['model']} | {reference['reported_retrieval_score']} | Không có số đối chiếu |")
    lines += ['', 'Các model legal được nhắc trong README nhưng chưa đủ artifact để đối chiếu tái lập: ' + ', '.join(r['model'] for r in references['legal_readme_references_unverified']) + '.',
              'Không xếp hạng chung điểm SAG local với điểm full dataset công bố; không chạy mock để thay provider thiếu quyền truy cập.']
    lines += ['', '## Kiểm tra lưu trữ và tách scope', '',
              '- Kết quả file khớp nguyên bản JSONB trong DB; đủ 100 câu SAG chạy mới, không lẫn baseline lịch sử.',
              '- Corpus và câu hỏi khớp SHA-256 trong manifest.',
              '- Hai project/source/collection khác nhau, cùng account đang tồn tại.',
              '- Kiểm tra canonical scope chéo project trả về rỗng; mỗi collection không có point thuộc project khác.',
              '- Đây là scope project SAG; chưa tạo entity Project/membership trong IAM Continuum.', '']
    (batch/'BENCHMARKS.md').write_text('\n'.join(lines), encoding='utf-8')
    (batch/'isolation_checks.json').write_text(json.dumps(checks, ensure_ascii=False, indent=2), encoding='utf-8')
    async with engine.begin() as connection:
        for check in checks:
            await connection.execute(text("UPDATE benchmark_runs SET manifest_json=manifest_json || jsonb_build_object('verification',CAST(:check AS jsonb)) WHERE id=:id"),
                                     {'id':check['run_id'],'check':json.dumps(check,ensure_ascii=False)})
    for row, check in zip(records, checks, strict=True):
        row['manifest_json']['verification'] = check
        (Path(row['manifest_json']['output_dir'])/'run_manifest.json').write_text(json.dumps(row['manifest_json'],ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'report':str(batch/'BENCHMARKS.md'),'checks':checks},ensure_ascii=False,indent=2))
    await engine.dispose()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_ids', nargs=2)
    args = parser.parse_args()
    asyncio.run(main(args.run_ids))
