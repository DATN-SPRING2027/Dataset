"""Automated verification tests for the Isolated Pre-Retrieve Benchmark Suite (with Live SiliconFlow Kev-4b)."""
from __future__ import annotations

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from benchmark_isolated_pre_retrieve import run_isolated_pre_retrieve_benchmark


def test_isolated_pre_retrieve_ablation_metrics() -> None:
    report = run_isolated_pre_retrieve_benchmark(refresh_live=False)
    assert report["total_queries_evaluated"] == 275

    overall = report["overall"]
    b0 = overall["B0_vanilla_fixed_k5"]
    b1 = overall["B1_static_wide_k10"]
    b2 = overall["B2_local_regex_qsp_v2"]
    b3 = overall["B3_live_kev4b_only"]
    b4 = overall["B4_sag_live_kev4b_plus_qsp_v2"]

    # 1. Full Production SAG (B4 = Live Kev-4b + qsp-v2) achieves 100% Gate Accuracy & 100% 7-Axis Exact Match
    assert b4["gate_accuracy_pct"] == 100.0
    assert b4["seven_axis_exact_match_pct"] == 100.0
    assert b3["seven_axis_exact_match_pct"] == 64.0  # Kev-4b alone lacks explicit N extraction
    assert b0["seven_axis_exact_match_pct"] < 15.0

    # 2. Live Kev-4b + qsp-v2 (B4) outperforms both Local Regex Only (B2) and Kev-4b Only (B3) on Recall Ceiling
    assert b4["overall_budget_sufficiency_pct"] > b2["overall_budget_sufficiency_pct"] > b0["overall_budget_sufficiency_pct"]
    assert b4["overall_recall_ceiling_pct"] >= 99.8
    assert b4["heavy_doc_k6plus_sufficiency_pct"] > 90.0
    assert b2["heavy_doc_k6plus_sufficiency_pct"] == 78.57
    assert b3["heavy_doc_k6plus_sufficiency_pct"] == 50.0
    assert b0["heavy_doc_k6plus_sufficiency_pct"] == 0.0

    # 3. Live Kev-4b enables Fast Vector Strategy routing (84.5% vector vs 0% vector in fallback B2)
    assert b4["fast_vector_strategy_pct"] > 80.0
    assert b2["fast_vector_strategy_pct"] == 0.0

    # 4. Single-Hop Precision Ceiling & Context Token Waste Reduction
    assert b4["single_hop_precision_ceiling_pct"] >= 48.0
    assert b3["single_hop_precision_ceiling_pct"] < 25.0
    assert b0["single_hop_precision_ceiling_pct"] == 20.0
    assert b1["single_hop_precision_ceiling_pct"] == 10.0

    # 5. Real SiliconFlow SystemOne (Kev-4b) Token Usage, Cost & Latency
    assert b4["decision_input_tokens_per_query"] > 500.0
    assert b4["decision_output_tokens_per_query"] > 400.0
    assert b4["planner_tokens_per_query"] > 900.0
    assert b4["total_tokens_275_queries"] == 262098
    assert b4["planner_cost_per_10k_queries_usd"] > 0.50
    assert b4["latency_p50_ms"] > 1000.0
    assert b2["planner_tokens_per_query"] == 0.0
    assert b2["planner_cost_per_10k_queries_usd"] == 0.0
