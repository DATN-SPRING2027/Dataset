# Kiểm tra tính E2E của các runner SAG

## Kết luận

Hai runner dataset đã chạy nhiều thành phần SAG thật, nhưng **chưa đáp ứng yêu cầu E2E đầy đủ qua API, ủy quyền thật và schema `sag` chuẩn**. Không được mô tả các lượt đã kiểm tra là E2E 100%. Đây là audit đọc mã, manifest và DB/Qdrant; không chạy lại benchmark trong audit này.

## Hai lượt dataset đã hoàn tất

| Lượt | Schema dữ liệu thực tế | Documents / SearchUnits / KnowledgeUnits | Graph / tree ACTIVE | Điểm cần lưu ý |
|---|---|---:|---:|---|
| RetrievalCI `retrievalci-fixed-20261027081141` | `sag_bench_retrievalci_20261027070959` | 81 / 784 / 3.585 | 1 / 1 | Tái sử dụng index của run `20261027T071001Z-15e97d`; lượt đánh giá này không upload/index lại. |
| VN-MTEB `vn_mteb-fixed-20261027100535` | `sag_bench_vn_mteb_20261027100535` | 130 / 153 / 368 | 1 / 1 | Lượt này ingest mới, nhưng qua service trực tiếp và trong schema riêng. |

Kiểm tra PostgreSQL chỉ đọc thấy lần lượt 81 và 130 `ingestion_runs` thành công trong các schema trên. Trong `sag.documents`, số document của hai project đó đều là 0. Truy vấn Qdrant chỉ đọc trả HTTP 200, lần lượt 784 và 153 điểm theo scope project/tenant, trùng số SearchUnit trong DB. Các bảng có cùng tên và cấu trúc SAG, nhưng chúng nằm trong schema riêng. `benchmark_runs` là bảng registry bổ sung của harness; không thay thế các bảng SAG lưu tài liệu.

Manifest của cả hai ghi E2 và document event extraction tắt. Đây là cấu hình được ghi nhận, không phải bằng chứng harness chủ động tắt hai tính năng; cũng không chứng minh hai luồng đó đã chạy. Cả hai lượt báo không có lỗi thực thi Q&A ở first pass.

## Những gì thực sự chạy và các khoảng trống

1. **Upload chưa qua HTTP API sản phẩm.** `SAGBenchmark.ingest` gọi trực tiếp `handle_document_upload` với database session và queue, bỏ qua endpoint `/api/v1/sources/{source_id}/documents`, kiểm tra file ở endpoint, và bước xác thực/ủy quyền của endpoint. Service và các tác vụ nền tiếp theo là mã SAG thật. Xem [runner](D:/DoAnTotnghiep/Dataset/sag_benchmark_runtime.py:120) và [endpoint](D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/api/v1/documents.py:210).
2. **Source/Project chưa qua luồng cấp quyền thật.** Harness tự tạo `SourceProjectMapping` trạng thái `CONFIRMED` trong DB với `approval_ref` benchmark. Hai lượt được kiểm tra đều có một mapping loại này. Source API thật tạo mapping `PENDING` để chờ xác nhận. Harness gọi endpoint Continuum login thật với BFF token, nhưng tự cung cấp project ID và headers, không chứng minh BE/IAM đã kiểm tra membership của user đối với project. Xem [runner](D:/DoAnTotnghiep/Dataset/sag_benchmark_runtime.py:105), [mapping được ghi](D:/DoAnTotnghiep/Dataset/sag_benchmark_runtime.py:140), và [create_source](D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/services/source_service.py:378).
3. **Schema riêng là hành vi cố ý của launcher.** `run_isolated_benchmark.py` tạo `sag_bench_*`, khởi tạo các bảng trong đó và copy account từ `sag.users`. Điều này không đáp ứng yêu cầu mới của người dùng về ghi dữ liệu thực tế vào các bảng chuẩn trong `sag`. Xem [launcher](D:/DoAnTotnghiep/Dataset/run_isolated_benchmark.py:29).
4. **Search/Q&A first pass dùng HTTP thật tới SAG.** Runner mở server SAG local với lifespan thật rồi gọi `/api/v1/search/stream`, đọc đến `completed` hoặc lỗi. Đây không chứng minh browser, gateway, BE/IAM hoặc dịch vụ SAG đã triển khai đều được đi qua. Xem [runtime](D:/DoAnTotnghiep/Dataset/sag_benchmark_runtime.py:46) và [client](D:/DoAnTotnghiep/Dataset/benchmark_http_client.py:63).
5. **Top-K và retrieve-only cần đọc đúng track.** First pass chính của cả hai dataset gọi `runtime.ask` không truyền Top-K, nên API tự chọn. RetrievalCI có track Top-5 riêng với `retrieval_only=True`: client dừng tại sự kiện `result`, không chờ generation `completed`. Probe Top-K và graph ablation cũng dùng retrieval-only, index cũ; graph ablation còn thay hàm graph expansion trong runtime. Các track này là diagnostic, không phải Q&A E2E từ đầu. Xem [RetrievalCI](D:/DoAnTotnghiep/Dataset/RetrievalCI_Bench_v0_2026/scripts/run_bench_v0_sag.py:196), [VN](D:/DoAnTotnghiep/Dataset/VN_MTEB_RAG_Bench_2026/scripts/run_vn_mteb_sag.py:36), [HTTP client](D:/DoAnTotnghiep/Dataset/benchmark_http_client.py:99), và [graph probe](D:/DoAnTotnghiep/Dataset/dense_graph_expansion_probe.py:43).
6. **Readiness gate chưa chứng minh mọi tree job xong trước câu hỏi.** `wait_ready` kiểm tra document, knowledge jobs và có một tree `ACTIVE`, nhưng không yêu cầu mọi tree job kết thúc hoặc xác minh active tree bao phủ đầy đủ phiên bản hiện hành. Manifest VN ghi một tree job `running` tại snapshot `pipeline` trước các câu hỏi; `pipeline_after_questions` ghi hai job `succeeded`. Điều đó không tự chứng minh kết quả câu hỏi sai, nhưng loại trừ khẳng định mọi bước đã kết thúc trước first pass. Xem [readiness gate](D:/DoAnTotnghiep/Dataset/sag_benchmark_runtime.py:214).
7. **Các trace tốc độ/ablation không phải E2E chuẩn.** Chúng instrument và thay một số hàm runtime, cô lập recovery của queue, gọi helper chuẩn bị Qdrant trước upload; ablation còn bỏ dense khỏi graph payload. Chúng không gửi truy vấn search hoàn chỉnh. Dữ liệu các probe này được tạo trong `sag` dev mặc dù registry từng ghi schema benchmark; xem [đính chính phạm vi](D:/DoAnTotnghiep/Dataset/reports/ingest-scope-correction-20261027.md).

## Điều kiện để chạy E2E đúng yêu cầu

- Dùng deployment/runtime SAG thật được cấu hình schema `sag`; kiểm tra `current_schema()` và các hàng của đúng project trong bảng SAG chuẩn. Không tạo schema/copy user riêng. Dữ liệu fixture cần nằm trong project/source được cấp quyền thật.
- Dùng đường xác thực và ủy quyền Continuum/BE thật cùng Source đã được owner xác nhận; upload multipart qua API sản phẩm, không gọi service trực tiếp và không tự ghi `CONFIRMED` vào DB. Write endpoint hiện yêu cầu signed principal assertion; cấu hình dev hiện tại không có issuer và JWKS, nên audit này không thể xác nhận đường upload đã được cấu hình E2E.
- Chạy mới từ đầu, không `--skip-index`, không monkeypatch hay chặn queue; chờ và xác minh document, index, knowledge và tree hiện hành hoàn tất. Các tính năng tắt phải được công bố theo cấu hình thực tế.
- Gửi truy vấn Top-5 theo yêu cầu người dùng, đọc stream đến `completed`, lưu kết quả/citation/lỗi, và xác minh bằng chứng lưu ở các bảng SAG chuẩn. Retrieval-only hoặc ablation chỉ được gắn nhãn diagnostic riêng.

Audit này không cấu hình IAM, không giả chữ ký và không chạy một E2E mới. Các kết quả cũ vẫn có giá trị trong phạm vi benchmark/diagnostic đã mô tả, nhưng không phải bằng chứng thỏa hợp đồng E2E mới.
