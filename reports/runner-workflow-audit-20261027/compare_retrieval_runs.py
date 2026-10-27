"""Read-only comparison of retained RetrievalCI per-question evidence."""
import asyncio
import json
import os
import statistics
import sys
from collections import Counter
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

ROOT = Path(__file__).resolve().parents[2]
SAG = ROOT.parent / 'sag-laya-integration/SAG'
sys.path.insert(0, str(SAG / 'apps/api'))
os.chdir(SAG)
from sag_api.core.config import settings

async def main():
    old = json.loads((ROOT/'RetrievalCI_Bench_v0_2026/reports/20261026T141834Z-3e858c/bench_v0_sag_diagnostics.json').read_text(encoding='utf-8'))
    path = ROOT/'reports/retrievalci-fixed-20261027081141/result/run_manifest.json'
    manifest = json.loads(path.read_text(encoding='utf-8'))
    url = make_url(settings.database_url)
    engine = create_async_engine(url.set(query={k: v for k, v in url.query.items() if k != 'search_path'}),
        connect_args={'server_settings': {'search_path': manifest['schema']}})
    try:
        async with engine.connect() as conn:
            new = await conn.scalar(text('SELECT diagnostics_json FROM benchmark_runs WHERE id=:id'), {'id':manifest['run_id']})
    finally:
        await engine.dispose()
    assert set(old) == set(new) and len(old) == 50
    rows=[]
    for key in old:
        a,b=old[key],new[key]
        assert a['question'] == b['question']
        assert set(a['ground_truth_citations']) == set(b['ground_truth_citations'])
        response=b.get('response') or {}
        stats=response.get('stats') or {}
        prefix_docs = list(dict.fromkeys(manifest['document_paths'].get(s.get('document_id'), '')
                                        for s in (response.get('sections') or [])[:5]))
        gold = set(a['ground_truth_citations'])
        rows.append({'question_id':key, 'tier':a['tier'], 'gold_docs':len(a['ground_truth_citations']),
            'old_docs':len(a['retrieved_unique_docs']), 'new_docs':len(b['retrieved_unique_docs']),
            'old_recall':a['retrieval_source_recall'], 'new_recall':b['retrieval_source_recall'],
            'old_precision':a['retrieval_source_precision'], 'new_precision':b['retrieval_source_precision'],
            'old_ms':a['latency_ms'], 'new_ms':b['retrieval_latency_ms'],
            'old_stages':a.get('stats',{}).get('stage_latencies_ms',{}),
            'new_stages':stats.get('stage_latencies_ms',{}),
            'new_sections':len(response.get('sections') or []), 'stop':stats.get('retrieval_stop_reason'),
            'prefix5_recall':len(gold.intersection(prefix_docs))/len(gold) if gold else None,
            'waves':stats.get('adaptive_waves'), 'effective_top_k':stats.get('effective_top_k'),
            'fallback':stats.get('selection_fallback_reason'), 'error':b.get('error')})
    def median(values):
        return round(statistics.median(values),2) if values else None
    stage_keys=set().union(*(r['old_stages'].keys() for r in rows),*(r['new_stages'].keys() for r in rows))
    summary={'questions':len(rows),'same_questions_and_gold':True,
        'median_old_docs':median([r['old_docs'] for r in rows]),'median_new_docs':median([r['new_docs'] for r in rows]),
        'median_new_sections':median([r['new_sections'] for r in rows]),
        'recall_changed':[{k:r[k] for k in ('question_id','old_recall','new_recall','gold_docs','old_docs','new_docs','stop')}
                          for r in rows if r['old_recall'] is not None and r['new_recall'] is not None and r['old_recall'] != r['new_recall']],
        'precision_direction':dict(Counter('higher' if r['new_precision'] > r['old_precision'] else 'lower' if r['new_precision'] < r['old_precision'] else 'equal'
                                           for r in rows if r['old_precision'] is not None and r['new_precision'] is not None)),
        'prefix5_recall_mean':statistics.fmean(r['prefix5_recall'] for r in rows if r['prefix5_recall'] is not None),
        'prefix5_recall_changes':[{k:r[k] for k in ('question_id','gold_docs','old_recall','prefix5_recall','new_recall')}
                                  for r in rows if r['old_recall'] is not None and r['prefix5_recall'] != r['old_recall']],
        'stop_counts':dict(Counter(r['stop'] for r in rows)), 'wave_counts':dict(Counter(r['waves'] for r in rows)),
        'stage_medians_ms':{key:{'old':median([r['old_stages'][key] for r in rows if r['old_stages'].get(key) is not None]),
                                 'new':median([r['new_stages'][key] for r in rows if r['new_stages'].get(key) is not None])}
                            for key in sorted(stage_keys)},'rows':rows}
    target=Path(__file__).with_name('old_vs_new_question_comparison.json')
    target.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='rows'},ensure_ascii=False,indent=2))

if __name__=='__main__': asyncio.run(main())
