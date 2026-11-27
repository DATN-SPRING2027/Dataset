"""Credibility, split-disjointness, latency-invariant, ACL-deny, and non-replay gates
for `Dataset` (`SAG-BENCH-001..004`, `DEP-004`, `DOC-006`).
"""
from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path

import pytest

DATASET_ROOT = Path(__file__).resolve().parent
if str(DATASET_ROOT) not in sys.path:
    sys.path.insert(0, str(DATASET_ROOT))

from benchmark_quality import (
    build_four_axis_scorecard,
    compute_mandatory_coverage,
    evaluate_must_not_cite,
    latency_summary,
    validate_dataset_splits_and_provenance,
    validate_latency_row,
    validate_live_benchmark_manifest,
)


def test_latency_summary_prevents_wixqa_ttft_p95_exceeding_e2e_p95() -> None:
    # Reproduce the exact n=18 TTFT vs n=20 E2E subset mismatch that caused TTFT p95 (81.6s) > E2E p95 (20.8s).
    rows = [
        {"question_id": f"q{i}", "retrieval_latency_ms": 4000, "first_token_ms": 12000 + i * 200, "latency_ms": 12100 + i * 200, "error": None}
        for i in range(17)
    ]
    rows.append({"question_id": "q_slow", "retrieval_latency_ms": 6000, "first_token_ms": 81582.88, "latency_ms": 81583.90, "error": None})
    # Two abstention rows with no summary delta (first_token_ms=None)
    rows.append({"question_id": "q_abs1", "retrieval_latency_ms": 4500, "first_token_ms": None, "latency_ms": 18000, "error": None})
    rows.append({"question_id": "q_abs2", "retrieval_latency_ms": 4600, "first_token_ms": None, "latency_ms": 19000, "error": None})

    report = latency_summary(rows, strict_invariants=True)
    matched = report["matched_answered"]
    assert matched["first_token_ms"]["n"] == matched["latency_ms"]["n"] == 18
    assert matched["retrieval_latency_ms"]["p50_ms"] <= matched["first_token_ms"]["p50_ms"] <= matched["latency_ms"]["p50_ms"]
    assert matched["retrieval_latency_ms"]["p95_ms"] <= matched["first_token_ms"]["p95_ms"] <= matched["latency_ms"]["p95_ms"]


def test_latency_row_rejects_inverted_timestamps() -> None:
    with pytest.raises(ValueError, match="Latency invariant violation"):
        validate_latency_row(
            {"question_id": "bad", "retrieval_latency_ms": 500, "first_token_ms": 900, "latency_ms": 700, "error": None},
            strict=True,
        )


def test_mandatory_coverage_handles_retrievalci_full_sentence_rubric_claims() -> None:
    terms = (
        "The default per file upload size limit (max_file_size) for multipart uploads on OpenAI-compatible endpoints is 10 MiB.",
        "The default total request size limit (max_total_request_size) for multipart uploads on OpenAI-compatible endpoints is 50 MiB.",
    )
    paraphrased_answer = (
        "Multipart uploads on OpenAI-compatible endpoints enforce max_file_size=10 MiB per file "
        "and max_total_request_size=50 MiB for the total request size limit by default."
    )
    res = compute_mandatory_coverage(paraphrased_answer, terms)
    assert res["mode"] == "rubric_claim_token"
    assert res["coverage"] == 1.0


def test_must_not_cite_enforces_versioned_rules_and_excludes_abstentions() -> None:
    # Versioned ban on @2.0-draft must NOT falsely flag approved base DOC-CHKO-20260416-01
    ok = evaluate_must_not_cite(["DOC-CHKO-20260416-01"], ["DOC-CHKO-20260416-01@2.0-draft"], answer_status="answered")
    assert ok["violation_count"] == 0
    assert ok["has_valid_citation"] is True

    # Exact versioned violation caught
    bad = evaluate_must_not_cite(["DOC-CHKO-20260416-01@2.0-draft"], ["DOC-CHKO-20260416-01@2.0-draft"], answer_status="answered")
    assert bad["violation_count"] == 1
    assert bad["has_valid_citation"] is False

    # Base ban catches versioned form too
    base_bad = evaluate_must_not_cite(["DOC-DRAFT-001@v1"], ["DOC-DRAFT-001"], answer_status="answered")
    assert base_bad["violation_count"] == 1

    # Abstention (e.g. RAG-007) must NEVER be scored as has_valid_citation=True
    abstain = evaluate_must_not_cite(["DOC-1"], [], answer_status="no_answer")
    assert abstain["abstention_filtered"] is True
    assert abstain["has_valid_citation"] is False


def test_enterprise_datasets_have_zero_dev_test_overlap_and_honest_review_status() -> None:
    eval_files = sorted(DATASET_ROOT.rglob("evaluation/*.jsonl"))
    assert len(eval_files) == 10  # 7 Project1 + 3 Org2..4
    total_dev = 0
    total_test = 0
    for path in eval_files:
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        prov = validate_dataset_splits_and_provenance(rows, allow_unreviewed=True)
        assert prov["dev_test_disjoint"] is True
        assert prov["dev_test_overlap_count"] == 0
        # Honest provenance: synthetic cases must NOT be fabricated as reviewed
        assert prov["all_human_reviewed"] is False
        assert prov["review_status_counts"]["unreviewed"] == len(rows)
        total_dev += prov["split_counts"].get("dev", 0)
        total_test += prov["split_counts"].get("test", 0)
    assert total_dev == 271
    assert total_test == 87

    # Publication gate rejects unreviewed test split
    sample_rows = [
        {"case_id": "C1", "split": "dev", "review_status": "unreviewed"},
        {"case_id": "C2", "split": "test", "review_status": "unreviewed"},
    ]
    with pytest.raises(ValueError, match="Publication gate rejected"):
        validate_dataset_splits_and_provenance(sample_rows, allow_unreviewed=False)

    # Overlap detector catches dev+test leakage
    leaked_rows = [
        {"case_id": "DUP-1", "split": "dev", "review_status": "unreviewed"},
        {"case_id": "DUP-1", "split": "test", "review_status": "unreviewed"},
    ]
    with pytest.raises(ValueError, match="Duplicate benchmark case IDs"):
        validate_dataset_splits_and_provenance(leaked_rows, allow_unreviewed=True)


def test_all_seven_datasets_have_non_zero_acl_deny_cases() -> None:
    from run_all_datasets_sag import ALL_SEVEN_KEYS, load_acl_deny_cases

    for key in ALL_SEVEN_KEYS:
        deny_cases = load_acl_deny_cases(key)
        assert len(deny_cases) > 0, f"{key} has 0 ACL deny cases!"


def test_four_axis_scorecard_separates_ir_from_unmeasured_answer_accuracy() -> None:
    card = build_four_axis_scorecard(
        retrieval_metrics={"recall_at_5": 0.96, "precision_at_5": 0.88},
        answer_quality={"protocol": {"judge_model": None}, "quality_summary": {"faithfulness": {"n_scored": 0, "mean": None}, "relevance": {"n_scored": 0, "mean": None}}},
        citation_metrics={"answer_citation_precision": 0.95, "answer_citation_recall": 0.85, "must_not_cite_violations": 0},
        acl_evaluation={"total_acl_cases": 6, "deny_accuracy": 1.0, "leaked_citations_count": 0, "enforcement_mode": "live_sag_http_acl"},
        measurement_mode="live",
    )
    assert card["retrieval_accuracy"]["recall_at_5"] == 0.96
    assert card["answer_accuracy"]["measured"] is False
    assert card["answer_accuracy"]["n_scored"] == 0
    assert card["acl_safety"]["acl_deny_cases_count"] == 6
    assert card["acl_safety"]["measured"] is True


def test_manifest_gate_blocks_cache_replay_and_zero_acl_cases() -> None:
    bad_manifest = {
        "cached_reused_count": 301,
        "acl_deny_cases_count": 0,
        "git_commit": "",
    }
    errors = validate_live_benchmark_manifest(bad_manifest)
    assert len(errors) == 3

    good_manifest = {
        "cached_reused_count": 0,
        "acl_deny_cases_count": 6,
        "git_commit": "2e4bc3c65971847085c12ff6212040a47b513c11",
        "quality_latency": {"latency": {"first_pass": {"invariant_violations": []}}},
    }
    assert validate_live_benchmark_manifest(good_manifest) == []


def test_seven_projects_pre_retrieve_disables_cache_replay_by_default() -> None:
    from run_seven_projects_full_pre_retrieve import _build_arg_parser, _needs_live_rerun

    args = _build_arg_parser().parse_args([])
    assert args.allow_cache_replay is False
    need_live, reason = _needs_live_rerun("any query", 1.0, True, allow_cache_replay=False)
    assert need_live is True
    assert "no_cache_replay" in reason


def test_pyproject_toml_valid_and_active_scripts_have_no_hardcoded_machine_paths() -> None:
    pyproject = tomllib.loads((DATASET_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["project"]["requires-python"].startswith(">=3.12")
    assert len(pyproject["project"]["dependencies"]) >= 8

    forbidden = re.compile(r"(D:[/\\]DoAnTotnghiep|C:[/\\]Users[/\\]This PC)", re.I)
    active_files = [
        DATASET_ROOT / "run_seven_projects_full_pre_retrieve.py",
        DATASET_ROOT / "run_all_datasets_sag.py",
        DATASET_ROOT / "sag_benchmark_runtime.py",
        DATASET_ROOT / "benchmark_isolated_pre_retrieve.py",
        DATASET_ROOT / "benchmark_quality.py",
        DATASET_ROOT / "summarize_benchmark_runs.py",
        DATASET_ROOT / "sync_benchmark_projects_mongo.mjs",
        DATASET_ROOT / "BENCHMARK_RUNS.md",
        DATASET_ROOT / "VN_MTEB_RAG_Bench_2026" / "scripts" / "build_vn_mteb_bench.py",
    ]
    for path in active_files:
        text = path.read_text(encoding="utf-8")
        assert not forbidden.search(text), f"Hardcoded machine path found in {path}"
