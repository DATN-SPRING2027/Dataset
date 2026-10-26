"""Download and materialize the official VN-MTEB / MMTEB Vietnamese RAG Benchmark suite.

Sources (Hugging Face official GreenNode / MMTEB repositories):
1. `GreenNode/zalo-ai-legal-text-retrieval-vn` (MTEB task: `ZacLegalTextRetrieval`)
   - Official Vietnamese legal article retrieval benchmark with published baselines for
     OpenAI (`OpenAI-embedding-v3`), Microsoft (`me5_large`, `me5_small`), BAAI (`M3-Embedding`),
     GreenNode (`M3-GN-VN-Mixed`), BKAI (`vietnamese-bi-encoder`), and `halong-embedding`.
2. `GreenNode/nano-hotpotqa-vn` (MTEB task: `HotpotQA-VN` / `NanoHotpotQA-VN`, arXiv:2507.21500)
   - Official Vietnamese multi-hop retrieval benchmark (2 supporting documents per query) with
     published baselines for Google (`bge-multilingual-Gemma2`, `LaBSE`), Alibaba (`gte-Qwen2-7B-instruct`,
     `gte-Qwen2-1.5B-instruct`), Microsoft/Mistral (`e5-Mistral-7B-instruct`, `m-e5-large`), and BAAI (`bge-m3`).
"""

from __future__ import annotations

import hashlib
import io
import json
import re
import urllib.request
from collections import defaultdict
from pathlib import Path

import pyarrow.parquet as pq

BENCH_DIR = Path(r"d:\DoAnTotnghiep\Dataset\VN_MTEB_RAG_Bench_2026")
CORPUS_DIR = BENCH_DIR / "corpus"
DATA_DIR = BENCH_DIR / "data"


def _fetch_parquet(repo: str, path: str) -> list[dict]:
    url = f"https://huggingface.co/datasets/{repo}/resolve/main/{path}"
    print(f"Downloading {url} ...")
    req = urllib.request.Request(url, headers={"User-Agent": "VN-MTEB-Bench-Builder/1.0"})
    raw = urllib.request.urlopen(req, timeout=60).read()
    return pq.read_table(io.BytesIO(raw)).to_pylist()


def _safe_doc_filename(prefix: str, raw_id: str) -> str:
    clean = re.sub(r"[^a-zA-Z0-9_-]+", "_", raw_id).strip("_")
    digest = hashlib.md5(raw_id.encode("utf-8")).hexdigest()[:8]
    return f"{prefix}__{clean[:48]}__{digest}.md"


def build_benchmark() -> None:
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------------------
    # Part 1: ZacLegalTextRetrieval (GreenNode/zalo-ai-legal-text-retrieval-vn)
    # -------------------------------------------------------------------------
    zalo_repo = "GreenNode/zalo-ai-legal-text-retrieval-vn"
    zalo_queries_raw = _fetch_parquet(zalo_repo, "queries/test-00000-of-00001.parquet")
    zalo_qrels_raw = _fetch_parquet(zalo_repo, "qrels/test-00000-of-00001.parquet")
    zalo_corpus_raw = _fetch_parquet(zalo_repo, "corpus/test-00000-of-00001.parquet")

    zalo_query_map = {str(r["id"]): str(r["text"]).strip() for r in zalo_queries_raw if r.get("text")}
    zalo_corpus_map = {
        str(r["id"]): (str(r.get("title") or "").strip(), str(r.get("text") or "").strip())
        for r in zalo_corpus_raw
        if r.get("text")
    }
    zalo_qrels: dict[str, list[str]] = defaultdict(list)
    for row in zalo_qrels_raw:
        qid = str(row["query-id"])
        cid = str(row["corpus-id"])
        score = int(row.get("score", 0))
        if score > 0 and qid in zalo_query_map and cid in zalo_corpus_map:
            if cid not in zalo_qrels[qid]:
                zalo_qrels[qid].append(cid)

    # Deterministically select 30 ZaloLegal test queries (sorted by query_id)
    selected_zalo_qids = sorted(zalo_qrels.keys())[:30]
    selected_zalo_cids: set[str] = set()
    decree_prefixes: set[str] = set()
    for qid in selected_zalo_qids:
        for cid in zalo_qrels[qid]:
            selected_zalo_cids.add(cid)
            if "+" in cid:
                decree_prefixes.add(cid.split("+", 1)[0])

    # Add hard-negative sibling articles from the exact same legal decrees (up to 70 total legal docs)
    for cid in sorted(zalo_corpus_map.keys()):
        if len(selected_zalo_cids) >= 70:
            break
        prefix = cid.split("+", 1)[0] if "+" in cid else ""
        if prefix in decree_prefixes and cid not in selected_zalo_cids:
            selected_zalo_cids.add(cid)

    # -------------------------------------------------------------------------
    # Part 2: HotpotQA-VN (GreenNode/nano-hotpotqa-vn)
    # -------------------------------------------------------------------------
    hp_repo = "GreenNode/nano-hotpotqa-vn"
    hp_queries_raw = _fetch_parquet(hp_repo, "queries/test-00000-of-00001.parquet")
    hp_qrels_raw = _fetch_parquet(hp_repo, "qrels/test-00000-of-00001.parquet")
    hp_corpus_raw = _fetch_parquet(hp_repo, "corpus/test-00000-of-00001.parquet")

    hp_query_map = {str(r["id"]): str(r["text"]).strip() for r in hp_queries_raw if r.get("text")}
    hp_corpus_map = {
        str(r["id"]): (str(r.get("title") or "").strip(), str(r.get("text") or "").strip())
        for r in hp_corpus_raw
        if r.get("text")
    }
    hp_qrels: dict[str, list[str]] = defaultdict(list)
    for row in hp_qrels_raw:
        qid = str(row["query-id"])
        cid = str(row["corpus-id"])
        score = int(row.get("score", 0))
        if score > 0 and qid in hp_query_map and cid in hp_corpus_map:
            if cid not in hp_qrels[qid]:
                hp_qrels[qid].append(cid)

    # Deterministically select 20 multi-hop queries where both supporting docs are present
    multi_hop_hp_qids = [qid for qid in sorted(hp_qrels.keys()) if len(hp_qrels[qid]) >= 2]
    selected_hp_qids = multi_hop_hp_qids[:20]
    selected_hp_cids: set[str] = set()
    for qid in selected_hp_qids:
        for cid in hp_qrels[qid]:
            selected_hp_cids.add(cid)

    # Add 20 hard-negative distractor passages from HotpotQA-VN corpus (up to 60 total HotpotQA docs)
    for cid in sorted(hp_corpus_map.keys()):
        if len(selected_hp_cids) >= 60:
            break
        if cid not in selected_hp_cids:
            selected_hp_cids.add(cid)

    # -------------------------------------------------------------------------
    # Write Markdown Corpus & Benchmark Manifest
    # -------------------------------------------------------------------------
    for old_file in CORPUS_DIR.glob("*.md"):
        old_file.unlink()

    cid_to_filename: dict[str, str] = {}
    corpus_records: list[dict] = []

    for cid in sorted(selected_zalo_cids):
        title, text = zalo_corpus_map[cid]
        fname = _safe_doc_filename("zalo_legal", cid)
        cid_to_filename[f"zalo:{cid}"] = fname
        decree_code = cid.split("+", 1)[0].upper() if "+" in cid else cid.upper()
        article_no = cid.split("+", 1)[1] if "+" in cid else ""
        header = f"# Văn bản {decree_code} - {title or f'Điều {article_no}'}\n\n"
        md_content = f"{header}**Mã văn bản pháp quy:** `{decree_code}`  \n**Điều khoản:** `{title}`\n\n{text}\n"
        (CORPUS_DIR / fname).write_text(md_content, encoding="utf-8")
        corpus_records.append(
            {
                "doc_id": fname,
                "original_corpus_id": cid,
                "subset": "ZacLegalTextRetrieval",
                "title": f"{decree_code} - {title}",
            }
        )

    for cid in sorted(selected_hp_cids):
        title, text = hp_corpus_map[cid]
        fname = _safe_doc_filename("hotpot_vn", cid)
        cid_to_filename[f"hp:{cid}"] = fname
        clean_title = title or f"Tài liệu {cid}"
        md_content = f"# {clean_title}\n\n{text}\n"
        (CORPUS_DIR / fname).write_text(md_content, encoding="utf-8")
        corpus_records.append(
            {
                "doc_id": fname,
                "original_corpus_id": cid,
                "subset": "HotpotQA-VN",
                "title": clean_title,
            }
        )

    questions_records: list[dict] = []
    for idx, qid in enumerate(selected_zalo_qids, start=1):
        rel_files = [cid_to_filename[f"zalo:{cid}"] for cid in zalo_qrels[qid]]
        questions_records.append(
            {
                "question_id": f"vn_zalo_{idx:03d}",
                "original_query_id": qid,
                "subset": "ZacLegalTextRetrieval",
                "tier": "single_hop_legal",
                "question": zalo_query_map[qid],
                "relevant_doc_ids": rel_files,
            }
        )

    for idx, qid in enumerate(selected_hp_qids, start=1):
        rel_files = [cid_to_filename[f"hp:{cid}"] for cid in hp_qrels[qid]]
        questions_records.append(
            {
                "question_id": f"vn_hotpot_{idx:03d}",
                "original_query_id": qid,
                "subset": "HotpotQA-VN",
                "tier": "multi_hop",
                "question": hp_query_map[qid],
                "relevant_doc_ids": rel_files,
            }
        )

    (DATA_DIR / "corpus_manifest.json").write_text(
        json.dumps(corpus_records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    with (DATA_DIR / "questions.jsonl").open("w", encoding="utf-8") as f:
        for q in questions_records:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")

    print(
        f"Built VN-MTEB RAG Benchmark at {BENCH_DIR}:\n"
        f"  - Total corpus documents: {len(corpus_records)} "
        f"(ZacLegalTextRetrieval={len(selected_zalo_cids)}, HotpotQA-VN={len(selected_hp_cids)})\n"
        f"  - Total queries: {len(questions_records)} "
        f"(ZacLegalTextRetrieval={len(selected_zalo_qids)}, HotpotQA-VN={len(selected_hp_qids)})"
    )


if __name__ == "__main__":
    build_benchmark()
