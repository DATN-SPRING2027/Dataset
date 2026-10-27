import pytest

from benchmark_quality import ir_metrics, latency_summary, parse_judge


def test_judge_rejects_unparsed_and_out_of_range_scores():
    for text in ('Looks good', 'SCORE: 9', 'SCORE: -1'):
        with pytest.raises(ValueError):
            parse_judge(text)
    assert parse_judge('SCORE: 4.5\nRATIONALE: Supported')['score'] == 4.5


def test_latency_keeps_failed_attempts_separate_and_does_not_invent_ttft():
    rows = [{'latency_ms': 100, 'retrieval_latency_ms': 20, 'first_token_ms': 30, 'error': None},
            {'latency_ms': 30000, 'retrieval_latency_ms': None, 'first_token_ms': None, 'error': {'code': 'TimeoutError'}}]
    report = latency_summary(rows)
    assert report['requests'] == 2 and report['errors'] == 1
    assert report['successful']['latency_ms']['p50_ms'] == 100
    assert report['all_attempts']['latency_ms']['p95_ms'] == 30000
    assert report['all_attempts']['first_token_ms']['n'] == 1


def test_ir_metrics_use_fixed_k_and_rank_discount_with_multiple_relevant_docs():
    metrics = ir_metrics(['wrong-a', 'wrong-b', 'relevant'], {'relevant', 'missing'}, 5)
    assert metrics['recall'] == .5
    assert metrics['precision'] == .2
    assert metrics['mrr'] == pytest.approx(1/3)
    assert metrics['map'] == pytest.approx(1/6)
    assert 0 < metrics['ndcg'] < .5
    assert ir_metrics(['relevant'], {'relevant'}, 10)['precision'] == .1
