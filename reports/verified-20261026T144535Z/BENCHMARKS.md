# Hai benchmark SAG — dữ liệu và kết quả đã lưu trong PostgreSQL

Account chung: `6acc9a5425f02c9d92a01012`. Bảng kết quả: `sag.benchmark_runs`.

| Benchmark | Project | Tài liệu | Câu SAG chạy mới | Trạng thái |
|---|---|---:|---:|---|
| retrievalci_v0 | `08c89c865e2c481fb5ebbe02` | 81 | 50 | COMPLETED |
| vn_mteb | `9f1dfc0aab484447a0b1e5c1` | 130 | 50 | COMPLETED |

## retrievalci_v0

- Run ID: `20261026T141834Z-3e858c`.
- File report: `D:\DoAnTotnghiep\Dataset\RetrievalCI_Bench_v0_2026\reports\20261026T141834Z-3e858c`.
- Score: 88.01/100; recall: 98.61%; precision: 63.27%; p50 retrieval: 1888.93 ms.
- Mode A retrieve-only: không sinh câu trả lời. Năm câu không có đáp án đều vẫn trả về nguồn (abstention correctness 0/5).
- Hai câu chưa đủ nguồn: qst_0348 và qst_0354. qst_0354 có 8 nguồn đích nhưng top-k chỉ là 5.
- 50 row SAG là lượt chạy mới; 450 row baseline là dữ liệu tham chiếu đã lưu, không gọi lại các provider đó. Cost trong adapter là placeholder, không phải billing.

## vn_mteb

- Run ID: `20261026T142931Z-35460f`.
- File report: `D:\DoAnTotnghiep\Dataset\VN_MTEB_RAG_Bench_2026\reports\20261026T142931Z-35460f`.
- Recall@5: 100.00%; nDCG@10: 98.68%; p50 retrieval warm-cache: 1852.00 ms.
- E2: 19/24; graph: 3905 cạnh; tree published: True.
- Sinh câu trả lời: 50/50 không rỗng; số có dấu trích dẫn: 50/50.
- Dấu trích dẫn không phải đánh giá độ chính xác độc lập; đây là subset local, không phải full leaderboard quốc tế.

## Kiểm tra lưu trữ và tách scope

- Kết quả file khớp nguyên bản JSONB trong DB; đủ 100 câu SAG chạy mới, không lẫn baseline lịch sử.
- Corpus và câu hỏi khớp SHA-256 trong manifest.
- Hai project/source/collection khác nhau, cùng account đang tồn tại.
- Kiểm tra canonical scope chéo project trả về rỗng; mỗi collection không có point thuộc project khác.
- Đây là scope project SAG; chưa tạo entity Project/membership trong IAM Continuum.
