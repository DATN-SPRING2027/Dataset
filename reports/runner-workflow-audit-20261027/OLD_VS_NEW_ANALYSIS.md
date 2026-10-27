# Runner RetrievalCI cũ và SAG workflow mới

Đối chiếu read-only 50 câu và ground truth của hai run `20261026T141834Z-3e858c`
và `20261027T081142Z-984c8a`. Kết quả runner cũ được coi là kết quả đo có thật.
Chi tiết theo câu: `old_vs_new_question_comparison.json`; script: `compare_retrieval_runs.py`.

Runner cũ vẫn chạy SearchUnit dense retrieval (`run_search_indexing_stage` dùng
embedder và `_retrieve_search_unit_sections` dùng query embedding); 0 dense là
KnowledgeUnit, không phải toàn bộ retrieval. KU graph cũ 29.364 cạnh, không có
tree ACTIVE; run mới có KU dense và tree ACTIVE.

Recall thay đổi ở 2/45 câu answerable: `qst_0348` 3/4 -> 4/4, 5 -> 15 tài liệu;
`qst_0354` 5/8 -> 8/8, 5 -> 26 tài liệu. Precision giảm ở 23/50 câu, bằng ở
27/50 và không tăng; số tài liệu trung bình 3,14 -> 9,54, trung vị 3 -> 4;
output mới có trung vị 48 SearchUnit. Ví dụ `qst_0015` 5 -> 31 tài liệu,
precision 20% -> 3,23%. Như vậy nới tập trả về giải thích rõ hướng thay đổi
precision và làm recall có cơ hội tăng; không chứng minh graph dense là nguyên nhân.

Cắt hậu kỳ 5 đoạn đầu của output dynamic cho recall 96,02% trên 45 câu, so với
98,61% của old Top-5. 4 câu đổi recall: qst_0343 1 -> 2/3, qst_0344 1 -> 3/4,
qst_0350 1 -> 2/3, qst_0354 5/8 -> 3/8. Đây chỉ là dấu hiệu ranking của output
dynamic; không phải chạy Top-5 thật vì candidate generation/selection đổi theo K.

Median stage cũ -> mới theo diagnostics: candidate retrieval 1.487,84 -> 2.662,55 ms;
diversity selection 192,35 -> 2.360,80 ms; tree route 0,32 -> 973,09 ms;
hydration 32,36 -> 41,53 ms; rank fusion 61,97 -> 74,45 ms; internal retrieval
1.886,58 -> 6.478,53 ms. Các median được tính riêng theo stage, không được cộng
thành median tổng. New HTTP retrieval p50 11.101,91 ms bao gồm thêm route/API.
27 câu có 1 wave, 16 có 2, 6 có 3, 1 có 4; 9 dừng deadline. Cả hai run khác
cache, code, API, K và provider; breakdown không xác lập quan hệ nhân quả từng yếu tố.
Graph-expansion timing >0 ở 21 câu: không được khẳng định graph không hề được dùng.

## Cách kiểm tra ngắn nhất trước khi chạy full benchmark

1. Giữ nguyên project, index, dữ liệu, model, API, cấu hình và lưu hash mỗi case.
   Đợi run đang đo hoàn tất để tránh nhiễu provider. Chạy 8 câu gồm qst_0343,
   0344, 0348, 0350, 0354, 0005, 0015 và một câu single-hop chuẩn; đánh dấu
   đây là probe chẩn đoán, không dùng thay số benchmark đầy đủ.
2. Với cùng code SAG và graph, gọi `top_k=5` và auto, mỗi case ít nhất 2 lần,
   đổi xen kẽ thứ tự. Ghi nguồn xếp hạng, recall, precision, stage times,
   candidate/wave counts, route fallback, provider errors và cache state. Bước này
   kiểm tra ảnh hưởng K/waves trước; không lấy gold để can thiệp lựa chọn.
3. Nếu cần xác định riêng đóng góp KU dense: tạo bản sao dataset/schema/collection
   cách ly, xây hai graph với cùng KU đầu vào và cấu hình, chỉ khác dense KU có/không;
   publish tree tương ứng và kiểm tra pin graph, ACL, checksum; SearchUnit embedding
   giữ nguyên. Chạy cùng 8 câu theo cùng protocol ở cả hai bản, xen kẽ thứ tự;
   kiểm tra graph được thực sự dùng và số lần fallback. Không tắt dense SearchUnit.
4. Chỉ khi probe có tín hiệu rõ, chạy toàn bộ 50 câu theo điều kiện được chọn,
   bao gồm truy xuất Top-5 thực sự, auto và judge (nếu cần QA). Không xếp 96,02%
   hậu kỳ thành kết quả matched Top-5 và không lấy probe thay benchmark quốc tế.

Các giá trị 40% trọng số semantic, số cạnh hoặc đồ thị đẹp không thay thế được
ablation. Nếu matched test không cải thiện chất lượng đủ để bù chi phí, có cơ sở
chọn phương án nhẹ hơn; hiện chưa thể quy chi phí truy vấn cho dense một cách độc lập.

## Top-5 thực tế đã hoàn tất

Lượt mới `20261027T081142Z-984c8a` COMPLETED và có 50 request Top-5 thực,
retrieve-only, warmed query cache; không dùng phép cắt hậu kỳ. Run cũ so với
mới lần lượt: recall **98,61% / 98,43%**, precision **63,27% / 62,27%**,
retrieval p50 **1.888,93 / 10.036,76 ms**. Cả 50 request mới không có execution
error. Chỉ hai câu đổi recall: qst_0348 3/4 -> 4/4, qst_0349 3/3 -> 2/3;
qst_0354 giữ 5/8. Run cũ gọi retrieval service trực tiếp, run mới gọi HTTP API
và còn query routing; thời điểm, provider/cache khác nhau. Không suy ra dense
làm retrieval chậm 5,3 lần hoặc dense không bao giờ có ích từ so sánh này.

Probe Top-K/auto `20261027T095848Z-895212` đã bắt đầu sau run trên, cùng scope
và index, 8 câu, 2 lần mỗi điều kiện, API thực. Dense A/B vẫn chưa chạy.
