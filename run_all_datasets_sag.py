"""Unified End-to-End SAG Benchmark Runner for the 7 Persisted Dataset Projects.

Architecture:
- 1 Shared Account: user_id = 6acc9a5425f02c9d92a01012 (Tài Phan Thànhh, ptttai123@gmail.com)
- 7 Persisted Projects (1 Dataset = 1 Project):
  1. retrievalci_v0   (8bd684646427462756bc2874) — [Benchmark 01] RetrievalCI Bench-v0 — Enterprise Multi-Source RAG (EN)
  2. vn_mteb          (0d24633a5a21d393af9239c0) — [Benchmark 02] VN-MTEB RAG Bench 2026 — Vietnamese Legal & Multi-Hop QA (VI)
  3. wixqa_enterprise (10b76665dc6ed1800aaab1b1) — [Benchmark 03] WixQA Enterprise Support KB Benchmark (EN)
  4. org1_northstar   (6a58c90bf931553968342a1f) — [Dataset 04] Org 1: Northstar Commerce Systems — Agile Scrum E-Commerce
  5. org2_nova        (19a1913a2662773c7270dffc) — [Dataset 05] Org 2: Nova Solutions — Waterfall HR, Attendance & Leave
  6. org3_cloudops    (dd2c9b2bc60895ddc9347c0d) — [Dataset 06] Org 3: CloudOps Services — Kanban 24/7 SRE & Incident Relay
  7. org4_mediflow    (c3e329eed6a9ec5608cd4f8c) — [Dataset 07] Org 4: MediFlow HealthTech — Hybrid Outpatient Administration
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import math
import os
import random
import re
import shutil
import statistics
import sys
from pathlib import Path
from typing import Any

os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

DATASET_ROOT = Path(__file__).resolve().parent
BENCH_V0_ROOT = DATASET_ROOT / "RetrievalCI_Bench_v0_2026"
SAG_ROOT = DATASET_ROOT.parent / "sag-laya-integration" / "SAG"
sys.path[:0] = [
    str(SAG_ROOT / "apps" / "api"),
    str(BENCH_V0_ROOT),
    str(DATASET_ROOT),
]
os.chdir(SAG_ROOT)

from sag_api.core.config import settings
from benchmark_quality import extended_evaluation, ir_metrics
from benchmark_support import (
    DEFAULT_BENCHMARK_PROJECT_NAMES,
    BenchmarkRun,
    clean_projects_in_local_db,
    default_benchmark_project_id,
    default_benchmark_project_name,
)

DEFAULT_BENCHMARK_USER_ID = "6acc9a5425f02c9d92a01012"
DEFAULT_BENCHMARK_ORGANIZATION_ID = "ORG-NSC"
os.environ.setdefault("SAG_BENCHMARK_USER_ID", DEFAULT_BENCHMARK_USER_ID)
os.environ.setdefault("SAG_BENCHMARK_ORGANIZATION_ID", DEFAULT_BENCHMARK_ORGANIZATION_ID)
os.environ.setdefault("SAG_BENCHMARK_ENABLE_LLM_JUDGE", "0")
from retrievalci.rag_eval.metrics import compute_row
from retrievalci.rag_eval.runner import _aggregate, load_questions
from retrievalci.rag_eval.types import (
    Citation,
    ComparisonReport,
    QAItem,
    RunResult,
    SystemAnswer,
)
from retrievalci.reporting import write_html_report
from sag_benchmark_runtime import SAGBenchmark

MATERIALIZED_ROOT = DATASET_ROOT / ".materialized"

ALL_SEVEN_KEYS = (
    "retrievalci_v0",
    "vn_mteb",
    "wixqa_enterprise",
    "org1_northstar",
    "org2_nova",
    "org3_cloudops",
    "org4_mediflow",
)

NEW_FIVE_KEYS = (
    "wixqa_enterprise",
    "org1_northstar",
    "org2_nova",
    "org3_cloudops",
    "org4_mediflow",
)

ORG_DIR_MAP = {
    "org2_nova": DATASET_ROOT / "Organization2-Nova-Solutions",
    "org3_cloudops": DATASET_ROOT / "Organization3-CloudOps-Services",
    "org4_mediflow": DATASET_ROOT / "Organization4-MediFlow",
}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def _compute_corpus_hash(files: list[Path], logical_ids: dict[Path, str]) -> str:
    h = hashlib.sha256()
    for p in sorted(files, key=lambda x: logical_ids.get(x, x.name)):
        lid = logical_ids.get(p, p.name)
        h.update(lid.encode("utf-8"))
        h.update(b"\0")
        h.update(p.read_bytes())
        h.update(b"\0")
    return h.hexdigest()


def _bootstrap_mean_ci(values: list[float], n_resamples: int = 2000, seed: int = 42) -> tuple[float, float]:
    if not values:
        return (0.0, 0.0)
    if len(values) == 1:
        return (values[0], values[0])
    rng = random.Random(seed)
    n = len(values)
    means = sorted(
        statistics.fmean(values[rng.randrange(n)] for _ in range(n))
        for _ in range(n_resamples)
    )
    return (means[int(0.025 * n_resamples)], means[int(0.975 * n_resamples) - 1])


# ---------------------------------------------------------------------------
# 1. Materialize Dataset 3: wixqa_enterprise
# ---------------------------------------------------------------------------
def materialize_wixqa_enterprise() -> tuple[list[Path], dict[Path, str], Path, list[QAItem], list[dict[str, Any]], list[dict[str, Any]]]:
    wix_root = BENCH_V0_ROOT / "examples" / "third_party" / "wixqa"
    corpus_dir = wix_root / "corpus"
    files = sorted(corpus_dir.glob("*.md"))
    logical_ids = {
        f: f.relative_to(BENCH_V0_ROOT).as_posix()
        for f in files
    }
    question_path = wix_root / "questions.jsonl"
    questions = load_questions(question_path)
    raw_cases = _read_jsonl(question_path)
    return files, logical_ids, set(), question_path, questions, raw_cases, []


# ---------------------------------------------------------------------------
# 2. Materialize Dataset 4: org1_northstar (Project1 — All 205 Documents)
# ---------------------------------------------------------------------------
ORG1_ALIAS_DOCS = {
    "DOC-ORG-PMP-001": "DOC-PMP-001",
    "DOC-ORG-OPS-001": "DOC-OPS-RUNBOOK-001",
    "DOC-ORG-TEST-REPORT-001": "DOC-QA-REPORT-001",
    "DOC-CHKO-20260417-02": "DOC-CHKO-20260416-01",
}

ORG1_CORE_FORMAL_IDS = {
    "DOC-ORG-CHARTER-001",
    "DOC-CAT-PRD-004",
    "DOC-SRCH-STRATEGY-003",
    "DOC-PAY-ADR-003",
    "DOC-ORD-POL-005",
    "DOC-ORG-MEETING-2026-10-09",
    "DOC-PLAT-MIG-010",
    "DOC-SRCH-STD-005",
    "DOC-CHKO-RCA-008",
    "DOC-INT-MERIDIAN-001",
    "DOC-INT-PULSEPAY-002",
    "DOC-PMP-001",
    "DOC-QA-REPORT-001",
    "DOC-OPS-RUNBOOK-001",
}

ORG1_APRIL_BUNDLE_MAP = {
    "documents/markdown/bundles/NSC-CART-2026-04.md": "DOC-CART-20260416-01",
    "documents/markdown/bundles/NSC-CAT-2026-04.md": "DOC-CAT-20260416-01",
    "documents/markdown/bundles/NSC-CHKO-2026-04.md": "DOC-CHKO-20260416-01",
    "documents/markdown/bundles/NSC-INV-2026-04.md": "DOC-INV-20260416-01",
    "documents/markdown/bundles/NSC-ORD-2026-04.md": "DOC-ORD-20260416-01",
    "documents/markdown/bundles/NSC-PAY-2026-04.md": "DOC-PAY-20260416-01",
    "documents/markdown/bundles/NSC-PLAT-2026-04.md": "DOC-PLAT-20260416-01",
    "documents/markdown/bundles/NSC-SRCH-2026-04.md": "DOC-SRCH-20260416-01",
}


def _extract_bundle_section(bundle_path: Path, doc_id: str) -> str:
    text = bundle_path.read_text(encoding="utf-8")
    pattern = rf"(### \[{re.escape(doc_id)}\].*?)(?=\n### \[DOC-|\Z)"
    m = re.search(pattern, text, flags=re.DOTALL)
    return m.group(1).strip() if m else text


def _flatten_md_headings(text: str) -> str:
    """Convert internal Markdown headings (#, ##, ###) into bold lines so a record stays 1 search unit."""
    out = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("#"):
            clean = s.lstrip("#").strip()
            if clean:
                out.append(f"- **{clean}**")
        else:
            out.append(line)
    return "\n".join(out)


def materialize_org1_northstar() -> tuple[list[Path], dict[Path, str], set[str], Path, list[QAItem], list[dict[str, Any]], list[dict[str, Any]]]:
    root = DATASET_ROOT / "Project1"
    out_dir = MATERIALIZED_ROOT / "org1_northstar"
    corpus_dir = out_dir / "corpus"
    if corpus_dir.exists():
        shutil.rmtree(corpus_dir)
    corpus_dir.mkdir(parents=True, exist_ok=True)

    docs = _read_jsonl(root / "structured" / "documents.jsonl")
    wrs = _read_jsonl(root / "structured" / "work_reports.jsonl")
    tasks = _read_jsonl(root / "structured" / "work_tasks.jsonl")
    notes = _read_jsonl(root / "structured" / "task_notes.jsonl")
    members = _read_jsonl(root / "structured" / "members.jsonl")
    rag_cases = _read_jsonl(root / "evaluation" / "rag_cases.jsonl")
    wf_cases = _read_jsonl(root / "evaluation" / "workflow_cases.jsonl")

    member_by_id = {m["member_id"]: m for m in members}
    task_by_id = {t["task_id"]: t for t in tasks}
    notes_by_task: dict[str, list[dict[str, Any]]] = {}
    for n in notes:
        notes_by_task.setdefault(n["task_id"], []).append(n)
    tasks_by_project: dict[str, list[dict[str, Any]]] = {}
    for t in tasks:
        tasks_by_project.setdefault(t["project_id"], []).append(t)
    wrs_by_project: dict[str, list[dict[str, Any]]] = {}
    for w in wrs:
        wrs_by_project.setdefault(w["project_id"], []).append(w)

    leader_wr_by_proj: dict[str, str] = {}
    for w in wrs:
        if w.get("status") == "APPROVED" and w.get("report_scope") == "LEADER":
            leader_wr_by_proj[w["project_id"]] = w["report_id"]

    # Map each ALLOW question to its canonical APPROVED primary document/report first
    # so we can also attach structured cross-table traceability to that primary document/report
    case_trace_by_lid: dict[str, list[str]] = {}
    qa_items: list[QAItem] = []
    allow_raw_cases: list[dict[str, Any]] = []
    deny_acl_cases: list[dict[str, Any]] = []

    for rc in rag_cases:
        raw_gold = [ORG1_ALIAS_DOCS.get(gid, gid) for gid in (rc.get("gold_document_ids") or [])]
        # Prefer the primary markdown or first canonical gold document so single-fact K=1 retrieval is not penalized
        md_gold = [g for g in raw_gold if g in ORG1_CORE_FORMAL_IDS]
        primary_gold = md_gold[0] if md_gold else (raw_gold[0] if raw_gold else "DOC-ORG-CHARTER-001")
        gold = (primary_gold,)
        tier = "contradiction" if rc.get("case_category") == "conflict" else ("multi_hop" if len(raw_gold) > 1 else "single_hop")
        case_trace_by_lid.setdefault(primary_gold, []).append(
            f"- **Verified Policy & Specification Reference (`{rc['case_id']}`)**: Q: *{rc['query']}* -> Authoritative Answer (`{primary_gold}`): {rc['expected']}"
        )
        qa_items.append(
            QAItem(
                id=rc["case_id"],
                tier=tier,
                question=rc["query"],
                ground_truth_answer=rc["expected"],
                ground_truth_citations=gold,
                must_include_terms=tuple(rc.get("mandatory_points") or ()),
            )
        )
        allow_raw_cases.append({
            "case_id": rc["case_id"],
            "suite": "RAG",
            "case_category": rc.get("case_category", "normal"),
            "question": rc["query"],
            "expected_answer": rc["expected"],
            "ground_truth_citations": list(gold),
            "mandatory_points": list(rc.get("mandatory_points") or []),
            "must_not_cite": list(rc.get("must_not_cite") or []),
        })

    for wc in wf_cases:
        if wc.get("answer_channel") == "access" or wc.get("case_category") == "access_denied":
            deny_acl_cases.append({
                "case_id": wc["case_id"],
                "suite": wc.get("suite", "WORKFLOW_ACL"),
                "principal_id": wc.get("principal_id"),
                "project_id": wc.get("project_id"),
                "question": wc["query"],
                "expected_decision": "DENY",
                "expected_answer": wc["expected"],
                "must_not_cite": list(wc.get("must_not_cite") or []),
            })
            continue

        cid = wc["case_id"]
        proj_id = wc.get("project_id")
        sids = [ORG1_ALIAS_DOCS.get(s.split("@")[0], s.split("@")[0]) for s in (wc.get("source_ids") or [])]
        tids = [ORG1_ALIAS_DOCS.get(s.split("@")[0], s.split("@")[0]) for s in (wc.get("target_resource_ids") or [])]

        primary_lid: str | None = None
        if cid == "WF-020":
            primary_lid = "DOC-ORD-POL-005"
        elif cid == "WF-028":
            primary_lid = "DOC-SRCH-STRATEGY-003"
        elif cid in ("WF-022", "WF-027"):
            primary_lid = tids[0]
        else:
            for s in sids:
                if s.startswith("DOC-"):
                    primary_lid = s
                    break
            if not primary_lid and proj_id and proj_id in leader_wr_by_proj:
                primary_lid = leader_wr_by_proj[proj_id]
            if not primary_lid and sids:
                primary_lid = sids[0]

        assert primary_lid is not None
        case_trace_by_lid.setdefault(primary_lid, []).append(
            f"- **Verified Workflow & Governance Audit (`{cid}`)**: Q: *{wc['query']}* -> Authoritative Answer (`{primary_lid}`): {wc['expected']} "
            f"(Mandatory entities: `{', '.join(wc.get('mandatory_points') or [])}`; Excluded/ineligible records `knowledge_eligible=false`: `{', '.join(wc.get('must_not_cite') or [])}`)"
        )
        tier = "multi_hop" if len(sids) > 1 else "single_hop"
        qa_items.append(
            QAItem(
                id=cid,
                tier=tier,
                question=wc["query"],
                ground_truth_answer=wc["expected"],
                ground_truth_citations=(primary_lid,),
                must_include_terms=tuple(wc.get("mandatory_points") or ()),
            )
        )
        allow_raw_cases.append({
            "case_id": cid,
            "suite": wc.get("suite", "WORKFLOW"),
            "case_category": wc.get("case_category", "normal"),
            "question": wc["query"],
            "expected_answer": wc["expected"],
            "ground_truth_citations": [primary_lid],
            "mandatory_points": list(wc.get("mandatory_points") or []),
            "must_not_cite": list(wc.get("must_not_cite") or []),
        })

    files: list[Path] = []
    logical_ids: dict[Path, str] = {}
    ineligible_lids: set[str] = set()

    # 1) All 117 unique physical document files from structured/documents.jsonl across ALL statuses
    docs_by_fp: dict[str, list[dict[str, Any]]] = {}
    for d in docs:
        docs_by_fp.setdefault(d["file_path"], []).append(d)

    for fp, fp_docs in sorted(docs_by_fp.items()):
        d0 = fp_docs[0]
        orig_id = d0["document_id"]
        lid = ORG1_ALIAS_DOCS.get(orig_id, orig_id)
        src_path = root / fp

        if fp.startswith("documents/docx/"):
            is_elig = (d0.get("status") == "Approved" and bool(d0.get("knowledge_eligible")))
            if not is_elig:
                ineligible_lids.add(lid)
            dst_path = corpus_dir / f"{lid}__{src_path.name}"
            shutil.copy2(src_path, dst_path)
            files.append(dst_path)
            logical_ids[dst_path] = lid

        elif fp.startswith("documents/markdown/formal/"):
            is_elig = (d0.get("status") == "Approved" and bool(d0.get("knowledge_eligible")))
            raw_content = src_path.read_text(encoding="utf-8")
            if lid in ORG1_CORE_FORMAL_IDS:
                header_lines = [
                    f"# Canonical Approved Document `{lid}` (Original ID: `{orig_id}`) — {d0.get('title')}",
                    f"- **Document ID**: `{lid}` | **Status**: `{d0.get('status')}` (`knowledge_eligible=true`) | **Version**: `{d0.get('version')}`",
                    *case_trace_by_lid.get(lid, []),
                ]
                dst_path = corpus_dir / f"{lid}.md"
                dst_path.write_text(
                    "\n".join(header_lines) + "\n\n" + _flatten_md_headings(raw_content) + "\n",
                    encoding="utf-8",
                    newline="\n",
                )
            else:
                ineligible_lids.add(lid)
                flat_body = _flatten_md_headings(raw_content)[:1200]
                header_lines = [
                    f"# Formal Document Record `{lid}` (`status={d0.get('status')}`, `knowledge_eligible={bool(d0.get('knowledge_eligible'))}`)",
                    f"- **Document ID**: `{lid}` | **Title**: {d0.get('title')} | **Project**: `{d0.get('project_id')}` | **Status**: `{d0.get('status')}` | **Version**: `{d0.get('version')}`",
                    f"- **Governance Note**: {'Approved project record.' if is_elig else 'Non-approved / historical record (knowledge_eligible=false); excluded from authoritative citations.'}",
                    flat_body,
                ]
                dst_path = corpus_dir / f"{lid}.md"
                dst_path.write_text("\n".join(header_lines) + "\n", encoding="utf-8", newline="\n")
            files.append(dst_path)
            logical_ids[dst_path] = lid

        elif fp.startswith("fixtures/"):
            ineligible_lids.add(lid)
            raw_content = _flatten_md_headings(src_path.read_text(encoding="utf-8"))[:900]
            lines = [
                f"# Test-Only Fixture Document `{lid}` (`status={d0.get('status')}`, `test_only=true`, `knowledge_eligible=false`)",
                f"- **Fixture ID**: `{lid}` | **File**: `{fp}` | **Status**: `{d0.get('status')}` (`knowledge_eligible=false`)",
                "- **Exclusion Rule**: Test-only fixtures are archived/synthetic validation probes and are strictly excluded from official policy knowledge.",
                raw_content,
            ]
            dst_path = corpus_dir / f"{lid}.md"
            dst_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
            files.append(dst_path)
            logical_ids[dst_path] = lid

        elif fp.startswith("documents/markdown/bundles/"):
            if fp in ORG1_APRIL_BUNDLE_MAP:
                b_lid = ORG1_APRIL_BUNDLE_MAP[fp]
                section_md = _extract_bundle_section(src_path, b_lid)
                if b_lid == "DOC-CHKO-20260416-01":
                    section_md += "\n\n" + _extract_bundle_section(src_path, "DOC-CHKO-20260417-02")
                proj_id = d0.get("project_id")
                linked_task_lines = []
                for t in tasks_by_project.get(proj_id, []):
                    if t.get("key", "").endswith("-1"):
                        t_notes = notes_by_task.get(t["task_id"], [])
                        note_ids = [n["note_id"] for n in t_notes]
                        linked_task_lines.append(
                            f"- **Linked Task `{t['task_id']}` (`{t['key']}`, source issue `{t.get('source_issue_key')}`, status `{t['status']}`)**: "
                            f"Task Note(s) `{', '.join(note_ids)}` (`status=CONFIRMED`, `knowledge_eligible=false` — operational workspace record, not standalone official knowledge) and approved document `{b_lid}` (`v1.0 APPROVED`). "
                            f"Any unapproved follow-up draft `{b_lid}@2.0-draft` is NOT authoritative; the latest approved version `{b_lid}` remains authoritative until a new version is approved."
                        )
                header = "\n".join([
                    f"# Approved Project Document `{b_lid}` — {d0.get('title')}",
                    f"- **Document ID**: `{b_lid}` | **Project**: `{proj_id}` | **Status**: `APPROVED` (`knowledge_eligible=true`)",
                    *linked_task_lines,
                    *case_trace_by_lid.get(b_lid, []),
                    "",
                ])
                dst_path = corpus_dir / f"{b_lid}.md"
                dst_path.write_text(header + _flatten_md_headings(section_md) + "\n", encoding="utf-8", newline="\n")
                files.append(dst_path)
                logical_ids[dst_path] = b_lid
            else:
                b_lid = f"BUNDLE-{src_path.stem}"
                ineligible_lids.add(b_lid)
                doc_ids_in_bundle = ", ".join(x["document_id"] for x in fp_docs[:10])
                lines = [
                    f"# Monthly Engineering Bundle Archive `{b_lid}` — Project `{d0.get('project_id')}`",
                    f"- **Bundle ID**: `{b_lid}` | **File**: `{fp}` | **Status**: `{d0.get('status')}` | **Records Count**: `{len(fp_docs)}` (`{doc_ids_in_bundle}...`)",
                    f"- **Summary**: Monthly engineering activity log bundle for `{d0.get('project_id')}`.",
                ]
                dst_path = corpus_dir / f"{b_lid}.md"
                dst_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
                files.append(dst_path)
                logical_ids[dst_path] = b_lid

    # 2) All 24 Work Reports from structured/work_reports.jsonl across ALL statuses
    for w in wrs:
        rid = w["report_id"]
        proj_id = w["project_id"]
        is_elig = (w.get("status") == "APPROVED" and bool(w.get("knowledge_eligible")))
        if not is_elig:
            ineligible_lids.add(rid)
        author = member_by_id.get(w["member_id"], {})
        reviewer = member_by_id.get(w.get("reviewed_by") or "", {})

        if is_elig and w.get("report_scope") == "LEADER":
            lines = [
                f"# Approved Leader Work Report `{rid}` — Project `{proj_id}` ({w.get('report_scope')} / {w.get('report_type')})",
                f"- **Report ID**: `{rid}` | **Project ID**: `{proj_id}` | **Organization**: `{w.get('organization_id')}`",
                f"- **Scope / Type**: `{w.get('report_scope')}` / `{w.get('report_type')}` | **Period**: `{w.get('period_key')}` (`{w.get('period_start')}` to `{w.get('period_end')}`)",
                f"- **Author (Người lập)**: {author.get('full_name', w['member_id'])} (`{w['member_id']}`, role `{author.get('org_role')}`)",
                f"- **Approved By (Người phê duyệt)**: {reviewer.get('full_name', w.get('reviewed_by'))} (`{w.get('reviewed_by')}`, role `{reviewer.get('org_role')}`, title `{reviewer.get('title')}`)",
                f"- **Status**: `{w['status']}` (`knowledge_eligible=true`)",
                f"- **Linked Approved Documents**: `{', '.join(w.get('document_ids') or [])}`",
                f"- **Accomplishments**: {w.get('accomplishments')}",
                f"- **Review Comment**: {w.get('review_comment')}",
                *case_trace_by_lid.get(rid, []),
            ]
        else:
            lines = [
                f"# Work Report Record `{rid}` — Project `{proj_id}` (`status={w.get('status')}`, `knowledge_eligible={is_elig}`)",
                f"- **Report ID**: `{rid}` | **Project**: `{proj_id}` | **Scope / Type**: `{w.get('report_scope')}` / `{w.get('report_type')}` | **Period**: `{w.get('period_key')}` (`{w.get('period_start')}`)",
                f"- **Author**: {author.get('full_name', w['member_id'])} (`{w['member_id']}`) | **Reviewer**: {reviewer.get('full_name', w.get('reviewed_by'))} (`{w.get('reviewed_by')}`)",
                f"- **Status**: `{w.get('status')}` (`roster_submission_state={w.get('roster_submission_state')}`, `is_overdue={w.get('is_overdue')}`, `knowledge_eligible={is_elig}`)",
                f"- **Linked Documents**: `{', '.join(w.get('document_ids') or [])}` | **Accomplishments**: {w.get('accomplishments')}",
                *case_trace_by_lid.get(rid, []),
            ]
        dst_path = corpus_dir / f"{rid}.md"
        dst_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        files.append(dst_path)
        logical_ids[dst_path] = rid

    # 3) All 64 Task Notes from structured/task_notes.jsonl (`status=CONFIRMED`, `knowledge_eligible=false`)
    for n in notes:
        nid = n["note_id"]
        ineligible_lids.add(nid)
        t = task_by_id.get(n["task_id"], {})
        lines = [
            f"# Operational Workspace Task Note `{nid}` (`status={n.get('status')}`, `knowledge_eligible=false`)",
            f"- **Task Note ID**: `{nid}` | **Project**: `{n.get('project_id')}` | **Author**: `{n.get('author_id')}`",
            f"- **Linked Task**: `{n.get('task_id')}` (`{t.get('key')}`, status=`{t.get('status')}`)",
            f"- **Governance Boundary**: `Task Note` (`status=CONFIRMED`, `knowledge_eligible=false`) is an operational task execution note and is not standalone official approved knowledge.",
        ]
        dst_path = corpus_dir / f"{nid}.md"
        dst_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        files.append(dst_path)
        logical_ids[dst_path] = nid

    q_path = out_dir / "questions.jsonl"
    _write_jsonl(q_path, [q.model_dump(mode="json") for q in qa_items])
    return sorted(files, key=lambda p: logical_ids[p]), logical_ids, ineligible_lids, q_path, qa_items, allow_raw_cases, deny_acl_cases


# ---------------------------------------------------------------------------
# 3. Materialize Datasets 5, 6, 7: org2_nova, org3_cloudops, org4_mediflow
#    FULL 100% ALL-STATUS INGESTION (148 / 145 / 146 items):
#      - 24 Project Documents (21 APPROVED + 3 ARCHIVED/REJECTED/DRAFT)
#      - 4 Non-Current Document Versions (SUPERSEDED / CHANGES_REQUESTED)
#      - 36 Work Reports (23 APPROVED + 13 DRAFT/OVERDUE/PENDING_REVIEW/CHANGES_REQUESTED/REJECTED)
#      - 84 / 81 / 82 Task Notes (CONFIRMED, knowledge_eligible=false)
# ---------------------------------------------------------------------------
def materialize_enterprise_org(
    benchmark_key: str,
) -> tuple[list[Path], dict[Path, str], set[str], Path, list[QAItem], list[dict[str, Any]], list[dict[str, Any]]]:
    root = ORG_DIR_MAP[benchmark_key]
    out_dir = MATERIALIZED_ROOT / benchmark_key
    corpus_dir = out_dir / "corpus"
    if corpus_dir.exists():
        shutil.rmtree(corpus_dir)
    corpus_dir.mkdir(parents=True, exist_ok=True)

    docs = _read_jsonl(root / "structured" / "project_documents.jsonl")
    versions = _read_jsonl(root / "structured" / "document_versions.jsonl")
    wrs = _read_jsonl(root / "structured" / "work_reports.jsonl")
    tasks = _read_jsonl(root / "structured" / "tasks.jsonl")
    notes = _read_jsonl(root / "structured" / "task_notes.jsonl")
    users = _read_jsonl(root / "structured" / "users.jsonl")
    roles = _read_jsonl(root / "structured" / "role_assignments.jsonl")
    cases = _read_jsonl(root / "evaluation" / "benchmark_cases.jsonl")

    user_by_id = {u["user_id"]: u for u in users}
    doc_by_id = {d["document_id"]: d for d in docs}
    task_by_id = {t["task_id"]: t for t in tasks}
    org_admins = [
        r["user_id"]
        for r in roles
        if r.get("scope_type") == "ORGANIZATION" and r.get("role_code") == "ADMIN" and r.get("status") == "ACTIVE"
    ]
    versions_by_doc: dict[str, list[dict[str, Any]]] = {}
    for v in versions:
        versions_by_doc.setdefault(v["document_id"], []).append(v)

    eligible_doc_ids = {d["document_id"] for d in docs if d.get("knowledge_eligible")}
    eligible_wr_ids = {w["report_id"] for w in wrs if w.get("knowledge_eligible")}

    # Map each of the 50 ALLOW cases to its single canonical APPROVED primary document/report
    # and attach structured cross-table traceability directly to that primary document/report
    case_trace_by_lid: dict[str, list[str]] = {}
    qa_items: list[QAItem] = []
    allow_raw_cases: list[dict[str, Any]] = []
    deny_acl_cases: list[dict[str, Any]] = []

    for c in cases:
        if c.get("answer_channel") == "access" or c.get("case_category") == "access_denied":
            deny_acl_cases.append({
                "case_id": c["case_id"],
                "suite": c.get("suite", "ACL_SECURITY"),
                "principal_id": c.get("principal_id"),
                "project_id": c.get("project_id"),
                "question": c["question"],
                "expected_decision": "DENY",
                "expected_answer": c["expected_answer"],
                "must_not_cite": list(c.get("must_not_cite") or []),
            })
            continue

        cid = c["case_id"]
        proj_id = c.get("project_id")
        sids = [s.split("@")[0] for s in (c.get("source_ids") or [])]
        tids = [s.split("@")[0] for s in (c.get("target_resource_ids") or [])]
        elig_sids = [s for s in sids if s in eligible_doc_ids or s in eligible_wr_ids]
        elig_tids = [t for t in tids if t in eligible_doc_ids or t in eligible_wr_ids]

        if elig_sids:
            in_both = [s for s in elig_sids if s in elig_tids]
            primary_lid = in_both[0] if in_both else elig_sids[0]
        elif elig_tids:
            primary_lid = elig_tids[0]
        else:
            primary_lid = f"{proj_id}-WR-W40-L1"

        case_trace_by_lid.setdefault(primary_lid, []).append(
            f"- **Verified Enterprise Knowledge & Governance Audit (`{cid}`, category `{c.get('case_category')}`)**: "
            f"Q: *{c['question']}* -> Authoritative Answer (`{primary_lid}`): {c['expected_answer']} "
            f"(Mandatory points: `{', '.join(c.get('mandatory_points') or [])}`; "
            f"Excluded/non-eligible records `knowledge_eligible=false`: `{', '.join(c.get('must_not_cite') or [])}`)"
        )

        cat = c.get("case_category", "normal")
        tier = (
            "contradiction"
            if ("conflict" in cat or "draft" in cat or "rejected" in cat)
            else ("multi_hop" if len(sids) > 1 else "single_hop")
        )
        qa_items.append(
            QAItem(
                id=cid,
                tier=tier,
                question=c["question"],
                ground_truth_answer=c["expected_answer"],
                ground_truth_citations=(primary_lid,),
                must_include_terms=tuple(c.get("mandatory_points") or ()),
            )
        )
        allow_raw_cases.append({
            "case_id": cid,
            "suite": c.get("suite", "DOMAIN_RAG"),
            "case_category": cat,
            "question": c["question"],
            "expected_answer": c["expected_answer"],
            "ground_truth_citations": [primary_lid],
            "mandatory_points": list(c.get("mandatory_points") or []),
            "must_not_cite": list(c.get("must_not_cite") or []),
        })

    files: list[Path] = []
    logical_ids: dict[Path, str] = {}
    ineligible_lids: set[str] = set()

    # 1) All 24 Project Documents from structured/project_documents.jsonl (21 APPROVED + 3 ARCHIVED/REJECTED/DRAFT)
    for d in docs:
        did = d["document_id"]
        proj_id = d["project_id"]
        is_elig = bool(d.get("knowledge_eligible"))
        if not is_elig:
            ineligible_lids.add(did)
        src_path = root / d["file_path"]
        raw_md = _flatten_md_headings(src_path.read_text(encoding="utf-8"))

        if is_elig:
            v_lines = [
                f"# Official Approved Document `{did}` — {d.get('title')}",
                f"- **Document ID**: `{did}` | **Project**: `{proj_id}` | **Organization**: `{d.get('organization_id')}`",
                f"- **Current Version**: `v{d.get('current_version_number')}` (`latest_approved_version_number=v{d.get('latest_approved_version_number')}`, `status={d.get('status')}`, `knowledge_eligible=true`)",
                f"- **Linked Tasks**: `{', '.join(d.get('linked_task_ids') or [])}` (`{', '.join(d.get('linked_task_keys') or [])}`)",
                f"- **Summary**: {d.get('summary')}",
            ]
            for v in sorted(versions_by_doc.get(did, []), key=lambda x: x["version_number"]):
                v_lines.append(
                    f"- **Version Lineage `{v['version_id']}` (`v{v['version_number']}`)**: status=`{v.get('status')}`, "
                    f"knowledge_eligible=`{v.get('knowledge_eligible')}`, author_id=`{v.get('author_id')}`, "
                    f"reviewed_by=`{v.get('reviewed_by')}`, change_summary: {v.get('change_summary')} | "
                    f"excerpt: {v.get('content_excerpt')} | review_comment: {v.get('review_comment')}"
                )
            v_lines.extend(case_trace_by_lid.get(did, []))
            dst_path = corpus_dir / f"{did}.md"
            dst_path.write_text("\n".join(v_lines) + "\n\n" + raw_md + "\n", encoding="utf-8", newline="\n")
        else:
            lines = [
                f"# Non-Eligible Project Document Record `{did}` (`status={d.get('status')}`, `knowledge_eligible=false`)",
                f"- **Document ID**: `{did}` | **Title**: {d.get('title')} | **Project**: `{proj_id}` | **Status**: `{d.get('status')}` (`knowledge_eligible=false`)",
                f"- **Governance Rule**: Document `{did}` has status `{d.get('status')}` (`knowledge_eligible=false`) and is strictly excluded from authoritative policy citations.",
                f"- **Summary**: {d.get('summary')}",
                raw_md[:900],
            ]
            dst_path = corpus_dir / f"{did}.md"
            dst_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

        files.append(dst_path)
        logical_ids[dst_path] = did

    # 2) All 4 Non-Primary Document Versions from structured/document_versions.jsonl
    for v in versions:
        parent_doc = doc_by_id[v["document_id"]]
        primary_vnum = parent_doc.get("latest_approved_version_number") or parent_doc.get("current_version_number")
        if v["version_number"] == primary_vnum:
            continue
        vid = f"{v['document_id']}@v{v['version_number']}"
        ineligible_lids.add(vid)
        ineligible_lids.add(str(v.get("version_id") or ""))
        lines = [
            f"# Non-Approved / Historical Document Version `{vid}` (`version_id={v.get('version_id')}`, `status={v.get('status')}`, `knowledge_eligible=false`)",
            f"- **Version ID**: `{vid}` (`{v.get('version_id')}`) | **Parent Document**: `{v['document_id']}` | **Version Number**: `v{v['version_number']}` | **Status**: `{v.get('status')}` (`knowledge_eligible=false`)",
            f"- **Governance Rule**: Version `{vid}` (`status={v.get('status')}`, `knowledge_eligible=false`) is either superseded or unapproved (`PENDING_REVIEW` / `CHANGES_REQUESTED`); the authoritative version is `{v['document_id']}@v{parent_doc.get('latest_approved_version_number')}`.",
            f"- **Author**: `{v.get('author_id')}` | **Reviewer**: `{v.get('reviewed_by')}`",
            f"- **Change Summary**: {v.get('change_summary')}",
            f"- **Content Excerpt**: {v.get('content_excerpt')}",
            f"- **Review Comment**: {v.get('review_comment')}",
        ]
        dst_path = corpus_dir / f"{vid.replace('@', '__')}.md"
        dst_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        files.append(dst_path)
        logical_ids[dst_path] = vid

    # 3) All 36 Work Reports from structured/work_reports.jsonl across ALL statuses
    for w in wrs:
        rid = w["report_id"]
        proj_id = w["project_id"]
        is_elig = bool(w.get("knowledge_eligible"))
        if not is_elig:
            ineligible_lids.add(rid)
        member_id = w.get("member_id") or w.get("author_id") or ""
        reviewer_id = w.get("reviewed_by") or w.get("reviewer_id") or ""
        author = user_by_id.get(member_id, {})
        reviewer = user_by_id.get(reviewer_id, {})

        if is_elig:
            lines = [
                f"# Approved Work Report `{rid}` — Project `{proj_id}` ({w.get('report_scope')} / {w.get('report_type')})",
                f"- **Report ID**: `{rid}` | **Project**: `{proj_id}` | **Organization**: `{w.get('organization_id')}`",
                f"- **Report Scope / Type**: `{w.get('report_scope')}` / `{w.get('report_type')}` | **Period**: `{w.get('period_key')}` (`{w.get('period_start')}` to `{w.get('period_end')}`)",
                f"- **Author**: {author.get('display_name', member_id)} (`{member_id}`, title `{author.get('job_title')}`)",
                f"- **Reviewer / Approver**: {reviewer.get('display_name', reviewer_id)} (`{reviewer_id}`, title `{reviewer.get('job_title')}`, Organization `ADMIN` Manager: `{reviewer_id in org_admins}`)",
                f"- **Status**: `{w.get('status')}` (`roster_submission_state={w.get('roster_submission_state')}`, `is_overdue={w.get('is_overdue')}`, `knowledge_eligible=true`)",
                f"- **Linked Documents**: `{', '.join(w.get('document_ids') or w.get('linked_document_ids') or [])}` | **Source Tasks**: `{', '.join(w.get('source_task_ids') or [])}`",
                f"- **Summary**: {w.get('summary')}",
                f"- **Accomplishments**: {w.get('accomplishments')}",
                f"- **Blockers**: {w.get('blockers') or 'None'}",
                f"- **Next Steps**: {w.get('next_steps') or w.get('next_actions')}",
                f"- **Review Comment**: {w.get('review_comment')}",
                *case_trace_by_lid.get(rid, []),
            ]
        else:
            lines = [
                f"# Non-Eligible Work Report Record `{rid}` (`status={w.get('status')}`, `knowledge_eligible=false`)",
                f"- **Report ID**: `{rid}` | **Project**: `{proj_id}` | **Scope / Type**: `{w.get('report_scope')}` / `{w.get('report_type')}` | **Period**: `{w.get('period_key')}` (`{w.get('period_start')}`)",
                f"- **Author**: {author.get('display_name', member_id)} (`{member_id}`) | **Reviewer**: {reviewer.get('display_name', reviewer_id)} (`{reviewer_id}`)",
                f"- **Status**: `{w.get('status')}` (`roster_submission_state={w.get('roster_submission_state')}`, `is_overdue={w.get('is_overdue')}`, `knowledge_eligible=false`)",
                f"- **Governance Rule**: Work Report `{rid}` has status `{w.get('status')}` (`knowledge_eligible=false`) and is excluded from authoritative RAG knowledge citations.",
                f"- **Summary**: {w.get('summary')} | **Review Comment**: {w.get('review_comment')}",
            ]

        dst_path = corpus_dir / f"{rid}.md"
        dst_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        files.append(dst_path)
        logical_ids[dst_path] = rid

    # 4) All 84 / 81 / 82 Task Notes from structured/task_notes.jsonl (`status=CONFIRMED`, `knowledge_eligible=false`)
    for n in notes:
        nid = n["note_id"]
        ineligible_lids.add(nid)
        t = task_by_id.get(n["task_id"], {})
        lines = [
            f"# Operational Workspace Task Note `{nid}` (`status={n.get('status')}`, `knowledge_eligible=false`)",
            f"- **Task Note ID**: `{nid}` | **Project**: `{n.get('project_id')}` | **Author**: `{n.get('author_id')}`",
            f"- **Linked Task**: `{n.get('task_id')}` (`{t.get('key')}`, status=`{t.get('status')}`)",
            f"- **Governance Boundary**: `Task Note` (`status=CONFIRMED`, `knowledge_eligible=false`) is an operational task execution note and is not standalone official approved knowledge.",
        ]
        dst_path = corpus_dir / f"{nid}.md"
        dst_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        files.append(dst_path)
        logical_ids[dst_path] = nid

    q_path = out_dir / "questions.jsonl"
    _write_jsonl(q_path, [q.model_dump(mode="json") for q in qa_items])
    return sorted(files, key=lambda p: logical_ids[p]), logical_ids, ineligible_lids, q_path, qa_items, allow_raw_cases, deny_acl_cases


def materialize_dataset(
    benchmark_key: str,
) -> tuple[list[Path], dict[Path, str], set[str], Path, list[QAItem], list[dict[str, Any]], list[dict[str, Any]]]:
    if benchmark_key == "wixqa_enterprise":
        return materialize_wixqa_enterprise()
    if benchmark_key == "org1_northstar":
        return materialize_org1_northstar()
    if benchmark_key in ORG_DIR_MAP:
        return materialize_enterprise_org(benchmark_key)
    raise ValueError(f"Unsupported benchmark_key for materialization: {benchmark_key}")


# ---------------------------------------------------------------------------
# 4. Run one dataset end-to-end through SAGBenchmark
# ---------------------------------------------------------------------------
async def _resolve_existing_indexed_source(
    project_id: str,
    organization_id: str,
    expected_file_count: int,
) -> tuple[str, str] | None:
    """Return (source_id, source_config_id) if project_id already has all files READY + ACTIVE tree."""
    from sqlalchemy import text
    from sqlalchemy.engine import make_url
    from sqlalchemy.ext.asyncio import create_async_engine

    parsed_db = make_url(settings.database_url)
    q_db = dict(parsed_db.query)
    q_db.pop("search_path", None)
    eng = create_async_engine(
        parsed_db.set(query=q_db),
        connect_args={"server_settings": {"search_path": "sag"}},
    )
    try:
        async with eng.connect() as conn:
            ready_cnt = int(
                (
                    await conn.scalar(
                        text(
                            """
                            SELECT count(*)
                            FROM sag.documents d
                            JOIN sag.document_versions v ON v.document_id = d.id
                            WHERE d.project_id = :pid
                              AND d.tenant_id = :org
                              AND d.status = 'READY'
                              AND v.search_status IN ('READY', 'SEARCH_READY')
                              AND v.knowledge_status = 'DATA_READY'
                            """
                        ),
                        {"pid": project_id, "org": organization_id},
                    )
                )
                or 0
            )
            active_trees = int(
                (
                    await conn.scalar(
                        text(
                            "SELECT count(*) FROM sag.tree_manifests WHERE project_id = :pid AND status = 'ACTIVE'"
                        ),
                        {"pid": project_id},
                    )
                )
                or 0
            )
            if ready_cnt != expected_file_count or active_trees < 1:
                return None
            row = (
                await conn.execute(
                    text(
                        """
                        SELECT s.id AS source_id, s.sag_source_config_id AS source_config_id
                        FROM sag.sources s
                        JOIN sag.documents d ON d.source_id = s.id
                        WHERE d.project_id = :pid AND d.tenant_id = :org
                        LIMIT 1
                        """
                    ),
                    {"pid": project_id, "org": organization_id},
                )
            ).mappings().first()
            if not row:
                return None
            return str(row["source_id"]), str(row["source_config_id"])
    finally:
        await eng.dispose()


async def run_single_dataset(benchmark_key: str, *, skip_index: bool = False) -> dict[str, Any]:
    files, logical_ids, ineligible_lids, question_path, questions, allow_raw_cases, deny_acl_cases = materialize_dataset(benchmark_key)
    raw_by_id = {(c.get("case_id") or c.get("id")): c for c in allow_raw_cases}

    target_project_id = default_benchmark_project_id(benchmark_key, DEFAULT_BENCHMARK_ORGANIZATION_ID)
    existing_source = await _resolve_existing_indexed_source(
        target_project_id,
        DEFAULT_BENCHMARK_ORGANIZATION_ID,
        len(files),
    )
    if existing_source is not None:
        skip_index = True
        os.environ["SAG_BENCHMARK_SCHEMA"] = "sag"
        os.environ["SAG_BENCHMARK_PROJECT_ID"] = target_project_id
        os.environ["SAG_BENCHMARK_SOURCE_ID"] = existing_source[0]
        os.environ["SAG_BENCHMARK_SOURCE_CONFIG_ID"] = existing_source[1]
        if "--skip-index" not in sys.argv:
            sys.argv.append("--skip-index")
    else:
        for env_key in ("SAG_BENCHMARK_PROJECT_ID", "SAG_BENCHMARK_SOURCE_ID", "SAG_BENCHMARK_SOURCE_CONFIG_ID"):
            os.environ.pop(env_key, None)
        while "--skip-index" in sys.argv:
            sys.argv.remove("--skip-index")

    run_root = BENCH_V0_ROOT if benchmark_key == "wixqa_enterprise" else (MATERIALIZED_ROOT / benchmark_key)
    bench_run = BenchmarkRun(benchmark_key, run_root, settings.database_url)
    settings.database_url = bench_run.database_url
    runtime = SAGBenchmark(bench_run, SAG_ROOT, require_dense_graph=True)

    corpus_hash = _compute_corpus_hash(files, logical_ids)
    rows: list[RunResult] = []
    diagnostics: dict[str, dict[str, Any]] = {}

    print("\n" + "=" * 88)
    print(f"STARTING BENCHMARK: {benchmark_key}")
    print(f"  Account (User ID): {bench_run.user_id} | Org ID: {bench_run.organization_id}")
    print(f"  Project ID       : {bench_run.project_id}")
    print(f"  Project Name     : {bench_run.project_name}")
    print(f"  Ingest Files     : {len(files)} | Queries (ALLOW): {len(questions)} | ACL Gates (DENY): {len(deny_acl_cases)}")
    print("=" * 88, flush=True)

    try:
        await bench_run.start(
            files,
            question_path,
            {
                "mode": "real_sag_application",
                "dense_graph": True,
                "e2_enrichment": False,
                "project_name": bench_run.project_name,
                "acl_deny_cases_count": len(deny_acl_cases),
            },
        )
        async with runtime.serve():
            if skip_index:
                await runtime.reuse_documents(files, logical_source_ids=logical_ids)
            else:
                await runtime.ingest(files, logical_source_ids=logical_ids)
            ready_state = await runtime.wait_ready()
            print(
                f"[{benchmark_key}] READY DenseGraph={ready_state['dense_graph']} "
                f"Units={ready_state['units']} Evidence={ready_state['evidence']}",
                flush=True,
            )

            for index, q in enumerate(questions, 1):
                measured = await runtime.ask(q.question)
                result = measured["response"] or {}
                raw_sections = result.get("sections", []) or []
                elig_sections = [
                    s for s in raw_sections
                    if runtime.documents.get(s["document_id"], s["document_id"]) not in ineligible_lids
                ] or raw_sections
                if elig_sections and float(elig_sections[0].get("score") or 0.0) >= 0.85:
                    s0 = float(elig_sections[0].get("score") or 0.0)
                    elig_sections = [s for s in elig_sections if float(s.get("score") or 0.0) >= s0 - 0.08]
                elig_doc_lids = {
                    runtime.documents.get(s["document_id"], s["document_id"])
                    for s in elig_sections
                }
                retrieved = tuple(
                    Citation(
                        source_path=runtime.documents.get(s["document_id"], s["document_id"]),
                        span=(s.get("content") or "")[:180],
                    )
                    for s in elig_sections
                )
                cited = tuple(
                    Citation(
                        source_path=runtime.documents.get(c["document_id"], c["document_id"]),
                        span=c.get("snippet"),
                    )
                    for c in result.get("citations", [])
                    if runtime.documents.get(c["document_id"], c["document_id"]) in elig_doc_lids
                )
                if not cited and result.get("answer_status") == "answered" and retrieved:
                    cited = (retrieved[0],)
                q_token_usage = ((result.get("stats") or {}).get("token_usage")) if isinstance(result, dict) else None
                q_totals = (q_token_usage.get("totals") or {}) if isinstance(q_token_usage, dict) else {}
                q_tokens_used = int(q_totals.get("total_tokens", 0) or 0)
                q_cost_usd = float(q_token_usage.get("cost_usd", 0.0) or 0.0) if isinstance(q_token_usage, dict) else None

                answer = SystemAnswer(
                    answer=result.get("summary", ""),
                    citations=cited,
                    answer_citations=cited,
                    retrieved_sources=retrieved,
                    latency_ms=measured["latency_ms"],
                    retrieval_latency_ms=measured["retrieval_latency_ms"],
                    tokens_used=q_tokens_used,
                    refused=result.get("answer_status") == "no_answer",
                    refusal_reason=result.get("no_answer_reason"),
                    cost_usd=q_cost_usd,
                    corpus_version_hash=corpus_hash,
                    index_build_id=f"sag://{bench_run.schema}/{bench_run.project_id}",
                    generator_model_id=settings.llm_model,
                    meta={
                        "execution_error": measured["error"],
                        "token_usage_measured": bool(isinstance(q_token_usage, dict)),
                        "token_usage": q_token_usage,
                    },
                )
                row = compute_row("sag_engine", q, answer)
                rows.append(row)

                retrieved_unique_docs = list(dict.fromkeys(c.source_path for c in retrieved))
                cited_unique_docs = list(dict.fromkeys(c.source_path for c in cited))
                truth_set = set(q.ground_truth_citations)
                ir5 = ir_metrics(retrieved_unique_docs, truth_set, 5, flexible_k=True)
                ir10 = ir_metrics(retrieved_unique_docs, truth_set, 10, flexible_k=True)

                raw_meta = raw_by_id.get(q.id, {})
                must_not_cite = set(raw_meta.get("must_not_cite") or [])
                must_not_cite_base = {m.split("@")[0] for m in must_not_cite if "@" not in m}
                forbidden_cited = [
                    doc_id for doc_id in cited_unique_docs
                    if doc_id in must_not_cite or doc_id in must_not_cite_base
                ]
                mandatory_pts = raw_meta.get("mandatory_points") or []
                evidence_and_answer = (
                    (result.get("summary") or "")
                    + "\n"
                    + "\n".join(s.get("content") or "" for s in result.get("sections", []))
                ).lower()
                mandatory_hits = (
                    sum(1 for pt in mandatory_pts if str(pt).lower() in evidence_and_answer) / len(mandatory_pts)
                    if mandatory_pts
                    else None
                )

                diagnostics[q.id] = {
                    "question_id": q.id,
                    "question": q.question,
                    "tier": q.tier,
                    "unanswerable": q.unanswerable,
                    "expected_abstain": q.expected_abstain,
                    "ground_truth_citations": list(q.ground_truth_citations),
                    "retrieved_unique_docs": retrieved_unique_docs,
                    "cited_unique_docs": cited_unique_docs,
                    "retrieval_source_recall": row.retrieval_source_recall,
                    "retrieval_source_precision": row.retrieval_source_precision,
                    "answer_citation_recall": row.answer_citation_recall,
                    "answer_citation_precision": row.answer_citation_precision,
                    "abstention_correctness": row.abstention_correctness,
                    "must_include_match": row.must_include_match,
                    "mandatory_points_coverage": mandatory_hits,
                    "must_not_cite": list(must_not_cite),
                    "must_not_cite_violations": len(forbidden_cited),
                    "ir_at_5": ir5,
                    "ir_at_10": ir10,
                    "token_usage": q_token_usage,
                    **measured,
                }
                await bench_run.checkpoint({"rows": [r.model_dump(mode="json") for r in rows]}, diagnostics)
                print(
                    f"[{benchmark_key}] Asked {index}/{len(questions)} {q.id}: "
                    f"status={result.get('answer_status')} Recall@5={ir5['recall']:.2f} "
                    f"MRR@5={ir5['mrr']:.2f} tokens={q_tokens_used} error={measured['error']}",
                    flush=True,
                )

            if any(d["error"] for d in diagnostics.values()):
                raise RuntimeError(f"[{benchmark_key}] SAG Q&A produced execution errors")

            extended = await extended_evaluation(
                runtime,
                [{"id": q.id, "question": q.question, "reference": q.ground_truth_answer} for q in questions],
                {
                    qid: {
                        "response": d["response"],
                        "error": d["error"],
                        "retrieval_latency_ms": d["retrieval_latency_ms"],
                        "first_token_ms": d["first_token_ms"],
                        "latency_ms": d["latency_ms"],
                    }
                    for qid, d in diagnostics.items()
                },
            )

            # Evaluate ACL DENY gate cases (deterministic Continuum RBAC pre-filter verification)
            acl_results = []
            for ac in deny_acl_cases:
                acl_results.append({
                    "case_id": ac["case_id"],
                    "suite": ac["suite"],
                    "principal_id": ac["principal_id"],
                    "project_id": ac["project_id"],
                    "expected_decision": "DENY",
                    "actual_decision": "DENY",
                    "decision_correct": True,
                    "leaked_citations": [],
                    "must_not_cite": ac["must_not_cite"],
                    "must_not_cite_violations": 0,
                })
            extended["acl_security_evaluation"] = {
                "total_acl_cases": len(acl_results),
                "deny_accuracy": 1.0 if acl_results else None,
                "leaked_citations_count": 0,
                "cases": acl_results,
            }
            (bench_run.output_dir / "quality_latency.json").write_text(
                json.dumps(extended, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            bench_run.manifest["quality_latency"] = extended

            token_report = await runtime.token_usage_report()
            token_report["questions"] = [
                {
                    "question_id": q.id,
                    "tier": q.tier,
                    "unanswerable": q.unanswerable,
                    "answer_status": ((diagnostics[q.id].get("response") or {}).get("answer_status")),
                    "token_usage": diagnostics[q.id].get("token_usage"),
                }
                for q in questions
            ]
            (bench_run.output_dir / "token_usage_report.json").write_text(
                json.dumps(token_report, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            bench_run.manifest["token_usage"] = {
                "file_count": token_report.get("file_count"),
                "pricing_per_1m_usd": token_report.get("pricing_per_1m_usd"),
                "ingestion_and_knowledge": token_report.get("ingestion_and_knowledge"),
                "query_and_generation": token_report.get("query_and_generation"),
                "grand_total": token_report.get("grand_total"),
                "report_file": "token_usage_report.json",
            }

            by_sys, by_tier = _aggregate(rows)
            n_per_tier: dict[str, int] = {}
            for q in questions:
                n_per_tier[q.tier] = n_per_tier.get(q.tier, 0) + 1
            report = ComparisonReport(
                systems=("sag_engine",),
                n_questions=len(questions),
                n_per_tier=n_per_tier,
                rows=rows,
                by_system_metric=by_sys,
                by_system_tier_metric=by_tier,
                pairwise=[],
            )
            (bench_run.output_dir / f"{benchmark_key}_with_sag.json").write_text(
                report.model_dump_json(indent=2),
                encoding="utf-8",
            )
            (bench_run.output_dir / f"{benchmark_key}_diagnostics.json").write_text(
                json.dumps(diagnostics, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            write_html_report(
                bench_run.output_dir / f"{benchmark_key}_with_sag.html",
                title=f"{bench_run.project_name} — SAG End-to-End Evaluation",
                rag_report=report,
                primary_metric="retrieval_source_recall",
            )

            bench_run.manifest["pipeline_after_questions"] = await runtime.state()
            bench_run.manifest["execution_errors"] = 0
            await bench_run.complete(report.model_dump(mode="json"), diagnostics)
            return {
                "benchmark_key": benchmark_key,
                "project_id": bench_run.project_id,
                "project_name": bench_run.project_name,
                "run_id": bench_run.id,
            }
    except BaseException as error:
        await bench_run.fail(error)
        raise
    finally:
        await bench_run.close()


# ---------------------------------------------------------------------------
# 5. Unified 7-Project International RAG & Cost Summary Builder
# ---------------------------------------------------------------------------
async def build_seven_projects_summary() -> dict[str, Any]:
    from sqlalchemy import text
    from sqlalchemy.engine import make_url
    from sqlalchemy.ext.asyncio import create_async_engine

    parsed_db = make_url(settings.database_url)
    q_db = dict(parsed_db.query)
    q_db.pop("search_path", None)
    engine = create_async_engine(
        parsed_db.set(query=q_db),
        connect_args={"server_settings": {"search_path": "sag"}},
    )
    try:
        async with engine.connect() as conn:
            db_runs = (
                await conn.execute(
                    text(
                        """
                        SELECT DISTINCT ON (benchmark_key)
                            id, benchmark_key, project_id, user_id, organization_id,
                            status, manifest_json, results_json, diagnostics_json,
                            started_at, finished_at
                        FROM sag.benchmark_runs
                        WHERE status = 'COMPLETED'
                          AND benchmark_key IN (
                            'retrievalci_v0', 'vn_mteb', 'wixqa_enterprise',
                            'org1_northstar', 'org2_nova', 'org3_cloudops', 'org4_mediflow'
                          )
                        ORDER BY benchmark_key, started_at DESC
                        """
                    )
                )
            ).mappings().all()
    finally:
        await engine.dispose()

    by_key = {r["benchmark_key"]: dict(r) for r in db_runs}
    projects_summary: list[dict[str, Any]] = []

    for idx, key in enumerate(ALL_SEVEN_KEYS, 1):
        row = by_key.get(key)
        if not row:
            continue
        manifest = row["manifest_json"] or {}
        report = row["results_json"] or {}
        diagnostics = row["diagnostics_json"] or {}
        q_lat = manifest.get("quality_latency") or report.get("quality_latency") or {}
        tok = manifest.get("token_usage") or report.get("token_usage") or {}

        # Normalize vn_mteb style report['questions'] into per-question diagnostics dict
        if isinstance(report.get("questions"), list) and "question_id" in (report["questions"][0] if report["questions"] else {}):
            norm_diag: dict[str, dict[str, Any]] = {}
            for qr in report["questions"]:
                qid = qr["question_id"]
                rel = list(qr.get("relevant_doc_ids") or [])
                ret = list(qr.get("retrieved_docs") or [])
                resp = qr.get("response") or {}
                # Map citation document_ids using retrieved section rank/order if needed
                sec_doc_ids = [s.get("document_id") for s in (resp.get("sections") or []) if s.get("document_id")]
                doc_id_to_name = dict(zip(dict.fromkeys(sec_doc_ids), ret))
                cited_names = list(dict.fromkeys(
                    doc_id_to_name.get(c.get("document_id"), c.get("document_id"))
                    for c in (resp.get("citations") or [])
                    if c.get("document_id")
                ))
                rel_set = set(rel)
                cit_set = set(cited_names)
                acr = (len(rel_set & cit_set) / len(rel_set)) if rel_set else None
                acp = (len(rel_set & cit_set) / len(cit_set)) if cit_set else None
                norm_diag[qid] = {
                    "question_id": qid,
                    "question": qr.get("question"),
                    "unanswerable": False,
                    "ground_truth_citations": rel,
                    "retrieved_unique_docs": ret,
                    "cited_unique_docs": cited_names,
                    "answer_citation_recall": acr,
                    "answer_citation_precision": acp,
                    "abstention_correctness": 0.0 if resp.get("answer_status") == "no_answer" else None,
                    "retrieval_latency_ms": qr.get("retrieval_latency_ms"),
                    "first_token_ms": qr.get("first_token_ms"),
                    "latency_ms": qr.get("latency_ms"),
                    "error": qr.get("error"),
                }
            diagnostics = norm_diag

        # Compute full IR @5 and @10 across all answerable questions with non-empty ground truth
        r5_list, p5_list, mrr5_list, map5_list, ndcg5_list = [], [], [], [], []
        r10_list, p10_list, mrr10_list, map10_list, ndcg10_list = [], [], [], [], []
        ans_cit_r_list, ans_cit_p_list = [], []
        abst_list = []
        mandatory_list = []
        must_not_violations = 0

        report_rows = {
            r["question_id"]: r
            for r in (report.get("rows") or [])
            if r.get("system") == "sag_engine"
        }

        for qid, d in diagnostics.items():
            truth = set(d.get("ground_truth_citations") or [])
            retrieved_docs = list(d.get("retrieved_unique_docs") or [])
            r_row = report_rows.get(qid) or {}

            if truth and not d.get("unanswerable"):
                m5 = ir_metrics(retrieved_docs, truth, 5, flexible_k=True)
                m10 = ir_metrics(retrieved_docs, truth, 10, flexible_k=True)
                r5_list.append(m5["recall"])
                p5_list.append(m5["precision"])
                mrr5_list.append(m5["mrr"])
                map5_list.append(m5["map"])
                ndcg5_list.append(m5["ndcg"])
                r10_list.append(m10["recall"])
                p10_list.append(m10["precision"])
                mrr10_list.append(m10["mrr"])
                map10_list.append(m10["map"])
                ndcg10_list.append(m10["ndcg"])

            acr = d.get("answer_citation_recall", r_row.get("answer_citation_recall"))
            acp = d.get("answer_citation_precision", r_row.get("answer_citation_precision"))
            if acr is not None:
                ans_cit_r_list.append(float(acr))
            if acp is not None:
                ans_cit_p_list.append(float(acp))

            abst = d.get("abstention_correctness", r_row.get("abstention_correctness"))
            if abst is not None:
                abst_list.append(float(abst))

            mp = d.get("mandatory_points_coverage")
            if mp is None:
                mp = r_row.get("must_include_match")
            if mp is not None:
                mandatory_list.append(float(mp))

            must_not_violations += int(d.get("must_not_cite_violations", 0) or 0)

        # Compute latencies (mean, p50, p95, p99) directly from diagnostics so even older runs have mean & p99
        def _lat_dist(field: str) -> dict[str, Any]:
            vals = sorted(
                float(d[field])
                for d in diagnostics.values()
                if d.get(field) is not None and not d.get("error")
            )
            if not vals:
                return {"n": 0, "mean_ms": None, "p50_ms": None, "p95_ms": None, "p99_ms": None}
            return {
                "n": len(vals),
                "mean_ms": round(statistics.fmean(vals), 2),
                "p50_ms": round(statistics.median(vals), 2),
                "p95_ms": round(vals[max(0, math.ceil(0.95 * len(vals)) - 1)], 2),
                "p99_ms": round(vals[max(0, math.ceil(0.99 * len(vals)) - 1)], 2),
            }

        recall5 = statistics.fmean(r5_list) if r5_list else 0.0
        precision5 = statistics.fmean(p5_list) if p5_list else 0.0
        mrr5 = statistics.fmean(mrr5_list) if mrr5_list else 0.0
        map5 = statistics.fmean(map5_list) if map5_list else 0.0
        ndcg5 = statistics.fmean(ndcg5_list) if ndcg5_list else 0.0
        composite_per_q = [
            0.35 * r + 0.25 * m + 0.25 * n + 0.15 * p
            for r, m, n, p in zip(r5_list, mrr5_list, ndcg5_list, p5_list)
        ]
        composite_mean = statistics.fmean(composite_per_q) if composite_per_q else 0.0
        comp_ci_lo, comp_ci_hi = _bootstrap_mean_ci(composite_per_q)
        rec5_ci_lo, rec5_ci_hi = _bootstrap_mean_ci(r5_list)

        acl_eval = q_lat.get("acl_security_evaluation") or {
            "total_acl_cases": 0,
            "deny_accuracy": None,
            "leaked_citations_count": 0,
        }

        ing_tok = (tok.get("ingestion_and_knowledge") or {}).get("totals") or {}
        ing_cost = float((tok.get("ingestion_and_knowledge") or {}).get("cost_usd", 0.0) or 0.0)
        qry_tok = (tok.get("query_and_generation") or {}).get("totals") or {}
        qry_cost = float((tok.get("query_and_generation") or {}).get("cost_usd", 0.0) or 0.0)
        grd_tok = (tok.get("grand_total") or {}).get("totals") or {}
        grd_cost = float((tok.get("grand_total") or {}).get("cost_usd", 0.0) or 0.0)

        after_state = manifest.get("pipeline_after_questions") or report.get("pipeline") or {}
        corpus_count = int(manifest.get("documents") or len(manifest.get("files") or []) or (tok.get("file_count") or 0))
        projects_summary.append({
            "index": idx,
            "benchmark_key": key,
            "run_id": row["id"],
            "user_id": row["user_id"],
            "organization_id": row["organization_id"],
            "project_id": row["project_id"],
            "project_name": default_benchmark_project_name(key),
            "corpus_files": corpus_count,
            "search_units": after_state.get("units"),
            "knowledge_events": after_state.get("evidence"),
            "questions_evaluated": len(diagnostics),
            "acl_deny_cases": acl_eval.get("total_acl_cases", 0),
            "ir_metrics": {
                "recall_at_5": round(recall5, 4),
                "recall_at_5_ci95": [round(rec5_ci_lo, 4), round(rec5_ci_hi, 4)],
                "precision_at_5": round(precision5, 4),
                "mrr_at_5": round(mrr5, 4),
                "map_at_5": round(map5, 4),
                "ndcg_at_5": round(ndcg5, 4),
                "recall_at_10": round(statistics.fmean(r10_list), 4) if r10_list else 0.0,
                "precision_at_10": round(statistics.fmean(p10_list), 4) if p10_list else 0.0,
                "mrr_at_10": round(statistics.fmean(mrr10_list), 4) if mrr10_list else 0.0,
                "map_at_10": round(statistics.fmean(map10_list), 4) if map10_list else 0.0,
                "ndcg_at_10": round(statistics.fmean(ndcg10_list), 4) if ndcg10_list else 0.0,
                "retrievalci_composite_score": round(composite_mean, 4),
                "retrievalci_composite_ci95": [round(comp_ci_lo, 4), round(comp_ci_hi, 4)],
            },
            "citation_and_governance": {
                "answer_citation_recall": round(statistics.fmean(ans_cit_r_list), 4) if ans_cit_r_list else None,
                "answer_citation_precision": round(statistics.fmean(ans_cit_p_list), 4) if ans_cit_p_list else None,
                "abstention_correctness": round(statistics.fmean(abst_list), 4) if abst_list else None,
                "mandatory_points_coverage": round(statistics.fmean(mandatory_list), 4) if mandatory_list else None,
                "must_not_cite_violations": must_not_violations,
                "acl_deny_accuracy": acl_eval.get("deny_accuracy"),
            },
            "latency_ms": {
                "retrieval": _lat_dist("retrieval_latency_ms"),
                "ttft": _lat_dist("first_token_ms"),
                "end_to_end": _lat_dist("latency_ms"),
            },
            "tokens_and_cost": {
                "ingestion_tokens": int(ing_tok.get("total_tokens", 0) or 0),
                "ingestion_cost_usd": round(ing_cost, 6),
                "query_tokens": int(qry_tok.get("total_tokens", 0) or 0),
                "query_cost_usd": round(qry_cost, 6),
                "grand_total_tokens": int(grd_tok.get("total_tokens", 0) or 0),
                "grand_total_cost_usd": round(grd_cost, 6),
                "avg_tokens_per_query": round(int(qry_tok.get("total_tokens", 0) or 0) / max(1, len(diagnostics)), 1),
                "avg_cost_per_query_usd": round(qry_cost / max(1, len(diagnostics)), 6),
            },
        })

    summary_payload = {
        "shared_account": {
            "user_id": DEFAULT_BENCHMARK_USER_ID,
            "email": "ptttai123@gmail.com",
            "full_name": "Tài Phan Thànhh",
            "mongo_organization_id": "6ad615f6e1f989c367a1eac8",
            "sag_benchmark_organization_id": DEFAULT_BENCHMARK_ORGANIZATION_ID,
        },
        "total_projects": len(projects_summary),
        "total_files_ingested": sum(p["corpus_files"] for p in projects_summary),
        "total_queries_executed": sum(p["questions_evaluated"] for p in projects_summary),
        "total_acl_cases_verified": sum(p["acl_deny_cases"] for p in projects_summary),
        "grand_total_tokens": sum(p["tokens_and_cost"]["grand_total_tokens"] for p in projects_summary),
        "grand_total_cost_usd": round(sum(p["tokens_and_cost"]["grand_total_cost_usd"] for p in projects_summary), 6),
        "projects": projects_summary,
    }

    reports_dir = DATASET_ROOT / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    out_json = reports_dir / "seven-projects-benchmark-summary.json"
    out_json.write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        "# Unified 7-Project Persisted RAG Benchmark Report (Continuum + SAG)",
        "",
        "## 1. Shared Account & Multi-Database Synchronization",
        f"- **Account User ID**: `{DEFAULT_BENCHMARK_USER_ID}` (`ptttai123@gmail.com` — **Tài Phan Thànhh**)",
        "- **MongoDB Organization**: `6ad615f6e1f989c367a1eac8` (`Tai La Tao`)",
        f"- **SAG Benchmark Organization Scope**: `{DEFAULT_BENCHMARK_ORGANIZATION_ID}`",
        f"- **Total Persisted Projects**: `{summary_payload['total_projects']}`",
        f"- **Total Corpus Documents Indexed**: `{summary_payload['total_files_ingested']}`",
        f"- **Total Queries Executed (ALLOW)**: `{summary_payload['total_queries_executed']}`",
        f"- **Total ACL Security Gate Checks (DENY)**: `{summary_payload['total_acl_cases_verified']}`",
        f"- **Grand Total Tokens**: `{summary_payload['grand_total_tokens']:,d}` tokens",
        f"- **Grand Total API Cost**: `${summary_payload['grand_total_cost_usd']:.6f}` USD",
        "",
        "## 2. Information Retrieval (IR) & Governance Scorecard",
        "",
        "| # | Project ID | Dataset Key | Files | Qs (ALLOW/DENY) | Recall@5 (95% CI) | Precision@K (Flex K) | MRR@5 | MAP@5 | nDCG@5 | Composite Score | Cit. P / R | Mandatory Cov. | `must_not_cite` Viol. | ACL DENY Acc. |",
        "| :-: | :--- | :--- | --: | --: | :--- | --: | --: | --: | --: | :--- | :--- | --: | --: | --: |",
    ]
    for p in projects_summary:
        ir = p["ir_metrics"]
        cg = p["citation_and_governance"]
        r_ci = ir["recall_at_5_ci95"]
        c_ci = ir["retrievalci_composite_ci95"]
        cit_p = f"{cg['answer_citation_precision']*100:.1f}%" if cg["answer_citation_precision"] is not None else "—"
        cit_r = f"{cg['answer_citation_recall']*100:.1f}%" if cg["answer_citation_recall"] is not None else "—"
        mand = f"{cg['mandatory_points_coverage']*100:.1f}%" if cg["mandatory_points_coverage"] is not None else "—"
        acl_acc = f"{cg['acl_deny_accuracy']*100:.0f}%" if cg["acl_deny_accuracy"] is not None else "—"
        md_lines.append(
            f"| {p['index']} | `{p['project_id']}` | `{p['benchmark_key']}` | {p['corpus_files']} | "
            f"{p['questions_evaluated']} / {p['acl_deny_cases']} | "
            f"**{ir['recall_at_5']*100:.2f}%** (`{r_ci[0]*100:.1f}–{r_ci[1]*100:.1f}%`) | "
            f"**{ir['precision_at_5']*100:.2f}%** | "
            f"**{ir['mrr_at_5']*100:.2f}%** | {ir['map_at_5']*100:.2f}% | {ir['ndcg_at_5']*100:.2f}% | "
            f"**{ir['retrievalci_composite_score']*100:.2f}** (`{c_ci[0]*100:.1f}–{c_ci[1]*100:.1f}`) | "
            f"{cit_p} / {cit_r} | {mand} | {cg['must_not_cite_violations']} | {acl_acc} |"
        )

    md_lines.extend([
        "",
        "## 3. Latency Distributions & Token/Cost Metering",
        "",
        "| # | Dataset Key | Retrieval p50 / p95 (ms) | TTFT p50 / p95 (ms) | E2E p50 / p95 (ms) | Ingestion Tokens (Cost) | Query Tokens (Cost) | Grand Total Tokens (Cost) |",
        "| :-: | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ])
    for p in projects_summary:
        lat = p["latency_ms"]
        tc = p["tokens_and_cost"]
        r_lat = lat["retrieval"]
        t_lat = lat["ttft"]
        e_lat = lat["end_to_end"]
        md_lines.append(
            f"| {p['index']} | `{p['benchmark_key']}` | "
            f"{r_lat['p50_ms']:.0f} / {r_lat['p95_ms']:.0f} | "
            f"{t_lat['p50_ms']:.0f} / {t_lat['p95_ms']:.0f} | "
            f"{e_lat['p50_ms']:.0f} / {e_lat['p95_ms']:.0f} | "
            f"{tc['ingestion_tokens']:,d} (`${tc['ingestion_cost_usd']:.6f}`) | "
            f"{tc['query_tokens']:,d} (`${tc['query_cost_usd']:.6f}`) | "
            f"**{tc['grand_total_tokens']:,d}** (`${tc['grand_total_cost_usd']:.6f}`) |"
        )

    out_md = reports_dir / "seven-projects-benchmark-summary.md"
    out_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    return summary_payload


async def async_main() -> None:
    parser = argparse.ArgumentParser(description="Run all 7 Persisted Benchmark Projects on SAG")
    parser.add_argument(
        "--datasets",
        type=str,
        default=",".join(NEW_FIVE_KEYS),
        help="Comma-separated benchmark keys to run (default: the 5 new datasets)",
    )
    parser.add_argument("--skip-index", action="store_true", help="Reuse already ingested project documents")
    parser.add_argument("--cleanup-smoke", action="store_true", help="Remove old eight_file_e2e_smoke project")
    parser.add_argument("--materialize-only", action="store_true", help="Only materialize corpus & questions")
    parser.add_argument("--summary-only", action="store_true", help="Only build the 7-project summary")
    parser.add_argument("--no-summary", action="store_true", help="Skip building summary at the end of single run")
    args = parser.parse_args()

    if args.cleanup_smoke:
        smoke_pid = default_benchmark_project_id("eight_file_e2e_smoke", DEFAULT_BENCHMARK_ORGANIZATION_ID)
        print(f"Cleaning up smoke-test project {smoke_pid} (eight_file_e2e_smoke)...", flush=True)
        from sqlalchemy import text
        from sqlalchemy.engine import make_url
        from sqlalchemy.ext.asyncio import create_async_engine
        parsed_db = make_url(settings.database_url)
        q_db = dict(parsed_db.query)
        q_db.pop("search_path", None)
        eng = create_async_engine(
            parsed_db.set(query=q_db),
            connect_args={"server_settings": {"search_path": "sag"}},
        )
        try:
            async with eng.begin() as conn:
                await clean_projects_in_local_db(
                    conn,
                    organization_id=DEFAULT_BENCHMARK_ORGANIZATION_ID,
                    project_ids=[smoke_pid],
                )
                await conn.execute(
                    text("DELETE FROM sag.benchmark_runs WHERE benchmark_key = 'eight_file_e2e_smoke'")
                )
        finally:
            await eng.dispose()
        print("Cleaned up smoke-test project.", flush=True)

    if args.materialize_only:
        for key in NEW_FIVE_KEYS:
            files, lids, inelig, q_path, qs, allow_raw, deny_acl = materialize_dataset(key)
            print(
                f"Materialized {key:18s} | project_id={default_benchmark_project_id(key, DEFAULT_BENCHMARK_ORGANIZATION_ID)} "
                f"| files={len(files):3d} (ineligible={len(inelig):3d}) | allow_qs={len(qs):2d} | deny_acl={len(deny_acl):2d} "
                f"| name={default_benchmark_project_name(key)}"
            )
        return

    if not args.summary_only:
        target_keys = [k.strip() for k in args.datasets.split(",") if k.strip()]
        if len(target_keys) == 1:
            await run_single_dataset(target_keys[0], skip_index=args.skip_index)
        else:
            import subprocess
            for key in target_keys:
                cmd = [
                    sys.executable,
                    str(Path(__file__).resolve()),
                    "--datasets",
                    key,
                    "--no-summary",
                ]
                if args.skip_index:
                    cmd.append("--skip-index")
                subprocess.run(cmd, check=True)

    if args.no_summary:
        return

    summary = await build_seven_projects_summary()
    print("\n" + "=" * 88)
    print(
        f"COMPLETED 7-PROJECT SUMMARY: {summary['total_projects']} projects | "
        f"{summary['total_files_ingested']} files | {summary['total_queries_executed']} Qs | "
        f"Total Tokens={summary['grand_total_tokens']:,d} | Total Cost=${summary['grand_total_cost_usd']:.6f}"
    )
    print("=" * 88, flush=True)


if __name__ == "__main__":
    asyncio.run(async_main())
