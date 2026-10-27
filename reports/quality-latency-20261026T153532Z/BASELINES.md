# Baseline quốc tế có sẵn — chờ kết quả SAG mới

SAG run: `20261026T153533Z-bcb5d8` (RUNNING).

Các hàng bên dưới là kết quả lịch sử trong dataset; không phải provider chạy mới, không bảo đảm latency cùng hạ tầng/cache/thời điểm.

Corpus chunk hash khớp hosted manifest: **True**.

| Hệ thống | Recall | Precision | p50 retrieval ms | Answer quality mới |
|---|---:|---:|---:|---|
| bm25_lexical | 0.4768518518518518 | 0.41 | None | Chưa chạy/chưa chấm lại |
| chunk_summary_rag | 0.4583333333333333 | 0.37066666666666664 | None | Chưa chạy/chưa chấm lại |
| dense_rag | 0.48518518518518516 | 0.38833333333333336 | None | Chưa chạy/chưa chấm lại |
| dense_rerank | 0.4824074074074074 | 0.41666666666666663 | None | Chưa chạy/chưa chấm lại |
| hybrid_rrf | 0.4768518518518518 | 0.429 | None | Chưa chạy/chưa chấm lại |
| vertex_ai_rag | 0.9453703703703703 | 0.5466666666666666 | None | Chưa chạy/chưa chấm lại |
| bedrock_kb | 0.8787037037037037 | 0.7013333333333334 | None | Chưa chạy/chưa chấm lại |
| openai_file_search | 0.8925925925925925 | 0.534 | None | Chưa chạy/chưa chấm lại |
| azure_ai_search | 0.9092592592592592 | 0.6783333333333332 | None | Chưa chạy/chưa chấm lại |

## VN-MTEB full-dataset references

Published/full-dataset references only. Not fresh runs, not the local 130-document fixture; no speed or superiority claims against local SAG results.

Nguồn: https://arxiv.org/html/2507.21500v1#A8

| Mô hình | HotpotQA-VN score đã công bố | Latency |
|---|---:|---|
| Vietnamese_Embedding | 70.07 | Không có điều kiện đo tương đương |
| gte-Qwen2-7B-instruct | 67.99 | Không có điều kiện đo tương đương |
| multilingual-e5-large | 65.11 | Không có điều kiện đo tương đương |
| e5-Mistral-7B-instruct | 64.54 | Không có điều kiện đo tương đương |
| bge-m3 | 63.76 | Không có điều kiện đo tương đương |
| bge-multilingual-Gemma2 | 29.72 | Không có điều kiện đo tương đương |
| LaBSE | 17.0 | Không có điều kiện đo tương đương |

Không xếp điểm các hàng này với SAG trên subset 130 docs/50 câu.
