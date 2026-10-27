"""Compatibility launcher for a fresh SAG benchmark in the application schema."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import runpy
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('benchmark', choices=('retrievalci', 'vn_mteb'))
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    sag = root.parent / 'sag-laya-integration/SAG'
    stamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
    output = root / 'reports' / f'{args.benchmark}-e2e-{stamp}'
    output.mkdir()
    for name in ('RUN_ID', 'PROJECT_ID', 'SOURCE_ID', 'SOURCE_CONFIG_ID',
                 'REUSE_RUN_ID', 'REUSE_MANIFEST_SHA256'):
        os.environ.pop('SAG_BENCHMARK_' + name, None)
    os.environ['SAG_BENCHMARK_SCHEMA'] = 'sag'
    os.environ['SAG_BENCHMARK_OUTPUT_DIR'] = str(output / 'result')
    sys.path[:0] = [str(sag / 'apps/api'), str(root)]
    os.chdir(sag)
    scripts = {'retrievalci': 'RetrievalCI_Bench_v0_2026/scripts/run_bench_v0_sag.py',
               'vn_mteb': 'VN_MTEB_RAG_Bench_2026/scripts/run_vn_mteb_sag.py'}
    script = root / scripts[args.benchmark]
    print(f'BENCH_OUTPUT={output}', flush=True)
    sys.argv = [str(script)]
    runpy.run_path(str(script), run_name='__main__')


if __name__ == '__main__':
    main()
