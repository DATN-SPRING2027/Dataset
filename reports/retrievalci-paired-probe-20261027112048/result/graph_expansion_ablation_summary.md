# Đối chứng dense KnowledgeUnit graph với Top-5

**Run:** `20261027T112049Z-6afc25` · **Status:** COMPLETED · **Dataset:** RetrievalCI 50 câu · **Đo:** retrieval-only, Top-5 cố định

## Kết quả

| Chỉ số | Dense graph bật | Dense edge tắt | Chênh lệch (tắt − bật) |
|---|---:|---:|---:|
| Recall theo tài liệu | 98,43% (45 câu có nhãn) | 96,20% (45 câu có nhãn) | −2,22 điểm % |
| Precision theo tài liệu | 62,27% (50 câu) | 61,60% (50 câu) | −0,67 điểm % |
| Retrieval latency p50 | 6,017 giây | 6,034 giây | +17 ms |
| Retrieval latency p95 | 20,649 giây | 21,306 giây | +657 ms |
| Lỗi request | 0/50 | 0/50 | — |

## Graph thực sự ảnh hưởng câu nào?

- Graph expansion được gọi ở **21/50 câu** trong mỗi nhánh. Trong nhóm này, bộ tài liệu trả về giống nhau ở **21/21 câu**; thứ tự khác ở 1 câu. Recall (17 câu có nhãn) và Precision (21 câu) bằng nhau giữa hai nhánh: **95,83% Recall**, **47,94% Precision**.
- Hai bộ tài liệu khác nhau còn lại là `qst_0005` và `qst_0482`; cả hai đều **không gọi graph expansion**. `qst_0005` là nguồn duy nhất của mức giảm Recall tổng thể; `qst_0482` không có nhãn Recall theo tài liệu. Vì vậy mức giảm tổng hợp 2,22 điểm % chưa phải bằng chứng dense graph gây giảm chất lượng.
- Dense bật/tắt đều mở rộng tổng cộng 200 ứng viên graph trên 21 lần gọi. Graph bật có 46.083 cạnh; graph dựng lại sau khi bỏ dense feature có 29.310 cạnh (**ít hơn 36,4%**). Dựng graph đối chứng mất 6,74 giây trong lượt đo.
- Dù kết quả cuối luôn giới hạn ở Top-5, độ rộng candidate ghi trong trace là 32 ở 38/50 câu; các câu còn lại tăng thích nghi lên 128 hoặc 256. Đây là lý do cần phân biệt `candidate_k` với `final_top_k`.

## Cách chạy và giới hạn

Hai nhánh dùng cùng index, cùng 50 câu và cùng Top-5; thứ tự bật/tắt luân phiên AB/BA theo câu. Nhánh tắt chỉ bỏ dense feature khi dựng cạnh KnowledgeUnit. Các cạnh dựa trên văn bản/entity/citation vẫn còn; dense SearchUnit và routing tree đã publish được giữ nguyên. Đây là phép thử **đóng góp của dense signal vào graph expansion**, không phải phép thử xóa toàn bộ graph hay bỏ embedding dense khỏi hệ thống.

Đây là một lượt đo mỗi nhánh cho mỗi câu, không chạy sinh câu trả lời. Raw Recall toàn bộ chênh −2,22 điểm %, hơi vượt biên 1–2 điểm % bạn nêu; nhưng phần chênh đó đến từ câu không đi qua graph. Kết quả trên nhóm thật sự gọi graph là 0 điểm % chênh Recall/Precision. Nếu cần quyết định rollout theo ngưỡng nghiêm ngặt, nên lặp lại ít nhất hai câu khác biệt (`qst_0005`, `qst_0482`) hoặc chạy thêm một lượt paired 50 câu để xác nhận độ ổn định.

## Top-K trong các search stack thực tế

Không có một `K` chung cho mọi tầng. Microsoft Azure AI Search khuyến nghị bắt đầu với vector candidate `k=30–50`, rồi giới hạn kết quả cuối `top=10–20` cho hybrid search; semantic ranker nhận tối đa 50 kết quả. Qdrant minh họa prefetch 20 kết quả mỗi nhánh dense/BM25, hợp nhất/rerank rồi trả 10 kết quả; tài liệu cũng khuyên đo candidate depth trên query có nhãn vì tăng depth có thể tăng latency. Do đó Top-5 đầu ra có thể hợp lý, miễn candidate pool đủ rộng và có rerank/điều kiện dừng.

- [Microsoft: Create a hybrid query](https://learn.microsoft.com/en-us/azure/search/hybrid-search-how-to-query)
- [Qdrant: Hybrid and multi-stage queries](https://qdrant.tech/documentation/search/hybrid-queries/)
- [Qdrant: Candidate depth](https://qdrant.tech/documentation/search-tuning/candidate-depth/)

## Artifact chi tiết

[graph_expansion_ablation.json](./graph_expansion_ablation.json) chứa protocol, response và score của từng lượt.

**Ghi chú vận hành:** Sau khi ghi xong kết quả, log có cảnh báo timeout lúc graceful shutdown. Manifest vẫn là COMPLETED, JSON đã được ghi và cả 100 request đều không có lỗi; cần tách cảnh báo dọn runtime khỏi chất lượng retrieval.

