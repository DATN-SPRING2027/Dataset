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
import asyncio
import concurrent.futures
import json
import re
import statistics
import subprocess
import sys
import time
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

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
    _degraded_decision,
    route_query_async,
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

_FULL_AUDIT_RE = re.compile(
    r"(?i)(?:(?:tổng\s+hợp|liệt\s+kê|điểm\s+lại|tóm\s+tắt|rút\s+ra)\s+(?:tất\s+cả|toàn\s+bộ|mọi)"
    r".*(?:từ\s+đầu|cuộc\s+trò\s+chuyện|buổi\s+chat|phiên|quyết\s+định|công\s+việc)"
    r"|(?:summarize|list|compile)\s+(?:all|every).*(?:from\s+the\s+start|entire\s+session|entire\s+conversation|decisions))"
)
_SESSION_CUE_RE = re.compile(
    r"(?i)(?:\b(?:chúng\s+ta|chúng\s+mình|tụi\s+mình|mình\s+vừa|mình\s+đã|vừa\s+bàn|lúc\s+nãy|lúc\s+đầu|ban\s+đầu|"
    r"buổi\s+họp|phiên\s+trước|cuộc\s+chat|chốt|thống\s+nhất|phương\s+án\s+(?:nào|đó|trên|mới|cũ)|"
    r"tiếp\s+tục\s+công\s+việc|ai\s+(?:nhận|phụ\s+trách|làm|đảm\s+nhiệm)|anh\s+\w+|chị\s+\w+|"
    r"we\s+(?:agreed|discussed|chose|decided)|earlier\s+in\s+chat|our\s+decision|"
    r"continue\s+(?:yesterday|where\s+we\s+left))\b)"
)
_DOC_CUE_RE = re.compile(
    r"(?i)(?:\b(?:tài\s+liệu|quy\s+định|quy\s+chuẩn|chính\s+sách|hợp\s+đồng|báo\s+cáo|biên\s+bản|"
    r"điều\s+\d+|khoản\s+\d+|mục\s+\d+|adr[-_ ]?\d+|rfc[-_ ]?\d+|spec|specification|policy|document|contract)\b)"
)
_LINEAGE_CUE_RE = re.compile(
    r"(?i)(?:(?:vì\s+sao|tại\s+sao|lý\s+do\s+(?:gì|nào)).*(?:chuyển|đổi|bỏ|thay|quay\s+lại)"
    r"|(?:chuyển\s+từ|đổi\s+từ|thay\s+đổi\s+từ).*(?:sang|qua)"
    r"|(?:lịch\s+sử\s+thay\s+đổi|quá\s+trình\s+thay\s+đổi|why\s+did\s+we\s+(?:switch|change|drop|revert)|"
    r"switched\s+from\s+.+\s+to))"
)
_TEMPORAL_TARGET_RE = re.compile(
    r"(?i)(?:\b(?:khi\s+nào|vào\s+ngày\s+nào|ngày\s+nào|ngày\s+mấy|lúc\s+mấy\s+giờ|bao\s+lâu|trước\s+hay\s+sau|"
    r"thứ\s+tự\s+thời\s+gian|when\s+did|what\s+date|how\s+long|before\s+or\s+after)\b)"
)
_EFFECTIVE_STATE_RE = re.compile(
    r"(?i)(?:\b(?:chốt|quyết\s+định\s+(?:cuối|hiện\s+tại|hiện\s+hành|chọn)|cuối\s+cùng\s+(?:chọn|dùng)|"
    r"đang\s+dùng|hiện\s+tại|hiện\s+giờ|ai\s+(?:nhận|phụ\s+trách|đảm\s+nhiệm)|còn\s+lỗi\s+nào|"
    r"việc\s+gì\s+đang\s+dở|tiếp\s+tục\s+công\s+việc|which\s+\w+\s+did\s+we\s+(?:choose|pick|select)|"
    r"current\s+(?:decision|status|owner)|final\s+decision|who\s+(?:owns|is\s+responsible|took))\b)"
)
_PAST_ANCHOR_RE = re.compile(
    r"(?i)(?:\b(?:hôm\s+qua|tuần\s+trước|tháng\s+trước|buổi\s+họp\s+trước|đầu\s+phiên|đầu\s+buổi|"
    r"yesterday|last\s+week|last\s+meeting|earlier\s+session)\b)"
)

_DOC_UNIT_WORDS = (
    r"file|files|tệp|tập\s+tin|tài\s+liệu|văn\s+bản|hồ\s+sơ|báo\s+cáo|"
    r"chính\s+sách|quy\s+định|quy\s+trình|hợp\s+đồng|biên\s+bản|"
    r"document|documents|doc|docs|report|reports|policy|policies|contract|contracts|paper|papers|runbook|runbooks|spec|specs"
)
_TOPIC_UNIT_WORDS = r"chủ\s+đề|vấn\s+đề\s+chính|nhóm\s+chủ\s+đề|topic|topics|theme|themes"
_PASSAGE_UNIT_WORDS = (
    r"đoạn|mục|phần|kết\s+quả|bằng\s+chứng|trích\s+đoạn|"
    r"passage|passages|section|sections|chunk|chunks|result|results|snippet|snippets"
)
_EXPLICIT_DOC_COUNT_RE = re.compile(
    rf"(?i)(?:(?:\b(?:top|mở|liệt\s+kê|tìm|lấy|hiển\s+thị|cho\s+tôi|xem|list|show|open|find|get|give\s+me|return)\s+(?:ra\s+|cho\s+tôi\s+)?(\d{{1,3}})\s+(?:các\s+|những\s+)?(?:{_DOC_UNIT_WORDS})\b)"
    rf"|(?:\b(\d{{1,3}})\s+(?:{_DOC_UNIT_WORDS})\s+(?:liên\s+quan|gần\s+nhất|mới\s+nhất|đầu\s+tiên|quan\s+trọng|chính|khác\s+nhau|relevant|related|recent|latest|top|matching|distinct)\b)"
    rf"|(?:\b(?:mở|liệt\s+kê|tìm|lấy|xem|list|show|open|find|get)\s+(?:đến\s+|tới\s+|khoảng\s+|tối\s+đa\s+|up\s+to\s+)?(\d{{1,3}})\s+(?:{_DOC_UNIT_WORDS})\b))"
)
_EXPLICIT_TOPIC_COUNT_RE = re.compile(
    rf"(?i)\b(?:top|liệt\s+kê|tìm|lấy|cho\s+biết|list|show|find|get|identify)?\s*(\d{{1,3}})\s+(?:{_TOPIC_UNIT_WORDS})\b"
)
_EXPLICIT_PASSAGE_COUNT_RE = re.compile(
    rf"(?i)\b(?:top|liệt\s+kê|tìm|lấy|hiển\s+thị|list|show|find|get|return)\s+(\d{{1,3}})\s+(?:{_PASSAGE_UNIT_WORDS})\b"
)
_DOC_COUNT_QUESTION_RE = re.compile(
    rf"(?i)(?:\b(?:có\s+bao\s+nhiêu|tổng\s+số|đếm\s+số(?:\s+lượng)?|số\s+lượng)\s+(?:các\s+|những\s+)?(?:{_DOC_UNIT_WORDS})\b"
    rf"|\bhow\s+many\s+(?:[a-z_-]+\s+){{0,2}}(?:{_DOC_UNIT_WORDS})\b)"
)
_DOC_ALL_RE = re.compile(
    rf"(?i)(?:\b(?:tất\s+cả|toàn\s+bộ|mọi)\s+(?:các\s+|những\s+)?(?:{_DOC_UNIT_WORDS})\b"
    rf"|\b(?:all|every)\s+(?:the\s+)?(?:[a-z_-]+\s+){{0,2}}(?:{_DOC_UNIT_WORDS})\b)"
)
_DOC_LIST_RE = re.compile(
    rf"(?i)(?:\b(?:liệt\s+kê|danh\s+sách|kể\s+tên|cho\s+biết\s+các)\b.*\b(?:{_DOC_UNIT_WORDS})\b"
    rf"|\b(?:những|các)\s+(?:{_DOC_UNIT_WORDS})(?:\s+[^\W\d_][\w-]*){{0,3}}\s+nào\b"
    rf"|(?<!theo\s)(?<!trong\s)\b(?:hiện\s+có|gồm(?:\s+có)?|bao\s+gồm|có)\s+(?:những\s+|các\s+)?(?:{_DOC_UNIT_WORDS})(?:\s+[^\W\d_][\w-]*){{0,3}}\s+nào\b"
    rf"|\b(?:liệt\s+kê|danh\s+sách|list|show\s+all|what\s+are\s+the|which)\s+(?:các\s+|những\s+|the\s+)?(?:[^\W\d_][\w-]*\s+){{0,2}}(?:{_DOC_UNIT_WORDS})\b)",
    re.UNICODE,
)
_DOC_OPEN_RE = re.compile(
    rf"(?i)^\s*(?:hãy\s+|vui\s+lòng\s+|please\s+)?(?:mở|xem\s+nội\s+dung|hiển\s+thị\s+toàn\s+bộ|open|view)\s+(?:{_DOC_UNIT_WORDS})\b"
)
_DOC_SUMMARIZE_RE = re.compile(
    rf"(?i)\b(?:tóm\s+tắt|tổng\s+hợp|summarize|summary\s+of)\s+(?:tất\s+cả\s+|toàn\s+bộ\s+|mọi\s+|all\s+|every\s+)?(?:các\s+|những\s+|the\s+)?(?:{_DOC_UNIT_WORDS})\b"
)
_COMPARE_RE = re.compile(
    r"(?i)\b(?:so\s+sánh|khác\s+nhau\s+giữa|khác\s+gì\s+giữa|điểm\s+khác\s+biệt\s+giữa|compare|comparison\s+between|difference\s+between|differences\s+between|versus|vs\.?)\b"
)
_TIME_DESC_RE = re.compile(
    r"(?i)\b(?:mới\s+nhất|gần\s+đây\s+nhất|hiện\s+hành|latest|newest|most\s+recent)\b"
)
_TIME_ASC_RE = re.compile(
    r"(?i)\b(?:cũ\s+nhất|đầu\s+tiên|theo\s+thứ\s+tự\s+thời\s+gian|oldest|earliest|chronological)\b"
)
_PARALLEL_SPLIT_RE = re.compile(
    r"(?i)(?:,\s*(?:và|and)\s+(?=(?:ai|khi\s+nào|ở\s+đâu|bao\s+nhiêu|như\s+thế\s+nào|tại\s+sao|vì\s+sao|gì|nào|which|who|what|when|where|how|why)\b))"
)

_VALID_MEMORY_SCOPES = frozenset(
    {"none", "session_history", "project_documents", "hybrid_both", "full_session_audit"}
)
_VALID_TEMPORAL_MODES = frozenset({"current_effective", "change_lineage", "past_point", "atemporal"})
_VALID_ANSWER_SHAPES = frozenset(
    {
        "fact_answer",
        "multi_facet_compare",
        "document_list",
        "exhaustive_count",
        "summarize_set",
        "open_document",
    }
)


def _infer_legacy_ecce_routing_signals(query: str, *, coarse_intent: str = "AMBIGUOUS") -> tuple[str, str]:
    cleaned = query.strip()
    if not cleaned or coarse_intent == "CHAT":
        return "none", "atemporal"

    if _FULL_AUDIT_RE.search(cleaned):
        memory_scope = "full_session_audit"
    else:
        has_session = bool(_SESSION_CUE_RE.search(cleaned))
        has_doc = bool(_DOC_CUE_RE.search(cleaned))
        if has_session and has_doc:
            memory_scope = "hybrid_both"
        elif has_session:
            memory_scope = "session_history"
        else:
            memory_scope = "project_documents"

    if _LINEAGE_CUE_RE.search(cleaned):
        temporal_mode = "change_lineage"
    elif _TEMPORAL_TARGET_RE.search(cleaned):
        temporal_mode = "past_point"
    elif _EFFECTIVE_STATE_RE.search(cleaned):
        temporal_mode = "current_effective"
    elif _PAST_ANCHOR_RE.search(cleaned):
        temporal_mode = "past_point"
    else:
        temporal_mode = "atemporal"
    return memory_scope, temporal_mode


def _extract_legacy_query_signals(query: str) -> dict[str, Any]:
    """Extract structured shape/cardinality/order/subquery signals compatible with SAG main's `plan_query`."""
    cleaned = unicodedata.normalize("NFC", query or "").strip()
    order_mode = "relevance"
    if _TIME_DESC_RE.search(cleaned):
        order_mode = "time_desc"
    elif _TIME_ASC_RE.search(cleaned):
        order_mode = "time_asc"

    parts = [p.strip(" ?.,;") for p in _PARALLEL_SPLIT_RE.split(cleaned) if p.strip(" ?.,;")]
    subqueries = tuple(parts) if len(parts) >= 2 else ()

    doc_count_match = _EXPLICIT_DOC_COUNT_RE.search(cleaned)
    if doc_count_match:
        raw_num = next((g for g in doc_count_match.groups() if g is not None), None)
        count_val = int(raw_num) if raw_num is not None else None
        is_open = bool(re.search(r"(?i)\b(?:mở|open)\b", cleaned))
        return {
            "answer_shape": "open_document" if is_open else "document_list",
            "target_unit": "document",
            "explicit_count": count_val,
            "is_catalog_query": False,
            "order_mode": order_mode,
            "subqueries": subqueries,
        }

    topic_count_match = _EXPLICIT_TOPIC_COUNT_RE.search(cleaned)
    if topic_count_match:
        return {
            "answer_shape": "summarize_set",
            "target_unit": "topic",
            "explicit_count": int(topic_count_match.group(1)),
            "is_catalog_query": False,
            "order_mode": order_mode,
            "subqueries": subqueries,
        }

    passage_count_match = _EXPLICIT_PASSAGE_COUNT_RE.search(cleaned)
    if passage_count_match:
        return {
            "answer_shape": "fact_answer",
            "target_unit": "passage",
            "explicit_count": int(passage_count_match.group(1)),
            "is_catalog_query": False,
            "order_mode": order_mode,
            "subqueries": subqueries,
        }

    if _DOC_COUNT_QUESTION_RE.search(cleaned):
        return {
            "answer_shape": "exhaustive_count",
            "target_unit": "document",
            "explicit_count": None,
            "is_catalog_query": True,
            "order_mode": order_mode,
            "subqueries": subqueries,
        }

    if _DOC_SUMMARIZE_RE.search(cleaned):
        return {
            "answer_shape": "summarize_set",
            "target_unit": "document",
            "explicit_count": None,
            "is_catalog_query": bool(_DOC_ALL_RE.search(cleaned)),
            "order_mode": order_mode,
            "subqueries": subqueries,
        }

    if _DOC_ALL_RE.search(cleaned) or _DOC_LIST_RE.search(cleaned):
        return {
            "answer_shape": "document_list",
            "target_unit": "document",
            "explicit_count": None,
            "is_catalog_query": bool(_DOC_ALL_RE.search(cleaned)),
            "order_mode": order_mode,
            "subqueries": subqueries,
        }

    if _DOC_OPEN_RE.search(cleaned):
        return {
            "answer_shape": "open_document",
            "target_unit": "document",
            "explicit_count": 1,
            "is_catalog_query": False,
            "order_mode": order_mode,
            "subqueries": subqueries,
        }

    if _COMPARE_RE.search(cleaned):
        return {
            "answer_shape": "multi_facet_compare",
            "target_unit": "passage",
            "explicit_count": None,
            "is_catalog_query": False,
            "order_mode": order_mode,
            "subqueries": subqueries,
        }

    return {
        "answer_shape": "fact_answer",
        "target_unit": "passage",
        "explicit_count": None,
        "is_catalog_query": False,
        "order_mode": order_mode,
        "subqueries": subqueries,
    }


def _adapt_legacy_systemone_answers(
    query: str,
    answers: dict[str, Any],
    model: str,
    latency_ms: float,
) -> dict[str, Any]:
    """Translate historical `/v1/systemone` multiple-choice cache rows into SAG main's unified router dict."""
    intent_res = answers.get("intent_type") or {}
    intent_choice = str(intent_res.get("choice", "factual_lookup")).strip().lower()
    intent_conf = float(intent_res.get("confidence", 0.5) or 0.0)
    is_chat_intent = intent_choice in {"chit_chat", "chat", "greeting"}
    if is_chat_intent and intent_conf >= CHAT_HIGH_CONFIDENCE:
        coarse_intent = "CHAT"
    elif is_chat_intent or intent_conf < CHAT_HIGH_CONFIDENCE:
        coarse_intent = "AMBIGUOUS"
    else:
        coarse_intent = "KNOWLEDGE"

    if coarse_intent == "CHAT":
        return {
            "query": query,
            "coarse_intent": "CHAT",
            "need_retrieval": False,
            "suggested_strategy": "vector",
            "answer_shape": "chit_chat",
            "memory_scope": "none",
            "temporal_mode": "atemporal",
            "confidence": intent_conf,
            "model": model,
            "latency_ms": latency_ms,
            "degraded": False,
        }

    inferred_scope, inferred_temporal = _infer_legacy_ecce_routing_signals(query, coarse_intent=coarse_intent)
    scope_res = answers.get("memory_scope") or {}
    scope_choice = str(scope_res.get("choice", "")).strip().lower() if isinstance(scope_res, dict) else ""
    memory_scope = (
        scope_choice
        if scope_choice in _VALID_MEMORY_SCOPES and scope_choice != "none"
        else inferred_scope
    )
    if inferred_scope in {"hybrid_both", "full_session_audit"} and memory_scope == "project_documents":
        memory_scope = inferred_scope

    temp_res = answers.get("temporal_mode") or {}
    temp_choice = str(temp_res.get("choice", "")).strip().lower() if isinstance(temp_res, dict) else ""
    temp_conf = float(temp_res.get("confidence", 0.5) or 0.0) if isinstance(temp_res, dict) else 0.0
    if temp_choice in _VALID_TEMPORAL_MODES:
        if temp_conf < 0.70 and inferred_temporal in {"change_lineage", "current_effective"}:
            temporal_mode = inferred_temporal
        else:
            temporal_mode = temp_choice
    else:
        temporal_mode = inferred_temporal

    shape_signals = _extract_legacy_query_signals(query)
    shape_res = answers.get("answer_shape") or {}
    shape_choice = str(shape_res.get("choice", "")).strip().lower() if isinstance(shape_res, dict) else ""
    if shape_signals["explicit_count"] is not None or shape_signals["answer_shape"] != "fact_answer":
        answer_shape = shape_signals["answer_shape"]
    elif shape_choice in _VALID_ANSWER_SHAPES:
        answer_shape = shape_choice
    else:
        answer_shape = shape_signals["answer_shape"]

    strategy = (
        "multi"
        if (
            intent_choice == "complex_reasoning"
            or coarse_intent == "AMBIGUOUS"
            or memory_scope in {"hybrid_both", "full_session_audit"}
            or temporal_mode == "change_lineage"
            or answer_shape in {"multi_facet_compare", "summarize_set"}
        )
        else "vector"
    )
    return {
        "query": query,
        "coarse_intent": coarse_intent,
        "need_retrieval": True,
        "suggested_strategy": strategy,
        "answer_shape": answer_shape,
        "target_unit": shape_signals["target_unit"],
        "explicit_count": shape_signals["explicit_count"],
        "is_catalog_query": shape_signals["is_catalog_query"],
        "order_mode": shape_signals["order_mode"],
        "subqueries": shape_signals["subqueries"],
        "memory_scope": memory_scope,
        "temporal_mode": temporal_mode,
        "confidence": intent_conf,
        "model": model,
        "latency_ms": latency_ms,
        "degraded": False,
    }


def _fetch_single_live_kev4b(case: IsolatedQueryCase) -> dict[str, Any]:
    """Invoke SAG `main`'s current unified `route_query_async` router (no deleted `/systemone` imports)."""
    t0 = time.perf_counter()
    try:
        decision = asyncio.run(
            route_query_async(
                case.query,
                has_sources=True,
                scoped=True,
                use_cache=False,
            )
        )
        ms = round((time.perf_counter() - t0) * 1000.0, 2)
        payload = decision.to_dict()
        return {
            "case_id": case.case_id,
            "suite": case.suite,
            "query": case.query,
            "schema": "unified_route_query_async",
            "model": str(payload.get("model") or settings.decision_model),
            "latency_ms": float(payload.get("latency_ms") or ms),
            "decision": payload,
            "usage": {},
            "error": payload.get("degraded_reason") if payload.get("degraded") else None,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "case_id": case.case_id,
            "suite": case.suite,
            "query": case.query,
            "schema": "unified_route_query_async",
            "model": "error",
            "latency_ms": 0.0,
            "decision": {},
            "usage": {},
            "error": str(exc),
        }


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

    fb_decision = _degraded_decision(query, "decision_router_disabled").to_dict()
    inferred_scope, inferred_temporal = _infer_legacy_ecce_routing_signals(query, coarse_intent="AMBIGUOUS")
    shape_signals = _extract_legacy_query_signals(query)
    fb_decision.update(
        {
            "answer_shape": shape_signals["answer_shape"],
            "target_unit": shape_signals["target_unit"],
            "explicit_count": shape_signals["explicit_count"],
            "is_catalog_query": shape_signals["is_catalog_query"],
            "order_mode": shape_signals["order_mode"],
            "subqueries": shape_signals["subqueries"],
            "memory_scope": inferred_scope,
            "temporal_mode": inferred_temporal,
        }
    )
    analysis = analyze_query(query, segmentation_enabled=False)
    features: QueryFeatures = analysis.features
    strat_plan: QueryStrategyPlan = plan_query(
        query,
        features=features,
        route_decision=fb_decision,
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
    unified_decision = live_entry.get("decision") if isinstance(live_entry.get("decision"), dict) else None
    usage = live_entry.get("usage") or {}
    in_tok = int(usage.get("input_tokens", 0) or 0)
    out_tok = int(usage.get("output_tokens", 0) or 0)
    tot_tok = in_tok + out_tok
    cost_usd = (tot_tok * SILICONFLOW_KEV4B_PRICE_PER_1M_USD) / 1_000_000.0
    http_latency_ms = float(live_entry.get("latency_ms", 0.0) or 0.0)

    if unified_decision:
        is_chat = not bool(unified_decision.get("need_retrieval", True))
        raw_shape = str(unified_decision.get("answer_shape", "fact_answer")).strip().lower()
        raw_scope = str(unified_decision.get("memory_scope", "project_documents")).strip().lower()
        raw_temp = str(unified_decision.get("temporal_mode", "atemporal")).strip().lower()
        intent_choice = "complex_reasoning" if unified_decision.get("suggested_strategy") == "multi" else "factual_lookup"
    else:
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

    unified_decision = live_entry.get("decision") if isinstance(live_entry.get("decision"), dict) else None
    if unified_decision:
        decision = unified_decision
    else:
        decision = _adapt_legacy_systemone_answers(
            query,
            answers,
            str(live_entry.get("model") or settings.decision_model),
            http_latency_ms,
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
        route_decision=decision,
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
            # SAG main `retrieval_plan._shape_to_target_output` reserves OutputMode.LIST for
            # {DOCUMENT, TOPIC, FACT, TURN}; PASSAGE with explicit_count=12 uses ANSWER + effective_n=12.
            expected_output="ANSWER",
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

    sag_repo = DATASET_ROOT.parent / "sag-laya-integration"
    try:
        git_sha = subprocess.check_output(
            ["git", "-C", str(sag_repo), "rev-parse", "HEAD"],
            text=True,
        ).strip()
    except Exception:
        git_sha = None
    cached_legacy_count = sum(
        1 for c in all_cases if c.case_id in _LIVE_KEV4B_CACHE and not _LIVE_KEV4B_CACHE[c.case_id].get("decision")
    )
    report = {
        "benchmark": "isolated_pre_retrieve_ablation_v2_live_kev4b",
        "measurement_mode": "live_refreshed" if refresh_live else "cached_replay_isolated_ablation",
        "cached_legacy_systemone_rows": cached_legacy_count,
        "git_commit": git_sha,
        "protocol_references": [
            "Adaptive-RAG (NAACL 2024, arXiv:2403.14403) — Question Complexity & Budget Allocation",
            "RouterBench (ICLR / arXiv:2403.12031) — Routing Accuracy vs Cost/Latency Trade-off",
            "Meta CRAG (KDD Cup 2024, arXiv:2406.04744) — 7-Axis Question Shape & Temporal Routing",
            "EnterpriseRAG-Bench (RetrievalCI Bench-v0) & VN-MTEB RAG Bench 2026",
            "SAG Unified 1-Call Decision Router (route_query_async) — Isolated Pre-Retrieve Ablation",
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
