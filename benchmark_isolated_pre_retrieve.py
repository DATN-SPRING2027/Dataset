"""Isolated Pre-Retrieve Benchmark Suite (Adaptive-RAG / RouterBench / CRAG 7-Axis Protocol).

Evaluates the SAG Pre-Retrieve layer in 100% component isolation (Zero DB, Zero Vector Index,
Zero LLM Answer Generation) across 4 benchmark suites (275 real & canonical queries):
  1. EnterpriseRAG-Bench (RetrievalCI Bench-v0, 50 queries: single_hop, multi_hop, contradiction, unanswerable)
  2. VN-MTEB RAG Bench 2026 (50 Vietnamese queries: Zalo Legal single-hop + HotpotQA-VN multi-hop)
  3. Enterprise Multi-Org Governance Suite (Org2 Nova, Org3 CloudOps, Org4 MediFlow: 150 real queries)
  4. CRAG / qsp-v2 7-Axis & Intent Stress Benchmark (25 labeled queries covering all 7 question types)

Compares 5 Pre-Retrieve configurations head-to-head:
  - B0_vanilla_fixed_k5            : Standard RAG default (fixed top_k=5, no Decision Router, no qsp-v2)
  - B1_static_wide_k10             : Naive wide top_k=10 (no Decision Router, no qsp-v2)
  - B2_local_regex_qsp_v2          : SAG with Decision API disabled (local _fallback_route + QueryAnalysis + qsp-v2)
  - B3_live_kev4b_only             : Live SiliconFlow SystemOne (Kev-4b) Decision Router alone (without qsp-v2 cardinality/anchors)
  - B4_sag_live_kev4b_plus_qsp_v2  : Full Production SAG Pre-Retrieve (Live SiliconFlow Kev-4b Decision Router + QueryAnalysis + qsp-v2)
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import statistics
import sys
import time
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

DATASET_ROOT = Path(__file__).resolve().parent
BENCH_V0_ROOT = DATASET_ROOT / "RetrievalCI_Bench_v0_2026"
VN_MTEB_ROOT = DATASET_ROOT / "VN_MTEB_RAG_Bench_2026"
SAG_ROOT = DATASET_ROOT.parent / "sag-laya-integration" / "SAG"
API_ROOT = SAG_ROOT / "apps" / "api"
LIVE_CACHE_PATH = DATASET_ROOT / "reports" / "siliconflow_kev4b_live_cache.jsonl"

if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from sag_api.core.config import settings
from sag_api.services.decision_router import (
    CHAT_HIGH_CONFIDENCE,
    _DECISION_QUESTIONS,
    _fallback_route,
    _route_from_answers,
)
from sag_api.services.query_analysis import QueryFeatures, analyze_query, extract_query_features
from sag_api.services.query_strategy_planner import QueryStrategyPlan, plan_query
from sag_api.services.retrieval_plan import OutputMode

DEFAULT_N_PASSAGE_ANSWER = 5
DEFAULT_N_COMPARE = 8
DEFAULT_N_DOCUMENT_LIST = 10
DEFAULT_N_EXHAUSTIVE = 50
DEFAULT_N_SUMMARIZE = 10
DEFAULT_N_OPEN = 1

# Exact production fast-path patterns from sag_api/services/agent_service.py (lines 65-110)
_GREETING_PREFIX = (
    r"(?:(?:xin\s+)?chào(?:\s+(?:bạn|cậu|anh|chị|em|mình|continuum(?:\s+ai)?))?"
    r"|alo|hi|hello|hey|chào\s+buổi\s+(?:sáng|chiều|tối))"
)
_IDENTITY_QUESTION = (
    r"(?:bạn\s+là\s+ai|(?:tên(?:\s+của)?\s+bạn|bạn\s+tên)(?:\s+là)?\s+gì"
    r"|who\s+are\s+you|what(?:'|’|\s+is)\s+your\s+name)"
)
_USER_PRONOUN = r"(?:tôi|mình|em|anh|chị)"
_USER_NAME_QUESTION = (
    rf"(?:(?:bạn\s+(?:có\s+)?)?biết\s+(?:tên(?:\s+của)?\s+{_USER_PRONOUN}|{_USER_PRONOUN}\s+tên)(?:\s+là\s+gì)?(?:\s+không)?"
    rf"|(?:tên(?:\s+của)?\s+{_USER_PRONOUN}|{_USER_PRONOUN}\s+tên)(?:\s+là)?\s+gì"
    r"|what(?:'|’|\s+is)\s+my\s+name"
    r"|do\s+you\s+know\s+my\s+name)"
)
_CONVERSATIONAL_SELF_OR_USER_QUERY = rf"(?:{_IDENTITY_QUESTION}|{_USER_NAME_QUESTION})"
_DIRECT_INTENT = re.compile(
    r"^(?!"
    r".*(?:tài\s+liệu|dự\s+án|project|hệ\s+thống|schema|file|\.md|quy\s+định|chính\s+sách|báo\s+cáo|quyền|role|nhóm|team)"
    r")(?:"
    rf"{_GREETING_PREFIX}"
    r"|cảm\s+ơn(?:\s+(?:bạn|nhiều))?(?:\s+nhé)?|thanks|thank\s+you|tạm\s+biệt|bye"
    rf"|(?:{_GREETING_PREFIX}[!！?？。,.，\s]+)?{_CONVERSATIONAL_SELF_OR_USER_QUERY}"
    rf"(?:(?:[!！?？。,.，;\s]+|\s+(?:và|còn|thế\s+còn|and)\s+){_CONVERSATIONAL_SELF_OR_USER_QUERY})?"
    rf"|(?:{_GREETING_PREFIX}[!！?？。,.，\s]+)?"
    r"(?:hãy\s+|vui\s+lòng\s+|bạn\s+có\s+thể\s+)?"
    r"(?:giới\s+thiệu|cho\s+biết)[^\n]{0,60}(?:khả\s+năng|vai\s+trò|hỗ\s+trợ|giúp|về\s+bạn)[^\n]{0,40}\bbạn\b[^\n]{0,25}"
    r")[!！?？。,.，\s]*$",
    re.IGNORECASE,
)
_SIMPLE_ARITHMETIC = re.compile(r"^[\d\s+\-*/().=？?]+$")

AVG_TOKENS_PER_RETRIEVED_SLOT = 380  # Average tokens per hydrated SearchUnit chunk in prompt
# SiliconFlow small-model serverless pricing ($0.06 / 1M tokens per sag_api/core/token_usage.py)
SILICONFLOW_KEV4B_PRICE_PER_1M_USD = 0.06


@dataclass(frozen=True)
class IsolatedQueryCase:
    case_id: str
    suite: str
    category: str
    query: str
    gold_doc_count: int
    expected_need_retrieval: bool = True
    expected_multi_hop: bool = False
    expected_has_identifiers: bool = False
    expected_target: str | None = None
    expected_output: str | None = None
    expected_effective_n: int | None = None
    expected_per_doc_limit: int | None = None
    expected_order: str | None = None
    expected_decomposition: str | None = None
    expected_memory_scope: str | None = None
    expected_temporal_mode: str | None = None


@dataclass(frozen=True)
class PreRetrieveDecisionOutput:
    strategy_name: str
    case_id: str
    need_retrieval: bool
    suggested_strategy: str
    answer_shape: str
    target_unit: str
    selection_mode: str
    output_mode: str
    cardinality_mode: str
    count_source: str
    effective_top_k: int
    initial_doc_admission: int
    max_doc_capacity: int
    first_wave_candidates: int
    per_document_limit: int | None
    order_mode: str
    decomposition_mode: str
    subquery_count: int
    multi_hop_detected: bool
    exact_identifiers_extracted: int
    memory_scope: str
    temporal_mode: str
    latency_ms: float
    decision_input_tokens: int
    decision_output_tokens: int
    planner_tokens_used: int
    planner_cost_usd: float


def _is_production_direct_chitchat(query: str) -> bool:
    """Use SAG's production _DIRECT_INTENT and _SIMPLE_ARITHMETIC fast-path gates."""
    normalized = unicodedata.normalize("NFC", " ".join((query or "").strip().split()))
    if not normalized:
        return True
    return bool(_DIRECT_INTENT.fullmatch(normalized) or _SIMPLE_ARITHMETIC.fullmatch(normalized))


# ---------------------------------------------------------------------------
# Live SiliconFlow SystemOne (Kev-4b) Decision Cache Loader / Fetcher
# ---------------------------------------------------------------------------
_LIVE_KEV4B_CACHE: dict[str, dict[str, Any]] = {}


def _fetch_single_live_kev4b(case: IsolatedQueryCase) -> dict[str, Any]:
    url = f"{settings.siliconflow_base_url.rstrip('/')}/systemone"
    headers = {
        "Authorization": f"Bearer {settings.siliconflow_api_key}",
        "Content-Type": "application/json",
    }
    for attempt in range(3):
        t0 = time.perf_counter()
        try:
            resp = httpx.post(
                url,
                headers=headers,
                json={
                    "model": settings.decision_model,
                    "state": {"query": case.query},
                    "questions": _DECISION_QUESTIONS,
                },
                timeout=25.0,
            )
            resp.raise_for_status()
            ms = round((time.perf_counter() - t0) * 1000.0, 2)
            payload = resp.json()
            return {
                "case_id": case.case_id,
                "suite": case.suite,
                "query": case.query,
                "model": str(payload.get("model") or settings.decision_model),
                "latency_ms": ms,
                "answers": payload.get("answers") or {},
                "usage": payload.get("usage") or {},
                "error": None,
            }
        except Exception as exc:  # noqa: BLE001
            if attempt == 2:
                return {
                    "case_id": case.case_id,
                    "suite": case.suite,
                    "query": case.query,
                    "model": "error",
                    "latency_ms": 0.0,
                    "answers": {},
                    "usage": {},
                    "error": str(exc),
                }
            time.sleep(0.5)
    raise RuntimeError("Unreachable")


def ensure_live_kev4b_cache(cases: list[IsolatedQueryCase], *, refresh_live: bool = False) -> dict[str, dict[str, Any]]:
    """Load verified live SiliconFlow Kev-4b responses, fetching any missing queries via HTTP."""
    global _LIVE_KEV4B_CACHE
    if not refresh_live and LIVE_CACHE_PATH.exists():
        for line in LIVE_CACHE_PATH.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                if not row.get("error"):
                    _LIVE_KEV4B_CACHE[row["case_id"]] = row

    missing = [c for c in cases if refresh_live or c.case_id not in _LIVE_KEV4B_CACHE]
    if missing and settings.siliconflow_api_key:
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
            fetched = list(ex.map(_fetch_single_live_kev4b, missing))
        for row in fetched:
            if not row.get("error"):
                _LIVE_KEV4B_CACHE[row["case_id"]] = row
        LIVE_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LIVE_CACHE_PATH.open("w", encoding="utf-8") as f:
            for c in cases:
                if c.case_id in _LIVE_KEV4B_CACHE:
                    f.write(json.dumps(_LIVE_KEV4B_CACHE[c.case_id], ensure_ascii=False) + "\n")
    return _LIVE_KEV4B_CACHE


# ---------------------------------------------------------------------------
# 1. Five Pre-Retrieve Strategies Under Test (Isolated)
# ---------------------------------------------------------------------------
def run_b0_vanilla_fixed_k5(query: str, case_id: str) -> PreRetrieveDecisionOutput:
    """B0: Standard RAG without Pre-Retrieve (fixed top_k=5, single-shot query, no routing)."""
    t0 = time.perf_counter_ns()
    _ = (query or "").strip()
    elapsed_ms = (time.perf_counter_ns() - t0) / 1_000_000.0
    return PreRetrieveDecisionOutput(
        strategy_name="B0_vanilla_fixed_k5",
        case_id=case_id,
        need_retrieval=True,
        suggested_strategy="vector",
        answer_shape="fact_answer",
        target_unit="PASSAGE",
        selection_mode="RELEVANCE",
        output_mode="ANSWER",
        cardinality_mode="N",
        count_source="DEFAULT",
        effective_top_k=5,
        initial_doc_admission=5,
        max_doc_capacity=5,
        first_wave_candidates=20,
        per_document_limit=None,
        order_mode="RELEVANCE",
        decomposition_mode="NONE",
        subquery_count=1,
        multi_hop_detected=False,
        exact_identifiers_extracted=0,
        memory_scope="project_documents",
        temporal_mode="atemporal",
        latency_ms=round(elapsed_ms, 4),
        decision_input_tokens=0,
        decision_output_tokens=0,
        planner_tokens_used=0,
        planner_cost_usd=0.0,
    )


def run_b1_static_wide_k10(query: str, case_id: str) -> PreRetrieveDecisionOutput:
    """B1: Naive wide top_k=10 without Pre-Retrieve intelligence."""
    t0 = time.perf_counter_ns()
    _ = (query or "").strip()
    elapsed_ms = (time.perf_counter_ns() - t0) / 1_000_000.0
    return PreRetrieveDecisionOutput(
        strategy_name="B1_static_wide_k10",
        case_id=case_id,
        need_retrieval=True,
        suggested_strategy="vector",
        answer_shape="fact_answer",
        target_unit="PASSAGE",
        selection_mode="RELEVANCE",
        output_mode="ANSWER",
        cardinality_mode="N",
        count_source="DEFAULT",
        effective_top_k=10,
        initial_doc_admission=10,
        max_doc_capacity=10,
        first_wave_candidates=40,
        per_document_limit=None,
        order_mode="RELEVANCE",
        decomposition_mode="NONE",
        subquery_count=1,
        multi_hop_detected=False,
        exact_identifiers_extracted=0,
        memory_scope="project_documents",
        temporal_mode="atemporal",
        latency_ms=round(elapsed_ms, 4),
        decision_input_tokens=0,
        decision_output_tokens=0,
        planner_tokens_used=0,
        planner_cost_usd=0.0,
    )


def _compute_sag_doc_bounds(
    rplan,
    *,
    features: QueryFeatures,
    subquery_count: int,
) -> tuple[int, int]:
    """Compute initial_doc_admission (Wave-1) and max_doc_capacity (Wave-2) from RetrievalService."""
    effective_n = rplan.cardinality.effective_n
    per_doc = rplan.per_document_limit
    is_exhaustive = rplan.output in {
        OutputMode.LIST,
        OutputMode.COUNT,
        OutputMode.SUMMARIZE,
    }
    if per_doc == 1 or is_exhaustive:
        initial_doc_admission = effective_n
        max_doc_capacity = effective_n
    elif rplan.output == OutputMode.COMPARE or features.multi_hop or subquery_count >= 2:
        initial_doc_admission = max(3, min(effective_n, 4))
        max_doc_capacity = max(effective_n, 8)
    else:
        initial_doc_admission = 1 if effective_n == 1 else 2
        max_doc_capacity = effective_n
    return initial_doc_admission, max_doc_capacity


def run_b2_local_regex_qsp_v2(query: str, case_id: str) -> PreRetrieveDecisionOutput:
    """B2: SAG with Decision API disabled (SAG_DECISION_PROVIDER=disabled -> _fallback_route + qsp-v2)."""
    t0 = time.perf_counter_ns()
    if _is_production_direct_chitchat(query):
        elapsed_ms = (time.perf_counter_ns() - t0) / 1_000_000.0
        return PreRetrieveDecisionOutput(
            strategy_name="B2_local_regex_qsp_v2",
            case_id=case_id,
            need_retrieval=False,
            suggested_strategy="vector",
            answer_shape="chit_chat",
            target_unit="NONE",
            selection_mode="NONE",
            output_mode="ANSWER",
            cardinality_mode="ONE",
            count_source="DEFAULT",
            effective_top_k=0,
            initial_doc_admission=0,
            max_doc_capacity=0,
            first_wave_candidates=0,
            per_document_limit=None,
            order_mode="RELEVANCE",
            decomposition_mode="NONE",
            subquery_count=0,
            multi_hop_detected=False,
            exact_identifiers_extracted=0,
            memory_scope="none",
            temporal_mode="atemporal",
            latency_ms=round(elapsed_ms, 4),
            decision_input_tokens=0,
            decision_output_tokens=0,
            planner_tokens_used=0,
            planner_cost_usd=0.0,
        )

    fb_decision = _fallback_route(query, "decision_router_disabled")
    analysis = analyze_query(query, segmentation_enabled=False)
    features: QueryFeatures = analysis.features
    strat_plan: QueryStrategyPlan = plan_query(
        query,
        features=features,
        answer_shape=str(fb_decision.get("answer_shape") or "") or None,
    )
    rplan = strat_plan.retrieval_plan
    subq_count = max(1, len(rplan.decomposition.subqueries))
    initial_doc_admission, max_doc_capacity = _compute_sag_doc_bounds(
        rplan, features=features, subquery_count=subq_count
    )
    exact_id_count = (
        len(features.exact_terms) + len(features.identifier_terms) + len(features.path_terms)
    )
    elapsed_ms = (time.perf_counter_ns() - t0) / 1_000_000.0

    return PreRetrieveDecisionOutput(
        strategy_name="B2_local_regex_qsp_v2",
        case_id=case_id,
        need_retrieval=bool(fb_decision["need_retrieval"]),
        suggested_strategy=str(fb_decision["suggested_strategy"]),
        answer_shape=str(fb_decision["answer_shape"]),
        target_unit=rplan.target.value,
        selection_mode=rplan.selection.value,
        output_mode=rplan.output.value,
        cardinality_mode=rplan.cardinality.mode.value,
        count_source=rplan.cardinality.count_source.value,
        effective_top_k=rplan.cardinality.effective_n,
        initial_doc_admission=initial_doc_admission,
        max_doc_capacity=max_doc_capacity,
        first_wave_candidates=rplan.cardinality.effective_n * 4,
        per_document_limit=rplan.per_document_limit,
        order_mode=rplan.order.value,
        decomposition_mode=rplan.decomposition.mode.value,
        subquery_count=subq_count,
        multi_hop_detected=bool(features.multi_hop or rplan.output == OutputMode.COMPARE),
        exact_identifiers_extracted=exact_id_count,
        memory_scope=str(fb_decision["memory_scope"]),
        temporal_mode=str(fb_decision["temporal_mode"]),
        latency_ms=round(elapsed_ms, 4),
        decision_input_tokens=0,
        decision_output_tokens=0,
        planner_tokens_used=0,
        planner_cost_usd=0.0,
    )


def run_b3_live_kev4b_only(query: str, case_id: str) -> PreRetrieveDecisionOutput:
    """B3: Live SiliconFlow SystemOne (Kev-4b) Decision Router ALONE (without qsp-v2 regex/cardinality planner)."""
    live_entry = _LIVE_KEV4B_CACHE.get(case_id)
    if live_entry is None:
        raise RuntimeError(f"Missing live SiliconFlow Kev-4b cache entry for {case_id}")

    answers = live_entry.get("answers") or {}
    usage = live_entry.get("usage") or {}
    in_tok = int(usage.get("input_tokens", 0) or 0)
    out_tok = int(usage.get("output_tokens", 0) or 0)
    tot_tok = in_tok + out_tok
    cost_usd = (tot_tok * SILICONFLOW_KEV4B_PRICE_PER_1M_USD) / 1_000_000.0
    http_latency_ms = float(live_entry.get("latency_ms", 0.0) or 0.0)

    intent_res = answers.get("intent_type") or {}
    intent_choice = str(intent_res.get("choice", "factual_lookup")).strip().lower()
    intent_conf = float(intent_res.get("confidence", 0.5) or 0.0)
    is_chat = intent_choice in {"chit_chat", "chat", "greeting"} and intent_conf >= CHAT_HIGH_CONFIDENCE

    shape_res = answers.get("answer_shape") or {}
    raw_shape = str(shape_res.get("choice", "fact_answer")).strip().lower()
    scope_res = answers.get("memory_scope") or {}
    raw_scope = str(scope_res.get("choice", "project_documents")).strip().lower()
    temp_res = answers.get("temporal_mode") or {}
    raw_temp = str(temp_res.get("choice", "atemporal")).strip().lower()

    if is_chat:
        return PreRetrieveDecisionOutput(
            strategy_name="B3_live_kev4b_only",
            case_id=case_id,
            need_retrieval=False,
            suggested_strategy="vector",
            answer_shape="chit_chat",
            target_unit="NONE",
            selection_mode="NONE",
            output_mode="ANSWER",
            cardinality_mode="ONE",
            count_source="DEFAULT",
            effective_top_k=0,
            initial_doc_admission=0,
            max_doc_capacity=0,
            first_wave_candidates=0,
            per_document_limit=None,
            order_mode="RELEVANCE",
            decomposition_mode="NONE",
            subquery_count=0,
            multi_hop_detected=False,
            exact_identifiers_extracted=0,
            memory_scope="none",
            temporal_mode="atemporal",
            latency_ms=round(http_latency_ms, 2),
            decision_input_tokens=in_tok,
            decision_output_tokens=out_tok,
            planner_tokens_used=tot_tok,
            planner_cost_usd=cost_usd,
        )

    # Map raw Kev-4b multiple-choice answer_shape without qsp-v2 explicit number extraction
    shape_map = {
        "fact_answer": ("PASSAGE", "ANSWER", "N", DEFAULT_N_PASSAGE_ANSWER, None),
        "multi_facet_compare": ("PASSAGE", "COMPARE", "N", DEFAULT_N_COMPARE, None),
        "document_list": ("DOCUMENT", "LIST", "N", DEFAULT_N_DOCUMENT_LIST, 1),
        "exhaustive_count": ("DOCUMENT", "COUNT", "ALL", DEFAULT_N_EXHAUSTIVE, 1),
        "summarize_set": ("DOCUMENT", "SUMMARIZE", "N", DEFAULT_N_SUMMARIZE, 1),
        "open_document": ("DOCUMENT", "OPEN", "ONE", DEFAULT_N_OPEN, 1),
    }
    t_unit, o_mode, c_mode, eff_n, per_doc = shape_map.get(
        raw_shape, ("PASSAGE", "ANSWER", "N", DEFAULT_N_PASSAGE_ANSWER, None)
    )
    strat = "multi" if intent_choice == "complex_reasoning" or o_mode in {"COMPARE", "SUMMARIZE"} else "vector"

    return PreRetrieveDecisionOutput(
        strategy_name="B3_live_kev4b_only",
        case_id=case_id,
        need_retrieval=True,
        suggested_strategy=strat,
        answer_shape=raw_shape,
        target_unit=t_unit,
        selection_mode="RELEVANCE",
        output_mode=o_mode,
        cardinality_mode=c_mode,
        count_source="DEFAULT",
        effective_top_k=eff_n,
        initial_doc_admission=eff_n,
        max_doc_capacity=eff_n,
        first_wave_candidates=eff_n * 4,
        per_document_limit=per_doc,
        order_mode="RELEVANCE",
        decomposition_mode="NONE",
        subquery_count=1,
        multi_hop_detected=(intent_choice == "complex_reasoning" or raw_shape == "multi_facet_compare"),
        exact_identifiers_extracted=0,
        memory_scope=raw_scope,
        temporal_mode=raw_temp,
        latency_ms=round(http_latency_ms, 2),
        decision_input_tokens=in_tok,
        decision_output_tokens=out_tok,
        planner_tokens_used=tot_tok,
        planner_cost_usd=cost_usd,
    )


def run_b4_sag_live_kev4b_plus_qsp_v2(query: str, case_id: str) -> PreRetrieveDecisionOutput:
    """B4: Full Production SAG Pre-Retrieve (Live SiliconFlow Kev-4b Decision Router + QueryAnalysis + qsp-v2).

    Mirrors sag_api/api/v1/search.py::_build_query_route and sag_api/services/decision_router.py::_route_from_answers.
    """
    t0 = time.perf_counter_ns()
    live_entry = _LIVE_KEV4B_CACHE.get(case_id)
    if live_entry is None:
        raise RuntimeError(f"Missing live SiliconFlow Kev-4b cache entry for {case_id}")

    answers = live_entry.get("answers") or {}
    usage = live_entry.get("usage") or {}
    in_tok = int(usage.get("input_tokens", 0) or 0)
    out_tok = int(usage.get("output_tokens", 0) or 0)
    tot_tok = in_tok + out_tok
    cost_usd = (tot_tok * SILICONFLOW_KEV4B_PRICE_PER_1M_USD) / 1_000_000.0
    http_latency_ms = float(live_entry.get("latency_ms", 0.0) or 0.0)

    decision = _route_from_answers(
        query,
        answers,
        str(live_entry.get("model") or settings.decision_model),
        http_latency_ms,
        "siliconflow",
    )
    analysis = analyze_query(query, segmentation_enabled=False)
    features: QueryFeatures = analysis.features
    local_ms = (time.perf_counter_ns() - t0) / 1_000_000.0
    total_latency_ms = round(http_latency_ms + local_ms, 2)

    if not decision.get("need_retrieval", True) or _is_production_direct_chitchat(query):
        return PreRetrieveDecisionOutput(
            strategy_name="B4_sag_live_kev4b_plus_qsp_v2",
            case_id=case_id,
            need_retrieval=False,
            suggested_strategy=str(decision.get("suggested_strategy") or "vector"),
            answer_shape="chit_chat",
            target_unit="NONE",
            selection_mode="NONE",
            output_mode="ANSWER",
            cardinality_mode="ONE",
            count_source="DEFAULT",
            effective_top_k=0,
            initial_doc_admission=0,
            max_doc_capacity=0,
            first_wave_candidates=0,
            per_document_limit=None,
            order_mode="RELEVANCE",
            decomposition_mode="NONE",
            subquery_count=0,
            multi_hop_detected=False,
            exact_identifiers_extracted=0,
            memory_scope="none",
            temporal_mode="atemporal",
            latency_ms=total_latency_ms,
            decision_input_tokens=in_tok,
            decision_output_tokens=out_tok,
            planner_tokens_used=tot_tok,
            planner_cost_usd=cost_usd,
        )

    strat_plan: QueryStrategyPlan = plan_query(
        query,
        features=features,
        answer_shape=str(decision.get("answer_shape") or "") or None,
    )
    rplan = strat_plan.retrieval_plan
    subq_count = max(1, len(rplan.decomposition.subqueries))
    initial_doc_admission, max_doc_capacity = _compute_sag_doc_bounds(
        rplan, features=features, subquery_count=subq_count
    )
    exact_id_count = (
        len(features.exact_terms) + len(features.identifier_terms) + len(features.path_terms)
    )

    return PreRetrieveDecisionOutput(
        strategy_name="B4_sag_live_kev4b_plus_qsp_v2",
        case_id=case_id,
        need_retrieval=True,
        suggested_strategy=str(decision.get("suggested_strategy") or "multi"),
        answer_shape=str(decision.get("answer_shape") or "fact_answer"),
        target_unit=rplan.target.value,
        selection_mode=rplan.selection.value,
        output_mode=rplan.output.value,
        cardinality_mode=rplan.cardinality.mode.value,
        count_source=rplan.cardinality.count_source.value,
        effective_top_k=rplan.cardinality.effective_n,
        initial_doc_admission=initial_doc_admission,
        max_doc_capacity=max_doc_capacity,
        first_wave_candidates=rplan.cardinality.effective_n * 4,
        per_document_limit=rplan.per_document_limit,
        order_mode=rplan.order.value,
        decomposition_mode=rplan.decomposition.mode.value,
        subquery_count=subq_count,
        multi_hop_detected=bool(features.multi_hop or rplan.output == OutputMode.COMPARE),
        exact_identifiers_extracted=exact_id_count,
        memory_scope=str(decision.get("memory_scope") or "project_documents"),
        temporal_mode=str(decision.get("temporal_mode") or "atemporal"),
        latency_ms=total_latency_ms,
        decision_input_tokens=in_tok,
        decision_output_tokens=out_tok,
        planner_tokens_used=tot_tok,
        planner_cost_usd=cost_usd,
    )


# ---------------------------------------------------------------------------
# 2. Benchmark Dataset Loaders (4 Suites = 275 Queries)
# ---------------------------------------------------------------------------
def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def load_enterpriserag_bench_v0() -> list[IsolatedQueryCase]:
    """Load all 50 questions from RetrievalCI Bench-v0 (single_hop, multi_hop, contradiction, unanswerable)."""
    q_path = BENCH_V0_ROOT / "examples" / "rag_eval" / "bench_v0" / "questions.jsonl"
    questions = _read_jsonl(q_path)

    cases: list[IsolatedQueryCase] = []
    for q_row in questions:
        q = q_row["question"]
        tier = q_row.get("tier", "single_hop")
        gold_docs = len(set(q_row.get("ground_truth_citations") or []))
        feats = extract_query_features(q)
        cases.append(
            IsolatedQueryCase(
                case_id=q_row["id"],
                suite="EnterpriseRAG_Bench_v0",
                category=tier,
                query=q,
                gold_doc_count=gold_docs,
                expected_need_retrieval=True,
                expected_multi_hop=(tier == "multi_hop"),
                expected_has_identifiers=bool(
                    feats.exact_terms or feats.identifier_terms or feats.path_terms
                ),
            )
        )
    return cases


def load_vn_mteb_bench() -> list[IsolatedQueryCase]:
    """Load all 50 Vietnamese questions from VN-MTEB RAG Bench 2026 (Zalo Legal + HotpotQA-VN)."""
    path = VN_MTEB_ROOT / "data" / "questions.jsonl"
    rows = _read_jsonl(path)
    cases: list[IsolatedQueryCase] = []
    for r in rows:
        q = r["question"]
        tier = r.get("tier", "single_hop_legal")
        gold_docs = len(set(r.get("relevant_doc_ids") or []))
        feats = extract_query_features(q)
        cases.append(
            IsolatedQueryCase(
                case_id=r["question_id"],
                suite="VN_MTEB_2026",
                category=tier,
                query=q,
                gold_doc_count=gold_docs,
                expected_need_retrieval=True,
                expected_multi_hop=(tier == "multi_hop"),
                expected_has_identifiers=bool(
                    feats.exact_terms or feats.identifier_terms or feats.path_terms
                ),
            )
        )
    return cases


def load_enterprise_multi_org_bench() -> list[IsolatedQueryCase]:
    """Load knowledge/workspace benchmark questions across Org2 Nova, Org3 CloudOps, Org4 MediFlow."""
    org_dirs = (
        ("Org2_Nova", DATASET_ROOT / "Organization2-Nova-Solutions" / "evaluation" / "benchmark_cases.jsonl"),
        ("Org3_CloudOps", DATASET_ROOT / "Organization3-CloudOps-Services" / "evaluation" / "benchmark_cases.jsonl"),
        ("Org4_MediFlow", DATASET_ROOT / "Organization4-MediFlow" / "evaluation" / "benchmark_cases.jsonl"),
    )
    cases: list[IsolatedQueryCase] = []
    for org_name, path in org_dirs:
        for r in _read_jsonl(path):
            if r.get("answer_channel") not in {"knowledge", "workspace"}:
                continue
            q = r["question"]
            cat = r.get("case_category", "general")
            gold_docs = len(set(r.get("source_ids") or []))
            feats = extract_query_features(q)
            cases.append(
                IsolatedQueryCase(
                    case_id=r["case_id"],
                    suite="Enterprise_MultiOrg",
                    category=f"{org_name}:{cat}",
                    query=q,
                    gold_doc_count=max(1, gold_docs),
                    expected_need_retrieval=True,
                    expected_multi_hop=bool(feats.multi_hop),
                    expected_has_identifiers=bool(
                        feats.exact_terms or feats.identifier_terms or feats.path_terms
                    ),
                )
            )
    return cases


def build_crag_seven_axis_stress_suite() -> list[IsolatedQueryCase]:
    """Build 25 canonical queries covering all 7 question shapes & routing axes (CRAG / qsp-v2)."""
    return [
        # --- Type 1: Chit-Chat / Greeting (K* = 0, need_retrieval = False) ---
        IsolatedQueryCase(
            case_id="axis_chat_01",
            suite="CRAG_7Axis_Stress",
            category="chit_chat",
            query="Xin chào bạn!",
            gold_doc_count=0,
            expected_need_retrieval=False,
            expected_target="NONE",
            expected_output="ANSWER",
            expected_effective_n=0,
            expected_memory_scope="none",
            expected_temporal_mode="atemporal",
        ),
        IsolatedQueryCase(
            case_id="axis_chat_02",
            suite="CRAG_7Axis_Stress",
            category="chit_chat",
            query="Hello",
            gold_doc_count=0,
            expected_need_retrieval=False,
            expected_target="NONE",
            expected_output="ANSWER",
            expected_effective_n=0,
            expected_memory_scope="none",
            expected_temporal_mode="atemporal",
        ),
        IsolatedQueryCase(
            case_id="axis_chat_03",
            suite="CRAG_7Axis_Stress",
            category="chit_chat",
            query="Cảm ơn bạn!",
            gold_doc_count=0,
            expected_need_retrieval=False,
            expected_target="NONE",
            expected_output="ANSWER",
            expected_effective_n=0,
            expected_memory_scope="none",
            expected_temporal_mode="atemporal",
        ),
        IsolatedQueryCase(
            case_id="axis_chat_04",
            suite="CRAG_7Axis_Stress",
            category="chit_chat",
            query="Bạn là ai?",
            gold_doc_count=0,
            expected_need_retrieval=False,
            expected_target="NONE",
            expected_output="ANSWER",
            expected_effective_n=0,
            expected_memory_scope="none",
            expected_temporal_mode="atemporal",
        ),
        # --- Type 2: Fact Answer (PASSAGE + ANSWER, default effective_n = 5, initial_doc_admission = 2) ---
        IsolatedQueryCase(
            case_id="axis_fact_01",
            suite="CRAG_7Axis_Stress",
            category="fact_answer",
            query="When must an evidence claim be rejected?",
            gold_doc_count=1,
            expected_target="PASSAGE",
            expected_output="ANSWER",
            expected_effective_n=5,
            expected_per_doc_limit=None,
            expected_order="RELEVANCE",
            expected_decomposition="NONE",
        ),
        IsolatedQueryCase(
            case_id="axis_fact_02",
            suite="CRAG_7Axis_Stress",
            category="fact_answer",
            query="Thời hạn hiệu lực mặc định của tài khoản nhà thầu trong quy định DOC-SEC-001 là bao lâu?",
            gold_doc_count=1,
            expected_has_identifiers=True,
            expected_target="PASSAGE",
            expected_output="ANSWER",
            expected_effective_n=5,
            expected_per_doc_limit=None,
        ),
        IsolatedQueryCase(
            case_id="axis_fact_03",
            suite="CRAG_7Axis_Stress",
            category="fact_answer",
            query="Show 12 passages about memory leak sanitization",
            gold_doc_count=3,
            expected_target="PASSAGE",
            expected_output="LIST",
            expected_effective_n=12,
            expected_per_doc_limit=None,
        ),
        # --- Type 3: Document List (DOCUMENT + LIST, explicit k or ALL, per_doc_limit = 1) ---
        IsolatedQueryCase(
            case_id="axis_list_01",
            suite="CRAG_7Axis_Stress",
            category="document_list",
            query="Hãy liệt kê 20 file liên quan đến chính sách bảo mật",
            gold_doc_count=20,
            expected_target="DOCUMENT",
            expected_output="LIST",
            expected_effective_n=20,
            expected_per_doc_limit=1,
        ),
        IsolatedQueryCase(
            case_id="axis_list_02",
            suite="CRAG_7Axis_Stress",
            category="document_list",
            query="Find top 15 documents about disaster recovery",
            gold_doc_count=15,
            expected_target="DOCUMENT",
            expected_output="LIST",
            expected_effective_n=15,
            expected_per_doc_limit=1,
        ),
        IsolatedQueryCase(
            case_id="axis_list_03",
            suite="CRAG_7Axis_Stress",
            category="document_list",
            query="Liệt kê tất cả các tài liệu quy định về vận hành hệ thống",
            gold_doc_count=35,
            expected_target="DOCUMENT",
            expected_output="LIST",
            expected_effective_n=50,
            expected_per_doc_limit=1,
        ),
        IsolatedQueryCase(
            case_id="axis_list_04",
            suite="CRAG_7Axis_Stress",
            category="document_list",
            query="Liệt kê 500 file liên quan đến thanh toán",
            gold_doc_count=50,
            expected_target="DOCUMENT",
            expected_output="LIST",
            expected_effective_n=50,
            expected_per_doc_limit=1,
        ),
        IsolatedQueryCase(
            case_id="axis_list_05",
            suite="CRAG_7Axis_Stress",
            category="document_list",
            query="Mở 20 file tài liệu về kiến trúc hệ thống",
            gold_doc_count=20,
            expected_target="DOCUMENT",
            expected_output="OPEN",
            expected_effective_n=20,
            expected_per_doc_limit=1,
        ),
        # --- Type 4: Open Single Document (DOCUMENT + OPEN, effective_n = 1, per_doc_limit = 1) ---
        IsolatedQueryCase(
            case_id="axis_open_01",
            suite="CRAG_7Axis_Stress",
            category="open_document",
            query="Mở tài liệu hướng dẫn vận hành",
            gold_doc_count=1,
            expected_target="DOCUMENT",
            expected_output="OPEN",
            expected_effective_n=1,
            expected_per_doc_limit=1,
        ),
        IsolatedQueryCase(
            case_id="axis_open_02",
            suite="CRAG_7Axis_Stress",
            category="open_document",
            query="Please open document runbook for EU failover",
            gold_doc_count=1,
            expected_target="DOCUMENT",
            expected_output="OPEN",
            expected_effective_n=1,
            expected_per_doc_limit=1,
        ),
        # --- Type 5: Exhaustive Count (DOCUMENT + COUNT, effective_n = 50, per_doc_limit = 1) ---
        IsolatedQueryCase(
            case_id="axis_count_01",
            suite="CRAG_7Axis_Stress",
            category="exhaustive_count",
            query="Có bao nhiêu tài liệu quy định về phân vùng bảo mật?",
            gold_doc_count=25,
            expected_target="DOCUMENT",
            expected_output="COUNT",
            expected_effective_n=50,
            expected_per_doc_limit=1,
        ),
        IsolatedQueryCase(
            case_id="axis_count_02",
            suite="CRAG_7Axis_Stress",
            category="exhaustive_count",
            query="How many policy documents cover encryption key rotation?",
            gold_doc_count=18,
            expected_target="DOCUMENT",
            expected_output="COUNT",
            expected_effective_n=50,
            expected_per_doc_limit=1,
        ),
        # --- Type 6: Summarize Set (DOCUMENT/TOPIC + SUMMARIZE, effective_n = 10, per_doc_limit = 1) ---
        IsolatedQueryCase(
            case_id="axis_sum_01",
            suite="CRAG_7Axis_Stress",
            category="summarize_set",
            query="Tóm tắt tất cả các tài liệu trong dự án",
            gold_doc_count=10,
            expected_target="DOCUMENT",
            expected_output="SUMMARIZE",
            expected_effective_n=10,
            expected_per_doc_limit=1,
        ),
        IsolatedQueryCase(
            case_id="axis_sum_02",
            suite="CRAG_7Axis_Stress",
            category="summarize_set",
            query="Summarize all reports on regional latency incidents",
            gold_doc_count=10,
            expected_target="DOCUMENT",
            expected_output="SUMMARIZE",
            expected_effective_n=10,
            expected_per_doc_limit=1,
        ),
        # --- Type 7: Multi-Facet Compare & Multi-Clause Decomposition ---
        IsolatedQueryCase(
            case_id="axis_cmp_01",
            suite="CRAG_7Axis_Stress",
            category="multi_facet_compare",
            query="So sánh cơ chế phân quyền giữa phiên bản v1 và v2",
            gold_doc_count=4,
            expected_multi_hop=True,
            expected_target="PASSAGE",
            expected_output="COMPARE",
            expected_effective_n=8,
            expected_per_doc_limit=None,
        ),
        IsolatedQueryCase(
            case_id="axis_cmp_02",
            suite="CRAG_7Axis_Stress",
            category="multi_facet_compare",
            query="What is the difference between ADR-007 in-memory DEK caching and the Key Management Standard?",
            gold_doc_count=4,
            expected_multi_hop=True,
            expected_has_identifiers=True,
            expected_target="PASSAGE",
            expected_output="COMPARE",
            expected_effective_n=8,
            expected_per_doc_limit=None,
        ),
        IsolatedQueryCase(
            case_id="axis_decomp_01",
            suite="CRAG_7Axis_Stress",
            category="parallel_decomposition",
            query="Liệt kê 10 tài liệu mới nhất về bảo mật, và ai là người phê duyệt chính sách?",
            gold_doc_count=10,
            expected_multi_hop=True,
            expected_target="DOCUMENT",
            expected_output="LIST",
            expected_effective_n=10,
            expected_per_doc_limit=1,
            expected_order="TIME_DESC",
            expected_decomposition="PARALLEL",
        ),
        IsolatedQueryCase(
            case_id="axis_decomp_02",
            suite="CRAG_7Axis_Stress",
            category="parallel_decomposition",
            query="What caused the EU-West activation funnel drop in January, and which PR fixed the event emission bug?",
            gold_doc_count=3,
            expected_multi_hop=True,
            expected_target="PASSAGE",
            expected_output="ANSWER",
            expected_effective_n=5,
            expected_decomposition="PARALLEL",
        ),
        # --- Temporal & Session Memory Routing Axes (ECCE / Zero-Mem) ---
        IsolatedQueryCase(
            case_id="axis_ecce_01",
            suite="CRAG_7Axis_Stress",
            category="session_lineage",
            query="Vì sao chúng ta chuyển từ MongoDB sang PostgreSQL trong buổi họp trước?",
            gold_doc_count=2,
            expected_memory_scope="session_history",
            expected_temporal_mode="change_lineage",
        ),
        IsolatedQueryCase(
            case_id="axis_ecce_02",
            suite="CRAG_7Axis_Stress",
            category="session_effective",
            query="Quyết định hiện tại của chúng ta về database chính và đối chiếu với tài liệu kiến trúc là gì?",
            gold_doc_count=2,
            expected_memory_scope="hybrid_both",
            expected_temporal_mode="current_effective",
        ),
        IsolatedQueryCase(
            case_id="axis_ecce_03",
            suite="CRAG_7Axis_Stress",
            category="session_full_audit",
            query="Tổng hợp tất cả các quyết định và công việc từ đầu cuộc trò chuyện đến nay",
            gold_doc_count=8,
            expected_memory_scope="full_session_audit",
        ),
    ]


# ---------------------------------------------------------------------------
# 3. Evaluation Metrics Calculator (Adaptive-RAG + RouterBench + CRAG)
# ---------------------------------------------------------------------------
def evaluate_strategy_on_cases(
    runner_fn,
    cases: list[IsolatedQueryCase],
) -> dict[str, Any]:
    outputs: list[PreRetrieveDecisionOutput] = [runner_fn(c.query, c.case_id) for c in cases]
    by_id = {c.case_id: c for c in cases}

    # 1. Need-Retrieval / Chit-Chat Gate Accuracy
    gate_correct = sum(
        1 for out in outputs if out.need_retrieval == by_id[out.case_id].expected_need_retrieval
    )

    # 2. Fast Vector Strategy Routing Rate (vs Heavy Multi-Hop Expansion)
    retrieval_outputs = [out for out in outputs if out.need_retrieval]
    vector_routed = sum(1 for out in retrieval_outputs if out.suggested_strategy == "vector")

    # 3. Budget Sufficiency & Theoretical Recall Ceiling (using max_doc_capacity vs gold_doc_count)
    answerable_all = [
        (by_id[out.case_id], out)
        for out in outputs
        if by_id[out.case_id].expected_need_retrieval and by_id[out.case_id].gold_doc_count >= 1
    ]
    budget_sufficient_count = sum(
        1 for c, out in answerable_all if out.max_doc_capacity >= c.gold_doc_count
    )
    recall_ceilings = [
        min(1.0, out.max_doc_capacity / c.gold_doc_count) for c, out in answerable_all
    ]

    # Multi-doc subset (K* >= 2)
    multi_doc_pairs = [(c, out) for c, out in answerable_all if c.gold_doc_count >= 2]
    multi_doc_sufficient = sum(
        1 for c, out in multi_doc_pairs if out.max_doc_capacity >= c.gold_doc_count
    )
    multi_doc_recall_ceilings = [
        min(1.0, out.max_doc_capacity / c.gold_doc_count) for c, out in multi_doc_pairs
    ]

    # Heavy multi-doc subset (K* >= 6)
    heavy_doc_pairs = [(c, out) for c, out in answerable_all if c.gold_doc_count >= 6]
    heavy_doc_sufficient = sum(
        1 for c, out in heavy_doc_pairs if out.max_doc_capacity >= c.gold_doc_count
    )
    heavy_doc_recall_ceilings = [
        min(1.0, out.max_doc_capacity / c.gold_doc_count) for c, out in heavy_doc_pairs
    ]

    # 4. Single-Hop Precision Ceiling & Over-Fetch Waste (K* == 1, using initial_doc_admission)
    single_doc_pairs = [(c, out) for c, out in answerable_all if c.gold_doc_count == 1]
    single_hop_precision_ceilings = [
        (1.0 / out.initial_doc_admission) if out.initial_doc_admission > 0 else 0.0
        for _, out in single_doc_pairs
    ]
    single_hop_overfetch_docs = [
        max(0, out.initial_doc_admission - 1) for _, out in single_doc_pairs
    ]

    # 5. Multi-Hop Detection / Decomposition Rate on Gold Multi-Hop Queries
    gold_mh_pairs = [
        (by_id[out.case_id], out) for out in outputs if by_id[out.case_id].expected_multi_hop
    ]
    mh_detected = sum(
        1
        for _, out in gold_mh_pairs
        if out.multi_hop_detected or out.subquery_count >= 2 or out.output_mode == "COMPARE"
    )

    # 6. Exact Identifier / Date Extraction Recall
    gold_id_pairs = [
        (by_id[out.case_id], out) for out in outputs if by_id[out.case_id].expected_has_identifiers
    ]
    id_extracted = sum(1 for _, out in gold_id_pairs if out.exact_identifiers_extracted >= 1)

    # 7. 7-Axis Spec Exact Match Rate (on CRAG_7Axis_Stress cases)
    axis_cases = [
        (by_id[out.case_id], out)
        for out in outputs
        if by_id[out.case_id].expected_target is not None
        or by_id[out.case_id].expected_memory_scope is not None
    ]
    axis_matches = 0
    for c, out in axis_cases:
        ok = True
        if c.expected_target is not None and out.target_unit != c.expected_target:
            ok = False
        if c.expected_output is not None and out.output_mode != c.expected_output:
            ok = False
        if c.expected_effective_n is not None and out.effective_top_k != c.expected_effective_n:
            ok = False
        if c.expected_per_doc_limit is not None and out.per_document_limit != c.expected_per_doc_limit:
            ok = False
        if c.expected_order is not None and out.order_mode != c.expected_order:
            ok = False
        if c.expected_decomposition is not None and out.decomposition_mode != c.expected_decomposition:
            ok = False
        if c.expected_memory_scope is not None and out.memory_scope != c.expected_memory_scope:
            ok = False
        if c.expected_temporal_mode is not None and out.temporal_mode != c.expected_temporal_mode:
            ok = False
        if ok:
            axis_matches += 1

    # 8. Real Latency, Token Usage & Cost
    latencies = [out.latency_ms for out in outputs]
    total_in_tokens = sum(out.decision_input_tokens for out in outputs)
    total_out_tokens = sum(out.decision_output_tokens for out in outputs)
    total_planner_tokens = sum(out.planner_tokens_used for out in outputs)
    total_planner_cost = sum(out.planner_cost_usd for out in outputs)
    wasted_doc_slots_per_query = statistics.fmean(
        [
            max(0, out.initial_doc_admission - by_id[out.case_id].gold_doc_count)
            for out in outputs
            if by_id[out.case_id].gold_doc_count <= 1
        ]
    )

    return {
        "strategy": outputs[0].strategy_name if outputs else "",
        "total_queries": len(outputs),
        "gate_accuracy_pct": round(100.0 * gate_correct / len(outputs), 2) if outputs else 0.0,
        "fast_vector_strategy_pct": (
            round(100.0 * vector_routed / len(retrieval_outputs), 2)
            if retrieval_outputs
            else 0.0
        ),
        "seven_axis_exact_match_pct": (
            round(100.0 * axis_matches / len(axis_cases), 2) if axis_cases else None
        ),
        "overall_budget_sufficiency_pct": (
            round(100.0 * budget_sufficient_count / len(answerable_all), 2)
            if answerable_all
            else 0.0
        ),
        "overall_recall_ceiling_pct": (
            round(100.0 * statistics.fmean(recall_ceilings), 2) if recall_ceilings else 0.0
        ),
        "multi_doc_budget_sufficiency_pct": (
            round(100.0 * multi_doc_sufficient / len(multi_doc_pairs), 2)
            if multi_doc_pairs
            else 0.0
        ),
        "multi_doc_recall_ceiling_pct": (
            round(100.0 * statistics.fmean(multi_doc_recall_ceilings), 2)
            if multi_doc_recall_ceilings
            else 0.0
        ),
        "heavy_doc_k6plus_sufficiency_pct": (
            round(100.0 * heavy_doc_sufficient / len(heavy_doc_pairs), 2)
            if heavy_doc_pairs
            else None
        ),
        "heavy_doc_k6plus_recall_ceiling_pct": (
            round(100.0 * statistics.fmean(heavy_doc_recall_ceilings), 2)
            if heavy_doc_recall_ceilings
            else None
        ),
        "single_hop_precision_ceiling_pct": (
            round(100.0 * statistics.fmean(single_hop_precision_ceilings), 2)
            if single_hop_precision_ceilings
            else 0.0
        ),
        "single_hop_avg_overfetch_docs": (
            round(statistics.fmean(single_hop_overfetch_docs), 2)
            if single_hop_overfetch_docs
            else 0.0
        ),
        "wasted_context_tokens_per_simple_query": round(
            wasted_doc_slots_per_query * AVG_TOKENS_PER_RETRIEVED_SLOT, 1
        ),
        "multi_hop_signal_detection_pct": (
            round(100.0 * mh_detected / len(gold_mh_pairs), 2) if gold_mh_pairs else None
        ),
        "identifier_anchor_extraction_pct": (
            round(100.0 * id_extracted / len(gold_id_pairs), 2) if gold_id_pairs else None
        ),
        "latency_p50_ms": round(statistics.median(latencies), 4) if latencies else 0.0,
        "latency_p95_ms": (
            round(sorted(latencies)[min(len(latencies) - 1, int(0.95 * len(latencies)))], 4)
            if latencies
            else 0.0
        ),
        "decision_input_tokens_per_query": round(total_in_tokens / len(outputs), 1) if outputs else 0.0,
        "decision_output_tokens_per_query": round(total_out_tokens / len(outputs), 1) if outputs else 0.0,
        "planner_tokens_per_query": round(total_planner_tokens / len(outputs), 1) if outputs else 0.0,
        "total_tokens_275_queries": total_planner_tokens,
        "planner_cost_per_10k_queries_usd": (
            round((total_planner_cost / len(outputs)) * 10_000, 4) if outputs else 0.0
        ),
    }


def run_isolated_pre_retrieve_benchmark(*, refresh_live: bool = False) -> dict[str, Any]:
    suite_map: dict[str, list[IsolatedQueryCase]] = {
        "EnterpriseRAG_Bench_v0": load_enterpriserag_bench_v0(),
        "VN_MTEB_2026": load_vn_mteb_bench(),
        "Enterprise_MultiOrg": load_enterprise_multi_org_bench(),
        "CRAG_7Axis_Stress": build_crag_seven_axis_stress_suite(),
    }
    all_cases: list[IsolatedQueryCase] = [c for cases in suite_map.values() for c in cases]
    ensure_live_kev4b_cache(all_cases, refresh_live=refresh_live)

    strategies = (
        ("B0_vanilla_fixed_k5", run_b0_vanilla_fixed_k5),
        ("B1_static_wide_k10", run_b1_static_wide_k10),
        ("B2_local_regex_qsp_v2", run_b2_local_regex_qsp_v2),
        ("B3_live_kev4b_only", run_b3_live_kev4b_only),
        ("B4_sag_live_kev4b_plus_qsp_v2", run_b4_sag_live_kev4b_plus_qsp_v2),
    )

    overall_summary: dict[str, Any] = {}
    by_suite_summary: dict[str, dict[str, Any]] = {}

    for strat_name, fn in strategies:
        overall_summary[strat_name] = evaluate_strategy_on_cases(fn, all_cases)

    for suite_name, suite_cases in suite_map.items():
        by_suite_summary[suite_name] = {
            "query_count": len(suite_cases),
            "strategies": {
                strat_name: evaluate_strategy_on_cases(fn, suite_cases)
                for strat_name, fn in strategies
            },
        }

    report = {
        "benchmark": "isolated_pre_retrieve_ablation_v2_live_kev4b",
        "protocol_references": [
            "Adaptive-RAG (NAACL 2024, arXiv:2403.14403) — Question Complexity & Budget Allocation",
            "RouterBench (ICLR / arXiv:2403.12031) — Routing Accuracy vs Cost/Latency Trade-off",
            "Meta CRAG (KDD Cup 2024, arXiv:2406.04744) — 7-Axis Question Shape & Temporal Routing",
            "EnterpriseRAG-Bench (RetrievalCI Bench-v0) & VN-MTEB RAG Bench 2026",
            "Live SiliconFlow SystemOne API (/v1/systemone, model=Kev-4b) — 275 Real HTTP Calls",
        ],
        "total_queries_evaluated": len(all_cases),
        "suites": {k: len(v) for k, v in suite_map.items()},
        "overall": overall_summary,
        "by_suite": by_suite_summary,
    }

    out_path = DATASET_ROOT / "reports" / "isolated-pre-retrieve-benchmark.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--refresh-live",
        action="store_true",
        help="Re-run all 275 HTTP requests against live SiliconFlow /v1/systemone (Kev-4b)",
    )
    args = parser.parse_args()
    result = run_isolated_pre_retrieve_benchmark(refresh_live=args.refresh_live)
    print(json.dumps(result["overall"], ensure_ascii=False, indent=2))
