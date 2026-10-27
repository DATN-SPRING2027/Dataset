# Chạy và lưu hai benchmark SAG theo project

> **Cập nhật 2026-10-27:** Runner dùng API upload và schema `sag`; chỉ xác thực upload và xác nhận mapping scope được bypass cho benchmark. Một lượt smoke 8 file đã hoàn tất ingest, graph/tree và một câu hỏi; xem [kết quả](RetrievalCI_Bench_v0_2026/reports/20261027T132343Z-07ff89/smoke_result.json). Kết quả cũ không chứng minh protocol mới; xem [kiểm tra trước khi sửa](reports/e2e-realism-audit-20261027.md).

Hai entrypoint chính thức trong dataset dùng chung `sag_benchmark_runtime.py`:

- RetrievalCI: 81 tài liệu, 50 câu; giữ công thức chấm của `retrievalci`.
- VN-MTEB local: 130 tài liệu, 50 câu; báo cáo IR@5. Đây không phải full public leaderboard.

Cả hai khởi động **`sag_api.main.lifespan` thật**: EngineManager, hàng đợi ingestion, KnowledgeWorker, graph/tree và LLMClient của sản phẩm. Không có embedder/LLM/runtime mô phỏng, không tự publish graph/tree hoặc tự enrich E2.

Harness đăng nhập Continuum và kiểm tra scoped SAG session. Upload đi qua API HTTP thật; runner thay dependency xác thực chữ ký principal assertion riêng cho upload của project benchmark và ghi xác nhận Source/project mapping trực tiếp. Đây là hai bypass quyền/scope được chấp nhận, không phải kiểm thử E2E quyền Continuum. Queue và các bước nội bộ SAG chạy thật.

Câu hỏi đi qua **HTTP thật trên loopback `/api/v1/search/stream`**, gồm routing, ACL, truy xuất, sinh câu trả lời và citation validation. SAG cố định retrieval Top-K = 5. Timeout đọc từ frontend: 30 giây đến retrieval result, 45 giây idle sau result. Không preload embedding câu hỏi, không dùng gold labels chọn K hay retry; gold labels chỉ dùng sau khi nhận response để chấm.

Embedding/LLM dùng nguyên timeout và retry đang hiệu lực trong SAG sau startup overrides. E2 dùng policy của KnowledgeWorker; manifest lưu cấu hình thực tế và trạng thái bật/tắt E2. Ngân sách/ngưỡng hàng đợi giữ nguyên; việc bị hoãn không được tính thành enrich thành công. Harness chờ các job SAG hoàn tất và dừng khi có lỗi terminal; không cắt toàn bộ corpus ở mốc 3600 giây khi worker vẫn đang xử lý. Timeout/retry từng tác vụ vẫn do SAG quản lý.

`benchmark_support.py` quản lý owner, scope, hash fixture, checkpoint và kết quả bền trong DB. Các lượt chạy cũ được giữ nguyên để audit; protocol mới là **full SAG application**, khác retrieve-only fixed Top-5 của baseline RetrievalCI lịch sử. Không diễn giải bảng ghép thành so sánh ngang cùng protocol.

## Chạy mới

Từ `D:/DoAnTotnghiep`, dùng môi trường Python của SAG và account **đã có, đang active** trong bảng `users`:

```powershell
$env:SAG_BENCHMARK_USER_ID = '<existing-SAG-user-id>'
$env:SAG_BENCHMARK_ORGANIZATION_ID = '<organization-id>'
$env:SAG_BENCHMARK_SCHEMA = 'sag'
$env:PYTHONUTF8 = '1'

& 'sag-laya-integration/SAG/apps/api/.venv/Scripts/python.exe' -u `
  'Dataset/RetrievalCI_Bench_v0_2026/scripts/run_bench_v0_sag.py'

& 'sag-laya-integration/SAG/apps/api/.venv/Scripts/python.exe' -u `
  'Dataset/VN_MTEB_RAG_Bench_2026/scripts/run_vn_mteb_sag.py'
```

Mỗi lệnh tạo `run_id`, project ID, source ID và collection mới. Cùng một account có thể sở hữu cả hai lượt chạy. Tenant dùng organization ID; security partition dùng project ID. Không xoá schema, không xoá collection và không ghi đè báo cáo cũ. Dữ liệu tài liệu/index nằm ngay trong schema ứng dụng đã cấu hình, được tách bằng project/source; không phải chỉ đổi tên evaluator.

Đây là các scope project của benchmark trong SAG. Runner không tạo entity Project/membership trong IAM của Continuum và không tự cấp quyền SSO. Muốn chọn project qua giao diện Continuum cần cấu hình Project/membership tương ứng ở IAM.

## Kết quả bền trong PostgreSQL

`benchmark_runs` được tạo trong schema ứng dụng, có khóa ngoại `user_id → users.id`. Mỗi bản ghi lưu scope, hash corpus/câu hỏi, model, thời gian, trạng thái, metric và toàn bộ kết quả từng câu trong JSONB. RetrievalCI lưu thêm diagnostics và các baseline lịch sử kèm báo cáo.

```sql
SELECT id, benchmark_key, user_id, project_id, source_id,
       status, started_at, finished_at,
       (manifest_json->>'documents')::int AS documents,
       (manifest_json->>'questions')::int AS questions
FROM sag.benchmark_runs
ORDER BY started_at DESC;

-- Kết quả SAG của RetrievalCI, loại baseline lịch sử khỏi tập câu chạy mới.
SELECT r.id, q->>'question_id', q
FROM sag.benchmark_runs r,
     LATERAL jsonb_array_elements(r.results_json->'rows') q
WHERE r.benchmark_key='retrievalci_v0' AND q->>'system'='sag_engine';

-- Kết quả từng câu VN-MTEB.
SELECT r.id, q->>'question_id', q
FROM sag.benchmark_runs r,
     LATERAL jsonb_array_elements(r.results_json->'questions') q
WHERE r.benchmark_key='vn_mteb';
```

Mỗi dataset cũng lưu file ở `reports/<run_id>/`, gồm `run_manifest.json` và các report của runner. `RUNNING` có checkpoint định kỳ; lỗi chuyển thành `FAILED`, giữ dữ liệu đã tạo để kiểm tra; hoàn tất chuyển thành `COMPLETED`.

## Diễn giải kết quả

- Mỗi lượt tạo project/source/collection mới và ingest lại tài liệu. Không tự bỏ qua E2/synthesis khác cấu hình sản phẩm.
- Đọc `execution` và `pipeline` trong manifest để biết policy, trạng thái E2 và tác vụ thành công/thất bại/hoãn của đúng lượt chạy.
- `COMPLETED` nghĩa là đã chạy hết câu hỏi; xem thêm số `execution_errors`. Response retrieval đã nhận nhưng generation timeout được giữ cùng mã lỗi, không biến thành câu trả lời thành công.
- So sánh quốc tế lưu trước đây là tham chiếu lịch sử, không phải provider vừa được gọi lại và không đảm bảo cùng corpus/protocol với lượt này. Runner VN mới không in số leaderboard hardcode.
- Các citation lấy từ response SAG thật. Judge độc lập chấm faithfulness/relevance theo protocol bên dưới; đây không phải human accuracy. Chi phí không đo được để `null`; token count bắt buộc bởi schema RetrievalCI dùng 0 kèm metadata `token_usage_measured=false`, không phải mức tiêu thụ thực tế.
- Thời gian truy xuất tính từ HTTP search đến sự kiện `result`; thời gian Q&A đến `completed` hoặc lỗi. Không bao gồm ingest, không preload/cache trước câu hỏi; runtime có thể tự cache theo hành vi sản phẩm.

## Protocol chất lượng và latency

`run_sag_benchmarks.ps1` chạy hai dataset tuần tự rồi xác minh DB và scope. Không hỗ trợ tiếp tục corpus ingest dở.

- Chất lượng truy xuất dùng metric dataset: recall/precision/MRR/MAP/nDCG; precision@K chia đúng K. VN được báo cáo riêng Legal và Hotpot.
- Chất lượng trả lời dùng rubric faithfulness/relevance 1–5 của RetrievalCI, judge `deepseek-ai/DeepSeek-V3.2`, khác generator SAG. Prompt, lỗi chấm và rationale được giữ; không thay output lỗi bằng điểm mặc định. VN chỉ có qrels, không có reference answer: faithfulness dựa trên evidence, không gọi là answer accuracy/EM/F1.
- Ba lượt query tuần tự: first pass không chủ động preload embedding; hai lượt warm với thứ tự xoay cố định. Không chọn lượt nhanh nhất/điểm tốt nhất. Báo cáo p50/p95 nearest-rank, retrieval, token đầu tiên, Q&A và lỗi; phân phối thành công tách khỏi tất cả attempts. Không cam kết physical cold cache.
- Judge chạy ngoài đồng hồ request. Các lời gọi judge không tính vào latency SAG.
- `first_token_ms` là thời gian đến `summary.delta` công khai đầu tiên. SAG giữ private delta của provider đến khi kiểm chứng citation, nên đây là thời gian đến câu trả lời đã kiểm chứng, không phải raw model TTFT. Không so con số này với TTFT token thô của provider.
- `execution.query_replays=0` ở manifest cũ chỉ việc không tự retry query lỗi trong một lượt. Hai warm replay độc lập được lưu đủ trong `quality_latency.protocol.latency_repetitions=3`; lỗi không bị chọn bỏ.
- Track Top-5 của RetrievalCI dùng kết quả retrieval từ lượt Q&A thật. Hosted baseline lưu sẵn là lịch sử; latency không phải phép so tốc độ nhân quả.
- `international_references.json` lưu các mô hình đã nhắc trong dataset và nguồn kiểm chứng. Không có credential để chạy mới OpenAI/AWS/Azure/Vertex; không dùng mock làm số liệu chất lượng thật. Bảng VN full leaderboard không đủ thông tin để đối chiếu latency và khác corpus local.
- `quality_latency.json` giữ điểm từng câu, rationale, mọi lần đo và các aggregate. Bản hoàn tất được ghi vào manifest JSONB của `benchmark_runs`; VN còn ghi trực tiếp trong report JSON.

Luồng ingest mới mặc định không gọi LLM Event/Entity theo chunk. Embedding dùng client SDK độc lập với kho Event; FOUNDATION dựa trên SEARCH_READY và E2 vẫn chọn lọc. Xem `../sag-laya-integration/SAG/docs/canonical-ingestion-and-adaptive-search.md`.

## Launcher tương thích

`run_isolated_benchmark.py retrievalci|vn_mteb` gọi script tương ứng với schema `sag` chuẩn. Tên file được giữ để tương thích; launcher không tạo schema riêng.

`summarize_benchmark_runs.py <ci-run-id> <vn-run-id>` tìm registry trong `sag`
và các schema benchmark, xác minh file = DB và kiểm tra scope bằng đúng schema
của từng run. Những scope này chưa tự xuất hiện trong backend đang cấu hình
`search_path=sag`; muốn xem chúng qua API/UI cần trỏ backend kiểm tra sang schema
tương ứng và cấu hình quyền Continuum phù hợp.

Query HTTP chạy ở process riêng với API, để event-loop stall không làm sai đồng
hồ timeout của client. Manifest lưu PID client, hash toàn bộ mã API và cấu hình
logging. Lượt chẩn đoán INFO ngày 27/10 được lưu riêng; lượt hiện tại dùng mức
DEBUG được cấu hình trong SAG. Riêng log DEBUG nội dung SSE bị tắt để tránh ghi
toàn văn bằng chứng vào log. Không đổi cấu hình mô hình, E2, retry hoặc timeout
để cải thiện điểm.
