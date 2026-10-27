# Trạng thái và kết quả đã có

Kiểm tra: 2026-10-26 22:58:54 +0700.

**Lượt mới chưa hoàn tất.** Run `20261026T153533Z-bcb5d8` vẫn RUNNING; kiểm tra DB vừa rồi: 16/81 READY, 4 EXTRACTING, 61 PENDING. Chưa chấm câu hỏi nào (0/50); VN-MTEB mới chưa bắt đầu.

## RetrievalCI — kết quả lịch sử, không phải lượt mới

SAG: run `20261026T141834Z-3e858c`, runner trước đồng bộ. Hosted: baseline lưu sẵn trong dataset. Cùng corpus nhưng khác thời điểm/hạ tầng/cache; không kết luận hệ thống nào nhanh hơn.

| Hệ thống | Recall | Precision | Retrieval p50 ms | Retrieval p95 ms |
|---|---:|---:|---:|---:|
| sag_engine | 98.61% | 63.27% | 1888.93 | 2383.96 |
| vertex_ai_rag | 94.54% | 54.67% | 358.44 | 950.50 |
| bedrock_kb | 87.87% | 70.13% | 408.05 | 533.90 |
| openai_file_search | 89.26% | 53.40% | 1358.33 | 1812.94 |
| azure_ai_search | 90.93% | 67.83% | 408.36 | 952.76 |

SAG cũ: abstention correctness 0/5 câu không có đáp án; không có answer-generation score trong lượt retrieve-only này.

## VN-MTEB local — kết quả lịch sử

Run `20261026T142931Z-35460f`: 130 docs/50 câu; Recall@5 = 100%, Recall@10 = 100%, nDCG@10 = 98.68%; p50 retrieval warm-cache = 1852 ms; p50 synthesis = 7735.5 ms.

Có citation marker 50/50 không chứng minh độ đúng/faithfulness. Điểm judge độc lập, TTFT và p95 Q&A theo runner mới chưa có. Đây không phải full public VN-MTEB leaderboard.
