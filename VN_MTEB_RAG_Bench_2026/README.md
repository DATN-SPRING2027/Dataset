> **Lưu ý protocol:** Các kết quả và mô tả “Full AI Pipeline” bên dưới là lịch sử của runner cũ, không đại diện cho cấu hình SAG hiện tại. Lượt mới dùng pipeline SAG thật, judge riêng và ba lượt latency; xem `../BENCHMARK_RUNS.md` và `reports/<run_id>/`. Kết quả subset local không so trực tiếp với full leaderboard. Dấu citation không phải điểm grounding độc lập. `bge-multilingual-Gemma2` là checkpoint BAAI dùng backbone Gemma; không phải dịch vụ Google được đo ở đây.

# VN-MTEB / MMTEB Vietnamese RAG Benchmark (2026) — SAG Engine (Full AI Pipeline) vs. Same-Corpus & BigTech Baselines

Bộ dữ liệu đánh giá truy xuất và tổng hợp RAG tiếng Việt chuẩn quốc tế (**VN-MTEB** / **MMTEB**, công bố tại `arXiv:2507.21500` và Hugging Face `GreenNode`) kết hợp 2 tập kiểm thử đại diện cho 2 bài toán cốt lõi của RAG tiếng Việt:

1. **`ZacLegalTextRetrieval`** ([`GreenNode/zalo-ai-legal-text-retrieval-vn`](https://huggingface.co/datasets/GreenNode/zalo-ai-legal-text-retrieval-vn)): Truy xuất văn bản pháp luật Việt Nam (Luật, Nghị định, Thông tư, Điều/Khoản).
2. **`HotpotQA-VN`** ([`GreenNode/nano-hotpotqa-vn`](https://huggingface.co/datasets/GreenNode/nano-hotpotqa-vn)): Truy xuất suy luận đa bước (Multi-hop Reasoning QA) yêu cầu tìm kiếm đồng thời nhiều tài liệu bắc cầu tiếng Việt.

---

## 1. Cấu hình Full AI Pipeline & Kiểm toán Lời gọi AI

Toàn bộ các tầng AI trong kiến trúc **SAG Engine** đã được kích hoạt đầy đủ khi chạy [`scripts/run_vn_mteb_sag.py`](file:///d:/DoAnTotnghiep/Dataset/VN_MTEB_RAG_Bench_2026/scripts/run_vn_mteb_sag.py):

- **AI Stage 1 — Dense Embedding (`Qwen/Qwen3-Embedding-0.6B`, 1024 chiều):** Nhúng đồng thời toàn bộ `SearchUnit` trong Qdrant và `368/368 KnowledgeUnit` trong PostgreSQL để kích hoạt tín hiệu ngữ nghĩa (`semantic` weight = `0.40`) khi xây dựng đồ thị tri thức.
- **AI Stage 2 — Tier E2 LLM Knowledge Extraction (`Qwen/Qwen3-8B`):** Gọi LLM trích xuất thực thể, bí danh, mệnh đề và quan hệ có đối chiếu span nguyên văn (`_align_e2_spans` + `apply_e2`), bổ sung `+109 entities`, `+49 claims`, `+58 relations` vào đồ thị.
- **AI Stage 3 — Knowledge Graph & Universe Routing Tree:** Xây dựng đồ thị liên kết trên `368 KnowledgeUnits` và công bố cây định tuyến phân cấp `Universe Tree` (`rebuild_project_universe_tree` + `acquire_tree_query_snapshot`).
- **AI Stage 4 — End-to-End LLM Answer Synthesis (`Qwen/Qwen3-8B`):** Tổng hợp câu trả lời tiếng Việt có kiểm chứng trích dẫn (`synthesize_search_answer`), đạt **`50/50` (`100.00%`) câu trả lời có gắn trích dẫn hợp lệ `[1]`, `[2]`** (`p50 = 5128.4 ms`).

---

## 2. Kết quả Thực nghiệm (Đối sánh Công bằng Cùng Tập Dữ Liệu + Bảng Xếp Hạng Quốc Tế)

### Bảng 1: Truy xuất Pháp luật Việt Nam — `ZacLegalTextRetrieval` (`n = 30`)

| Hệ thống / Mô hình | Chế độ đánh giá | MAP@5 | MRR@5 | NDCG@5 | Recall@5 | Trung bình (Mean) |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| **SAG Engine (Full AI Pipeline — Sau khi sửa toàn bộ bug)** | **Cùng tập 130 docs** | **97.78** | **97.78** | **98.33** | **100.00** | **98.47** |
| SAG Engine (Trước khi sửa 6 bug logic tiếng Việt) | Cùng tập 130 docs | 96.67 | 96.67 | 96.67 | 96.67 | 96.67 |
| **Pure Dense Baseline (`Qwen3-Embedding-0.6B` Cosine Only)** | **Cùng tập 130 docs** | **94.00** | **94.00** | **95.50** | **100.00** | **95.88** |
| **Pure Sparse Baseline (`BM25 / Lexical Overlap Only`)** | **Cùng tập 130 docs** | **72.89** | **72.89** | **78.88** | **96.67** | **80.33** |
| `M3-GN-VN-Mixed` (GreenNode SOTA VN) | Full Leaderboard | 69.75 | 69.28 | 74.01 | 86.74 | 74.95 |
| `M3-Embedding` (`bge-m3` — BAAI) | Full Leaderboard | 69.34 | 68.96 | 73.70 | 86.68 | 74.67 |
| `multilingual-e5-large` (**Microsoft**) | Full Leaderboard | 60.14 | 59.62 | 64.17 | 76.02 | 64.99 |
| `vietnamese-bi-encoder` (BKAI) | Full Leaderboard | 54.88 | 54.47 | 59.10 | 79.51 | 61.99 |
| **`text-embedding-3`** (**OpenAI**) | Full Leaderboard | 38.68 | 38.80 | 41.53 | 49.94 | 41.74 |

### Bảng 2: Truy xuất Đa bước (Multi-Hop QA) — `HotpotQA-VN` (`n = 20`, `arXiv:2507.21500`)

| Hệ thống / Mô hình | Chế độ đánh giá | NDCG@10 | Recall@5 | Recall@10 | MRR@5 |
| :--- | :--- | ---: | ---: | ---: | ---: |
| **SAG Engine (Full AI Pipeline — Sau khi sửa toàn bộ bug)** | **Cùng tập 130 docs** | **98.85** | **100.00** | **100.00** | **100.00** |
| SAG Engine (Trước khi sửa 6 bug logic tiếng Việt) | Cùng tập 130 docs | 90.33 | 87.50 | 87.50 | 100.00 |
| **Pure Dense Baseline (`Qwen3-Embedding-0.6B` Cosine Only)** | **Cùng tập 130 docs** | **99.09** | **97.50** | **100.00** | **100.00** |
| **Pure Sparse Baseline (`BM25 / Lexical Overlap Only`)** | **Cùng tập 130 docs** | **89.49** | **95.00** | **97.50** | **94.17** |
| `Vietnamese_Embedding` (AITeamVN — 568M) | Full Leaderboard | 70.07 | - | - | - |
| **`gte-Qwen2-7B-instruct`** (**Alibaba Cloud** — 7B) | Full Leaderboard | 67.99 | - | - | - |
| **`multilingual-e5-large`** (**Microsoft** — 560M) | Full Leaderboard | 65.11 | - | - | - |
| **`e5-Mistral-7B-instruct`** (**Microsoft / Mistral** — 7B) | Full Leaderboard | 64.54 | - | - | - |
| **`bge-m3`** (**BAAI** — 568M) | Full Leaderboard | 63.76 | - | - | - |
| **`bge-multilingual-Gemma2`** (**Google** — 9B) | Full Leaderboard | 29.72 | - | - | - |
| **`LaBSE`** (**Google** — 471M) | Full Leaderboard | 17.00 | - | - | - |

### Tổng hợp toàn bộ VN-MTEB (`n = 50` truy vấn, `130` tài liệu, `368` KUs)
- **Recall@5:** `100.00%` (`50/50` truy vấn tìm thấy đầy đủ toàn bộ tài liệu đích trong Top-5, tăng từ `93.00%`)
- **Recall@10:** `100.00%` (`50/50` truy vấn, tăng từ `95.00%`)
- **NDCG@5:** `98.54%` (tăng từ `94.13%`)
- **NDCG@10:** `98.54%` (tăng từ `94.84%`)
- **LLM Answer Synthesis Grounding (`Qwen/Qwen3-8B`):** `100.00%` (`50/50` câu trả lời sinh thành công và gắn trích dẫn chuẩn xác)
