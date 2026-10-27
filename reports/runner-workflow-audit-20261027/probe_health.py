"""Measure public health responsiveness from outside the API process."""
import argparse
import json
import statistics
import time
from pathlib import Path

import httpx

parser = argparse.ArgumentParser()
parser.add_argument('url')
parser.add_argument('output', type=Path)
parser.add_argument('--seconds', type=int, default=300)
args = parser.parse_args()
samples = []
deadline = time.monotonic() + args.seconds
with httpx.Client(timeout=3, trust_env=False) as client:
    while time.monotonic() < deadline:
        started = time.perf_counter()
        error = None
        try:
            client.get(args.url + '/api/v1/system/health').raise_for_status()
        except Exception as exc:
            error = type(exc).__name__
        samples.append({'ms': round((time.perf_counter() - started)*1000, 2), 'error': error})
        args.output.write_text(json.dumps({'samples': samples}, indent=2), encoding='utf-8')
        time.sleep(1)
values = sorted(s['ms'] for s in samples)
result = {'requests':len(samples), 'errors':sum(s['error'] is not None for s in samples),
          'p50_ms':statistics.median(values), 'p95_ms':values[max(0, int(len(values)*.95)-1)],
          'max_ms':max(values), 'samples':samples}
args.output.write_text(json.dumps(result,indent=2),encoding='utf-8')
print({k:v for k,v in result.items() if k != 'samples'})
