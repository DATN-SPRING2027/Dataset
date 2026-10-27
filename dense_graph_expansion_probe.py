"""Paired graph-expansion ablation; the published routing tree remains unchanged."""
import asyncio
import copy
import dataclasses
import json
import statistics
import time
from collections import defaultdict

import probe_retrieval_breadth as probe


def adjacency(edges, ids, partitions):
    pairs = {}
    for edge in edges:
        a, b, weight = str(edge['source']), str(edge['target']), float(edge['weight'])
        if edge['partition'] not in partitions or a not in ids or b not in ids or a == b or weight < .55:
            continue
        pair = tuple(sorted((a, b)))
        pairs[pair] = max(weight, pairs.get(pair, 0.0))
    result = defaultdict(list)
    for (a, b), weight in pairs.items():
        result[a].append((b, weight))
        result[b].append((a, weight))
    return {key: sorted(values, key=lambda x: (-x[1], x[0])) for key, values in result.items()}


async def evaluate(run, runtime, files, questions):
    from sqlalchemy import select
    from sag_api.core.db import SessionLocal
    from sag_api.db.models import KnowledgeUnit, KnowledgeGraphBuild, ProjectSearchState, TreeManifest
    from sag_api.services.knowledge_service import graph_payload, KnowledgeConfig
    from sag_api.services import search_unit_retrieval_service as retrieval
    from retrievalci.rag_eval.metrics import compute_row
    from retrievalci.rag_eval.types import Citation, SystemAnswer

    rows = []
    original = retrieval._get_or_build_scope_knowledge_index
    try:
        await run.start(files, probe.BENCH/'examples/rag_eval/bench_v0/questions.jsonl', {'mode': 'graph_expansion_ablation'})
        async with runtime.serve():
            await runtime.reuse_documents(files)
            await runtime.wait_ready()
            async with SessionLocal() as session:
                state = await session.get(ProjectSearchState, run.project_id)
                tree = await session.get(TreeManifest, state.active_tree_version)
                graph_id = tree.manifest_json['knowledge_graph_build_id']
                graph = await session.get(KnowledgeGraphBuild, graph_id)
                units = list((await session.scalars(select(KnowledgeUnit).where(
                    KnowledgeUnit.project_id == run.project_id, KnowledgeUnit.is_current.is_(True)
                ).order_by(KnowledgeUnit.id))).all())
            assert units and all(u.features_json.get('dense') for u in units)
            assert dict(graph.manifest_json['units']) == {u.id: u.checksum for u in units}
            off_units = [copy.copy(u) for u in units]
            for unit in off_units:
                unit.features_json = {**unit.features_json, 'dense': []}
            start = time.perf_counter()
            off_graph = await asyncio.to_thread(graph_payload, off_units, KnowledgeConfig.model_validate(graph.manifest_json['config']))
            build_seconds = time.perf_counter() - start
            mode = 'on'
            observed = defaultdict(int)
            async def with_variant(session, current_versions, allowed_partitions):
                index = await original(session, current_versions, allowed_partitions)
                observed[mode] += 1
                if mode == 'on':
                    return index
                return dataclasses.replace(index, edges_by_ku=adjacency(off_graph['edges'], index.ku_by_id, set(allowed_partitions)))
            retrieval._get_or_build_scope_knowledge_index = with_variant
            protocol = {'scope':'dense graph expansion only; published routing tree remains dense',
                        'graph_id':graph_id, 'tree_version':state.active_tree_version,
                        'unit_count':len(units), 'on_edges':len(graph.manifest_json['edges']),
                        'off_edges':len(off_graph['edges']), 'off_graph_build_seconds':build_seconds,
                        'top_k':5, 'question_count':len(questions), 'order':'AB/BA alternating by question',
                        'retrieval_only':True, 'searchunit_dense':'unchanged'}
            run.manifest['probe_protocol'] = protocol
            run._write_manifest()
            print('GRAPH_ABLATION_READY '+json.dumps(protocol), flush=True)
            for i, (qid, question) in enumerate(questions.items()):
                for mode in (('on','off') if i % 2 == 0 else ('off','on')):
                    before = observed[mode]
                    measured = await runtime.ask(question.question, top_k=5, retrieval_only=True)
                    response = measured['response'] or {}
                    citations = tuple(Citation(source_path=runtime.documents[s['document_id']], span=s['content'][:180])
                                      for s in response.get('sections', []))
                    score = compute_row('graph_ablation', question, SystemAnswer(
                        answer='', citations=(), retrieved_sources=citations, latency_ms=measured['latency_ms'],
                        retrieval_latency_ms=measured['retrieval_latency_ms'], tokens_used=0, cost_usd=None))
                    rows.append({'question_id':qid, 'mode':mode, 'measurement':measured,
                                 'score':score.model_dump(mode='json'), 'index_uses':observed[mode]-before})
                    await run.checkpoint({'stage':'graph_expansion_ablation','rows':rows})
                    print(f'GRAPH_PROBE {len(rows)}/{2*len(questions)} {qid} {mode} error={measured["error"]} index_uses={observed[mode]-before}',flush=True)
            summary = {}
            for mode in ('on','off'):
                selected = [r for r in rows if r['mode'] == mode]
                summary[mode] = {'requests':len(selected), 'errors':sum(bool(r['measurement']['error']) for r in selected),
                                 'index_uses':sum(r['index_uses'] for r in selected)}
                for metric in ('retrieval_source_recall','retrieval_source_precision'):
                    values = [r['score'][metric] for r in selected if r['score'].get(metric) is not None]
                    summary[mode][metric] = statistics.fmean(values) if values else None
                values = [r['measurement']['retrieval_latency_ms'] for r in selected if r['measurement']['retrieval_latency_ms'] is not None and not r['measurement']['error']]
                summary[mode]['retrieval_p50_ms'] = statistics.median(values) if values else None
            report = {'protocol':protocol, 'summary':summary, 'rows':rows}
            (run.output_dir/'graph_expansion_ablation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
            await run.complete(report)
            print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
    except BaseException as error:
        await run.fail(error)
        raise
    finally:
        retrieval._get_or_build_scope_knowledge_index = original
        await run.close()


if __name__ == '__main__':
    probe.evaluate = evaluate
    probe.main()
