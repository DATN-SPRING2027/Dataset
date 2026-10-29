# Hai benchmark SAG — dữ liệu và kết quả đã lưu trong PostgreSQL

Account chung: `6acc9a5425f02c9d92a01012`. Bảng kết quả: `sag.benchmark_runs`, `sag.benchmark_runs`.

| Benchmark | Project | Tài liệu | Câu SAG chạy mới | Trạng thái |
|---|---|---:|---:|---|
| retrievalci_v0 | `8bd684646427462756bc2874` | 81 | 50 | COMPLETED |
| vn_mteb | `0d24633a5a21d393af9239c0` | 130 | 50 | COMPLETED |

## retrievalci_v0

- Run ID: `20261029T124344Z-27a384`.
- File report: `D:\DoAnTotnghiep\Dataset\RetrievalCI_Bench_v0_2026\reports\20261029T124344Z-27a384`.
- Recall: 98.61%; precision: 80.93%.
- P50 retrieval: 6111.644199991133 ms.
- Các row provider khác là tham chiếu lịch sử, không chạy lại và không bảo đảm cùng protocol.
- Runtime: `sag_api.main.lifespan (FOUNDATION E0/E1 + full DenseGraph + Leiden tree; E2 enrichment removed)`; transport: `loopback HTTP /api/v1/search/stream; separate client process`.
- Frontend policy: `{"top_k": 5, "load_more_step": 5, "stream_idle_seconds": 45.0, "first_result_seconds": 30.0, "stream_idle_activity": "received data after result, including SSE ping comments"}`.
- E2 enabled: False; policy: `{"capacity": 512, "concurrency": 8, "max_attempts": 3, "poll_seconds": 2.0, "retry_seconds": 30, "max_age_seconds": 86400, "timeout_seconds": 60}`.

### Chất lượng trả lời — judge độc lập

Judge: `None`. Thang 1–5; không phải human accuracy.

| Metric | Mean | Số câu chấm được |
|---|---:|---:|
| relevance | None | 0 |
| faithfulness | None | 0 |

### Latency SAG

| Lượt | Request | Lỗi | Retrieval p50/p95 ms | First validated answer p50/p95 ms | Q&A p50/p95 ms |
|---|---:|---:|---|---|---|
| first_pass | 50 | 0 | 6111.644199991133 / 7127.36279994715 | 11808.784499939065 / 22112.742999917828 | 11743.642800021917 / 22113.2788999239 |
| warm_combined | 0 | 0 | None / None | None / None | None / None |

Bảng latency trên dùng request thành công; JSON giữ cả phân phối tất cả attempts và lỗi. First pass không preload query; physical cold cache chưa xác minh. summary.delta chỉ được gửi sau kiểm chứng citation, nên first_token_ms không phải raw model TTFT.

### Top-5 retrieval so với hosted reference

SAG first-pass full Q&A with Top-5; hosted references historical, latency conditions not matched

| Hệ thống | Recall | Precision | p50 retrieval ms |
|---|---:|---:|---:|
| bedrock_kb | 0.8787037037037037 | 0.7013333333333334 | None |
| vertex_ai_rag | 0.9453703703703703 | 0.5466666666666666 | None |
| azure_ai_search | 0.9092592592592592 | 0.6783333333333332 | None |
| sag_engine_top5 | 0.9861111111111112 | 0.8093333333333333 | 6111.644199991133 |
| openai_file_search | 0.8925925925925925 | 0.534 | None |

Các hàng hosted là lịch sử, không có answer để chấm; thời gian đo/hạ tầng/cache khác SAG. Không kết luận hệ thống nào nhanh hơn từ bảng này.

## vn_mteb

- Run ID: `20261029T125830Z-e6edea`.
- File report: `D:\DoAnTotnghiep\Dataset\VN_MTEB_RAG_Bench_2026\reports\20261029T125830Z-e6edea`.
- Recall@5: 83.00%; nDCG@5: 86.39%.
- Answered: 48/50; execution errors: 0.
- P50 retrieval: 4041.42 ms; P50 Q&A: 9151.30 ms.
- Runtime: `sag_api.main.lifespan (FOUNDATION E0/E1 + full DenseGraph + Leiden tree; E2 enrichment removed)`; transport: `loopback HTTP /api/v1/search/stream; separate client process`.
- Frontend policy: `{"top_k": 5, "load_more_step": 5, "stream_idle_seconds": 45.0, "first_result_seconds": 30.0, "stream_idle_activity": "received data after result, including SSE ping comments"}`.
- E2 enabled: False; policy: `{"capacity": 512, "concurrency": 8, "max_attempts": 3, "poll_seconds": 2.0, "retry_seconds": 30, "max_age_seconds": 86400, "timeout_seconds": 60}`.

### Chất lượng trả lời — judge độc lập

Judge: `None`. Thang 1–5; không phải human accuracy.

| Metric | Mean | Số câu chấm được |
|---|---:|---:|
| relevance | None | 0 |
| faithfulness | None | 0 |

### Latency SAG

| Lượt | Request | Lỗi | Retrieval p50/p95 ms | First validated answer p50/p95 ms | Q&A p50/p95 ms |
|---|---:|---:|---|---|---|
| first_pass | 50 | 0 | 4041.421550035011 / 9251.66320009157 | 9149.91060004104 / 15592.999499989673 | 9151.302800048143 / 15593.46770006232 |
| warm_combined | 0 | 0 | None / None | None / None | None / None |

Bảng latency trên dùng request thành công; JSON giữ cả phân phối tất cả attempts và lỗi. First pass không preload query; physical cold cache chưa xác minh. summary.delta chỉ được gửi sau kiểm chứng citation, nên first_token_ms không phải raw model TTFT.

## Tham chiếu VN quốc tế — khác corpus local

Published/full-dataset references only. Not fresh runs, not the local 130-document fixture; no speed or superiority claims against local SAG results.

Nguồn chính: https://arxiv.org/html/2507.21500v1#A8

| Mô hình | HotpotQA-VN reported retrieval score | Latency |
|---|---:|---|
| Vietnamese_Embedding | 70.07 | Không có số đối chiếu |
| gte-Qwen2-7B-instruct | 67.99 | Không có số đối chiếu |
| multilingual-e5-large | 65.11 | Không có số đối chiếu |
| e5-Mistral-7B-instruct | 64.54 | Không có số đối chiếu |
| bge-m3 | 63.76 | Không có số đối chiếu |
| bge-multilingual-Gemma2 | 29.72 | Không có số đối chiếu |
| LaBSE | 17.0 | Không có số đối chiếu |

Các model legal được nhắc trong README nhưng chưa đủ artifact để đối chiếu tái lập: M3-GN-VN-Mixed, M3-Embedding (bge-m3), multilingual-e5-large, vietnamese-bi-encoder, text-embedding-3.
Không xếp hạng chung điểm SAG local với điểm full dataset công bố; không chạy mock để thay provider thiếu quyền truy cập.

## Kiểm tra lưu trữ và tách scope

- Kết quả file khớp nguyên bản JSONB trong DB; đủ 100 câu SAG chạy mới, không lẫn baseline lịch sử.
- Corpus và câu hỏi khớp SHA-256 trong manifest.
- Hai project/source/collection khác nhau, cùng account đang tồn tại.
- Kiểm tra canonical scope chéo project trả về rỗng; mỗi collection không có point thuộc project khác.
- Đây là scope project SAG; chưa tạo entity Project/membership trong IAM Continuum.
