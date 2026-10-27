"""HTTP measurement in a process independent of the API event loop."""
from __future__ import annotations
import asyncio
import json
import multiprocessing
import os
import time
from contextlib import AsyncExitStack
import httpx


def _worker(connection, base_url):
    async def run():
        async with httpx.AsyncClient(base_url=base_url, timeout=None, trust_env=False) as client:
            while True:
                options = await asyncio.to_thread(connection.recv)
                if options is None:
                    return
                result = await measure_search(client, **options)
                result["http_client_pid"] = os.getpid()
                connection.send(result)
    try:
        asyncio.run(run())
    finally:
        connection.close()


class QueryClientProcess:
    def __init__(self, base_url):
        context = multiprocessing.get_context("spawn")
        self.connection, child = context.Pipe()
        self.process = context.Process(target=_worker, args=(child, base_url))
        self.process.start()
        child.close()
        self.lock = asyncio.Lock()

    async def ask(self, options):
        async with self.lock:
            def exchange():
                self.connection.send(options)
                while not self.connection.poll(.1):
                    if not self.process.is_alive():
                        raise RuntimeError("Benchmark HTTP client exited before returning its measurement")
                return self.connection.recv()
            return await asyncio.to_thread(exchange)

    async def close(self):
        def stop():
            try:
                if self.process.is_alive():
                    self.connection.send(None)
                    self.process.join(5)
            finally:
                if self.process.is_alive():
                    self.process.terminate()
                    self.process.join(2)
                if self.process.is_alive():
                    self.process.kill()
                    self.process.join()
                self.connection.close()
        await asyncio.to_thread(stop)

async def measure_search(client, authorization, source_id, policy, query, *, top_k=None, retrieval_only=False):
    start = time.perf_counter()
    result = None
    deadline = asyncio.get_running_loop().time() + policy['first_result_seconds']
    response_body = None
    error = None
    first_token_ms = None
    try:
        async with AsyncExitStack() as stack:
            async with asyncio.timeout_at(deadline):
                response = await stack.enter_async_context(client.stream('POST', '/api/v1/search/stream',
                    headers={'Authorization': authorization},
                    json={'query': query, 'source_ids': [source_id], **({'top_k': top_k} if top_k is not None else {})},
                    timeout=None))
            response.raise_for_status()
            lines = response.aiter_lines().__aiter__()
            frame = []
            while True:
                try:
                    async with asyncio.timeout_at(deadline):
                        line = await anext(lines)
                except StopAsyncIteration:
                    break
                # The web client resets idle on received bytes after result, including SSE pings.
                if result is not None:
                    deadline = asyncio.get_running_loop().time() + policy['stream_idle_seconds']
                if line:
                    frame.append(line)
                    continue
                event, data = parse_frame(frame)
                frame = []
                if event == 'result':
                    if result is not None:
                        raise ValueError('Duplicate retrieval result')
                    result = data
                    retrieval_ms = (time.perf_counter() - start) * 1000
                    if retrieval_only:
                        response_body = data
                        break
                elif event == 'completed':
                    response_body = data
                    break
                elif event == 'summary.delta' and data.get('delta') and first_token_ms is None:
                    first_token_ms = (time.perf_counter() - start) * 1000
                elif event == 'error':
                    error = data
                    break
                if event in ('result', 'summary.delta'):
                    deadline = asyncio.get_running_loop().time() + policy['stream_idle_seconds']
    except (TimeoutError, httpx.HTTPError) as exc:
        error = {'code': type(exc).__name__}
    if response_body is None and error is None:
        error = {'code': 'incomplete_search_stream'}
    return {'response': response_body or result, 'retrieval_latency_ms': retrieval_ms if result else None,
            'latency_ms': (time.perf_counter() - start) * 1000, 'first_token_ms': first_token_ms, 'error': error}

def parse_frame(lines: list[str]):
    event = ''
    data = []
    for line in lines:
        if line.startswith('event:'):
            event = line[6:].strip()
        elif line.startswith('data:'):
            data.append(line[5:].lstrip())
    return (event, json.loads('\n'.join(data))) if data else ('', None)
