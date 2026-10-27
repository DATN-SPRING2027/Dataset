**Đối chiếu runner cũ với workflow chính của SAG — 27/10/2026, Asia/Saigon**

Runner cũ hoàn tất được vì chạy một quy trình batch tuần tự, tách lúc index khỏi lúc dựng graph, và có phạm vi công việc khác workflow sản phẩm. Workflow chính hiện có chi phí graph dense rất lớn trên event loop của API, lặp graph toàn project trong các job FOUNDATION, vẫn còn hai nơi dựng foundation, và mất thông tin retry khi bọc lỗi ingest. Đổi runner sang gọi workflow chính đã làm các vấn đề này xuất hiện; nó không chứng minh script mới tự làm hỏng dataset.

Lần sửa trước đã bỏ bước Event/Entity LLM theo chunk ở luồng mặc định và sửa Top-K. Phần đó chưa xử lý hết orchestration FOUNDATION/graph. Nhánh foundation inline còn sót là một thiếu sót trong lần sửa đó.

**Phạm vi và nguồn chứng cứ**

- Đọc toàn bộ đường liên quan: hai runner cũ/mới, upload service, document jobs, SDK embedding adapter, worker FOUNDATION/E2, graph persistence, tree enqueue/build/publish, hàng đợi, timeout, retry, readiness, HTTP benchmark harness và các test liên quan.
- Runner cũ được trích từ Git Dataset commit `895f012`, lưu nguyên văn tại [RetrievalCI cũ](D:/DoAnTotnghiep/Dataset/reports/runner-workflow-audit-20261027/old_retrievalci_895f012.py) và [VN cũ](D:/DoAnTotnghiep/Dataset/reports/runner-workflow-audit-20261027/old_vn_mteb_895f012.py). Không chạy các script cũ có nhánh reset schema.
- Hai lượt cũ COMPLETED thực tế: `20261026T141834Z-3e858c`, project `08c89c865e2c481fb5ebbe02`; `20261026T142931Z-35460f`, project `9f1dfc0aab484447a0b1e5c1`.
- Lượt mới schema riêng FAILED: `20261027T030153Z-9b0297`, project `0924d58e249b4502b86dfdb9`, schema `sag_bench_ci_20261027030149`.
- Các wrapper về account/project đã thay đổi sau commit runner cũ. Manifest của hai lượt COMPLETED không lưu hash mã runner, nên không khẳng định bản Git là byte-for-byte đúng script đã chạy. Những khác biệt chính bên dưới được kiểm tra thêm bằng DB của chính các lượt COMPLETED.
- Truy vấn điều tra đặt transaction READ ONLY. Các phép đo graph dùng dữ liệu đọc ra bộ nhớ, không cập nhật DB, không gọi LLM/embedding. Kiểm tra Qdrant chỉ dùng `/points/count`, không xóa hoặc ghi điểm.
- Không sửa code sản phẩm hoặc runner canonical trong lần điều tra này.

**So sánh khối lượng và đường chạy thực tế**

| Nội dung | RetrievalCI cũ | VN-MTEB cũ | Workflow chính, lượt lỗi mới |
|---|---|---|---|
| Tài liệu | 81/81 READY | 130/130 READY | 8 READY, 2 FAILED, 71 PENDING |
| KnowledgeUnit hiện hành | 3.585 | 368 | 677, mới từ 8 tài liệu READY |
| KU có dense vector | 0 | 368, chiều 1024 | 677, chiều 1024 |
| FOUNDATION durable jobs | Không có | Không có | Có; cuối lượt có 2 SUCCEEDED, 4 RETRY, 1 RUNNING |
| E2 | Không chạy | Chọn tối đa 24; 19 thành công | Tắt theo cấu hình thực tế |
| Bản graph duy nhất đã lưu | 1, 29.364 cạnh | 1, 3.905 cạnh | 2; nhiều lần tính bị timeout/rollback không tạo bản lưu |
| Tree ACTIVE | Không có | Có 1 | Không có; job tree còn QUEUED |
| Đường ingest | Tạo record và gọi service trực tiếp | Tạo record và gọi service trực tiếp | Upload service thật → document queue |
| Principal | Fixture dựng trực tiếp | Fixture dựng trực tiếp | Continuum login và SAG session thật |
| Event/Entity LLM theo chunk | Không | Không | Không, sau lần sửa trước |
| Graph | Sau corpus, không có worker đồng thời | Finalize sau corpus; tree có thể tính lại graph | Worker FOUNDATION tính toàn project sau từng version; tree cũng dùng graph |
| Top-K | 5 | 10 | Tự động; chưa chạy câu hỏi nào |
| Synthesis | Không; retrieve-only | Có, chạy sau retrieval, concurrency 8, lấy tối đa 5 section cho synthesis | API stream thật; chưa đến bước này |

Số bản graph lưu trong DB không bằng số lần graph được tính. `persist_graph` tính payload rồi mới tìm bản build đã có. Hai lượt cũ dùng embedding `Qwen/Qwen3-Embedding-0.6B`; model khác không giải thích được sự cố hiện tại. Dense của SearchUnit khác dense của KnowledgeUnit: KU dense bằng 0 không có nghĩa runner cũ không dùng dense retrieval hoặc không phát sinh embedding API calls.

DB đối chiếu: [database_comparison.json](D:/DoAnTotnghiep/Dataset/reports/runner-workflow-audit-20261027/database_comparison.json).

**1. Đã đo được graph dense chặn event loop của API**

`KnowledgeWorker.run_one` gọi `persist_graph`; hàm này gọi trực tiếp hàm Python đồng bộ `graph_payload`. Không có bước chuyển sang worker CPU hoặc nhường event loop trong toàn bộ phép tính đó. Các task document, FOUNDATION và HTTP trong cùng process phải chờ nó.

Đo trên đúng 677 KU đang lưu ở project lỗi, không có traffic LLM/embedding hay DB trong phép tính:

| Phép đo | Wall time | CPU time | Event loop bị chặn lâu nhất | Cạnh |
|---|---:|---:|---:|---:|
| Dữ liệu dense thực tế | 28,853 s | 28,078 s | 28,866 s | 7.869 |
| Cùng unit, bỏ dense trong bản sao bộ nhớ | 1,160 s | 1,172 s | 1,175 s | 4.953 |

Dense khiến phép tính này đắt hơn khoảng 24,9 lần. Phép bỏ dense chỉ là đối chứng: số cạnh đổi, nên không được dùng nó làm bằng chứng rằng bỏ semantic signal vẫn giữ nguyên chất lượng.

Profile riêng 128 unit cho thấy `_cosine` được gọi 5.268 lần, mất 7,60 giây cumulative; tạo dấu LSH mất khoảng 2,37 giây. Cosine lặp kiểm tra finite, chuẩn hóa và tính norm trên từng cặp vector 1024 chiều. LSH lại tính SHA-256 cho các tọa độ ở từng unit; riêng profile 128 unit có 1.048.576 lần SHA-256.

Đây là chi phí CPU Python, không phải LLM extraction. `asyncio` concurrency 4 không biến nó thành bốn worker CPU độc lập.

Nguồn: [graph_payload và cosine](D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/services/knowledge_service.py:634), [worker gọi graph](D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/jobs/knowledge.py:676), [số đo](D:/DoAnTotnghiep/Dataset/reports/runner-workflow-audit-20261027/graph_measurements.json), [profile](D:/DoAnTotnghiep/Dataset/reports/runner-workflow-audit-20261027/graph_profile.txt).

**2. Workflow chính tính graph toàn project trong từng FOUNDATION, còn runner cũ đợi corpus xong**

Sau mỗi lần rebuild một version, worker lấy tất cả KU hiện hành của tenant/project và gọi `persist_graph`. Khi corpus đang nạp, các job tính lại những phần graph đã tính ở các lượt trước. Retry tiếp tục thực hiện lại phần này nếu transaction trước chưa hoàn tất.

RetrievalCI cũ xây KU theo từng tài liệu rồi gọi `persist_graph` một lần ở cuối. VN cũ cũng finalize graph sau khi index corpus; bước publish tree đi qua `build_project_routing_snapshot` có thể tính graph lần nữa, nhưng không tạo hàng chục FOUNDATION đang cạnh tranh khi các HTTP index khác còn chờ.

Ở workflow chính, `build_project_routing_snapshot` còn gọi `persist_graph` thêm khi tree job được chạy. Tree job có coalescing; không có cơ sở nói chắc tree được dựng 81 lần. Sự lặp đã xác nhận nằm trong đường FOUNDATION, cộng với lần tính của tree khi chạy.

Nguồn: [runner CI cũ](D:/DoAnTotnghiep/Dataset/reports/runner-workflow-audit-20261027/old_retrievalci_895f012.py:312), [VN finalize](D:/DoAnTotnghiep/Dataset/reports/runner-workflow-audit-20261027/old_vn_mteb_895f012.py:581), [worker toàn project](D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/jobs/knowledge.py:662), [tree dùng graph](D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/services/knowledge_candidate_service.py:239).

**3. Hai producer FOUNDATION vẫn tồn tại, và cờ tắt inline chưa được khai báo**

Document job đã đánh dấu READY và ghi log hoàn thành, sau đó vẫn chạy `_embed_blocks` và `rebuild_knowledge_version` inline. Worker FOUNDATION riêng cũng làm các bước đó. `rebuild_knowledge_version` có khóa theo version, nên đây không phải hai lần ghi cùng version hoàn toàn không có khóa; vấn đề đã xác nhận là lặp công việc, chờ khóa và giữ slot document job lâu hơn mốc READY/log.

Nhánh inline kiểm tra `getattr(settings, 'document_fast_graph_enabled', True)`. Không có field này trong Settings; Settings bỏ qua extra. Kiểm tra dựng Settings với `document_fast_graph_enabled=False` vẫn cho nhánh `getattr(..., True)` thành True. Không có cấu hình chuẩn tương ứng để chọn worker riêng và tắt inline.

Shared embedding cache có thể tránh một số lần gọi mạng trùng nhau. Không khẳng định hai producer luôn tạo hai lần embedding API call. Nhưng E0/E1, checksum, DB và chờ khóa vẫn có thể bị thực hiện lại. Hai producer cũng không truyền `extra_entities` giống nhau: worker mặc định không bridge entity legacy; inline dùng mặc định của rebuild. Trên corpus mới không có entity legacy, chưa có bằng chứng khác dữ liệu từ điểm này; với nguồn legacy đây là rủi ro tính nhất quán.

Nguồn: [inline sau log READY](D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/jobs/tasks.py:738), [nhánh inline](D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/jobs/tasks.py:767), [khóa version](D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/services/knowledge_service.py:515), [kiểm tra cờ](D:/DoAnTotnghiep/Dataset/reports/runner-workflow-audit-20261027/operational_checks.json).

**4. Timeout không khớp với công việc nằm bên trong và không thể ngắt CPU Python đồng bộ**

Lượt lỗi có: Qdrant client 30 giây, embedding 120 giây, FOUNDATION outer timeout 60 giây, knowledge concurrency 4, document queue concurrency 4. FOUNDATION timeout bao cả embedding, chờ lock, E0/E1, graph toàn project và commit. Chỉ riêng embedding đã được phép chờ lâu hơn timeout bao ngoài.

Kiểm chứng bằng ba tác vụ graph trên 677 KU: lần lượt 24,669 s, 25,217 s và 24,710 s. Một tác vụ vốn chỉ chờ `sleep(0.1)` bị báo TimeoutError với cả deadline 30 s và 60 s; cả hai chỉ trở lại sau 74,62 s. Không gọi provider trong phép tái hiện này. Timer async không được chạy trong thời gian graph chiếm event loop.

Kiểm chứng Qdrant thật, chỉ đọc cùng collection:

- Rảnh trước thử: HTTP 200, 0,755 s.
- Trong hai tác vụ graph: HTTP 200, 49,122 s dù client timeout 30 s.
- Rảnh sau thử: HTTP 200, 0,179 s.

Không phải mọi lần chặn loop đều buộc httpx phát ReadTimeout: thứ tự callback có thể làm response thành công nhưng trễ, như phép thử này. Đã xác nhận việc chặn loop làm méo deadline và thời gian I/O. Không thể khôi phục loại exception gốc của hai cleanup request lúc benchmark thất bại vì log đã bỏ mất class; chưa chứng minh 100% rằng hai request đó không có thêm lỗi mạng độc lập.

Nguồn: [outer timeout](D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/jobs/knowledge.py:609), [Qdrant timeout](D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/jobs/tasks.py:473), [tái hiện timer](D:/DoAnTotnghiep/Dataset/reports/runner-workflow-audit-20261027/loop_timeout_reproduction.json), [Qdrant chỉ đọc](D:/DoAnTotnghiep/Dataset/reports/runner-workflow-audit-20261027/qdrant_read_reproduction.json).

**5. Lỗi ingest bị bọc mất phân loại retry, nên không thực hiện đủ số lần thử**

Chuỗi hiện tại: lỗi HTTP cleanup → `RuntimeError('Qdrant point cleanup failed: ...')` → `ApiError` mặc định `retryable=False`. Queue kiểm tra cờ retry và một số loại domain error; không đi xuống `__cause__` để khôi phục lỗi gốc.

Đã mô phỏng đúng các lớp bọc với `httpx.ReadTimeout('')`: queue trả `_is_retryable=False`; thông điệp công khai chỉ còn `Qdrant point cleanup failed: `. DB của lượt lỗi xác nhận hai PROCESS_DOCUMENT FAILED ở `attempts=1`, dù `job_max_attempts=3`.

`max_attempts=3` là trần cho lỗi được nhận diện retryable, không phải đảm bảo mọi lỗi được chạy ba lần. FOUNDATION có cơ chế retry riêng và thực tế đã retry; việc đó không sửa được lỗi document job đã mất cờ retry.

Nguồn: [bọc lỗi cleanup](D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/services/search_index_service.py:740), [bọc domain error](D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/jobs/tasks.py:550), [phân loại retry](D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/jobs/inproc.py:53), [kiểm chứng](D:/DoAnTotnghiep/Dataset/reports/runner-workflow-audit-20261027/operational_checks.json).

**6. Checksum và kiểm tra cache graph còn lặp nhiều công việc**

`persist_graph` gọi `unit_checksum` cho từng KU. Mỗi checksum truy vấn evidence riêng. Đo trực tiếp 677 unit: 677 SELECT, 1,144 giây trên PostgreSQL hiện tại, không có checksum mismatch. Đây là N+1 query đã đo được; không phải bằng chứng dữ liệu đã hỏng.

Sau vòng kiểm chứng đó, hàm tính toàn bộ `graph_payload`, hash payload rồi mới tìm build đã có trong DB. Vì vậy có cùng build ID không tránh được chi phí graph CPU. Đây là lý do graph có thể chỉ có một bản lưu mà vẫn bị tính nhiều lần.

Nguồn: [checksum từng unit](D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/services/knowledge_service.py:349), [thứ tự tính rồi tìm cache](D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/services/knowledge_service.py:838), [số đo query](D:/DoAnTotnghiep/Dataset/reports/runner-workflow-audit-20261027/checksum_validation.json).

**7. Tree chưa ACTIVE là hậu quả trong lượt này; chưa thấy tree engine chạy rồi lỗi**

DB cuối lượt có một REBUILD_UNIVERSE_TREE QUEUED và một INDEX_UNIVERSE QUEUED. Document jobs và tree job dùng chung hàng đợi; các job upload được xếp trước. Tree chưa có cơ hội xuất bản trước khi runner dừng. Không có bằng chứng tree builder đã chạy và lỗi Leiden/routing ở lượt này.

Runner CI cũ không cần tree ACTIVE để đánh giá; DB lượt COMPLETED của nó không có tree. Runner mới đợi tất cả document search-ready, knowledge DATA_READY, hết job active và có tree ACTIVE; gặp document FAILED sẽ dừng. Đây là khác biệt protocol/readiness, không phải cách sửa bằng việc giả READY hoặc bỏ kiểm chứng.

Theo contract sản phẩm, tài liệu SEARCH_READY có thể phục vụ global hybrid fallback khi knowledge/tree chưa sẵn sàng. Nhưng một benchmark đòi hoàn tất toàn bộ pipeline có quyền dừng và báo lỗi chuẩn bị corpus. Cần phân biệt availability của phần đã index với thành công toàn bộ corpus.

Nguồn: [hàng đợi cuối lượt](D:/DoAnTotnghiep/Dataset/reports/runner-workflow-audit-20261027/operational_checks.json), [runner wait_ready](D:/DoAnTotnghiep/Dataset/sag_benchmark_runtime.py:193), [contract độc lập readiness](D:/DoAnTotnghiep/sag-laya-integration/SAG/docs/phase-0-contracts-and-foundations.md:378).

**8. 'Runner cũ thành công' không có nghĩa đã kiểm tra cùng chất lượng, E2 và trải nghiệm UI**

- CI cũ retrieve-only, warmup trước đo, Top-5, không synthesis/judge, không FOUNDATION queue và không tree ACTIVE. Chỉ số retrieval của nó có giá trị cho cấu hình đã chạy; không xác nhận full product pipeline.
- VN cũ có dense và synthesis nhưng chỉ 368 KU, ít hơn cả 677 KU từ 8 tài liệu đầu của CI mới. Nó chạy từng pha: index → E2 → graph/tree → retrieval → synthesis. Không đan graph nặng với index HTTP.
- VN cũ chọn tối đa 24 E2, dùng policy riêng 45 s, input 2.600 ký tự, output 1.200 token, concurrency 6 và tối đa hai lần gọi; lỗi từng unit được ghi warning rồi tiếp tục. Lượt cũ có 19 job E2 SUCCEEDED. Lượt mới E2 đang tắt theo cấu hình endpoint/model riêng; 60 unit được đánh dấu có thể enrich không phải 60 LLM calls.
- VN cũ synthesis concurrency 8, dùng tối đa 5 section. Chỉ số 'citation_grounded' được tính bằng regex có marker `[n]`, không chứng minh faithfulness hoặc factual accuracy. Runner mới thêm judge riêng và hai replay nên tổng khối lượng QA về sau khác; phần đó chưa chạy và không gây lỗi ingest hiện tại.
- Các runner cũ tự tạo record READY và principal fixture, gọi service trực tiếp, bỏ qua lifecycle upload/job/recovery của ứng dụng. DB cũ có chunk_count trên Document bằng 0 dù SearchUnits đã được index; đây là side effect không được runner cập nhật, không phải không có index.
- Script cũ có nhánh reset/drop schema. Không nên chạy lại nguyên bản đó lên DB đã giữ kết quả để chữa lỗi workflow.

**9. Runner mới còn một điểm cần sửa trước khi khẳng định timeout giống browser hoàn toàn**

Harness hiện dùng HTTP socket thật nhưng server uvicorn và httpx client đều ở cùng asyncio event loop. Khi graph chặn loop, timer 30/45 s của client benchmark cũng không được thực thi đúng theo đồng hồ thực. Browser/Next.js chạy process khác sẽ tự timeout trong lúc API bị nghẽn.

Điều này không tạo ra công việc graph thừa trong product và không giải thích riêng lỗi ingest; nhưng có thể làm phép đo query timeout dưới tải khác UI thật. Muốn kiểm chứng latency/timeout như UI, nên chạy API và benchmark client ở process riêng, vẫn giữ nguyên endpoint/policy/auth.

Nguồn: [serve cùng loop](D:/DoAnTotnghiep/Dataset/sag_benchmark_runtime.py:44), [client deadline](D:/DoAnTotnghiep/Dataset/sag_benchmark_runtime.py:219).

**10. Vì sao test nhỏ trước đó không bắt được**

Test canonical ingestion dùng index giả và gọi document task với `job_queue=None`, nên không chạy nhánh inline sau READY. Test graph dùng lượng unit nhỏ. Smoke API thật trước đó chỉ có hai tài liệu nhỏ. Chúng kiểm tra được cờ tắt Event LLM, manifest fail-closed, ACL và Top-K nhưng không kiểm tra tranh chấp hai producer, graph dense hàng trăm unit, event-loop lag hay chuỗi retry từ Qdrant.

Vì vậy 55 test qua là bằng chứng cho các trường hợp đó, chưa phải chứng nhận tải thật của workflow. Lần sửa trước và cách báo 'luồng đã ổn' đã thiếu phần kiểm tra này.

Nguồn: [test bỏ qua job_queue](D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/tests/test_canonical_ingestion_readiness.py:108).

**Chuỗi gây lỗi được xác nhận và giới hạn kết luận**

Dense KU + tính graph toàn project trên event loop → chặn API/worker/I/O hàng chục giây mỗi lần → các deadline bị trễ hoặc hủy tác vụ → FOUNDATION retry và chi phí tính lại → ingest gặp lỗi cleanup Qdrant → lỗi bị bọc non-retryable → hai document FAILED ngay lần 1 → runner full-pipeline dừng trước QA.

Các thành phần CPU, event-loop starvation, timeout bị trễ, hai producer và mất retry đã được kiểm chứng bằng code/DB/phép đo. Loại exception mạng gốc của hai cleanup request lịch sử không còn trong log, nên quan hệ nhân quả riêng của từng request đó chưa được chứng minh tuyệt đối bằng stack trace tại thời điểm xảy ra. Không có bằng chứng cần đổi provider hoặc model để giải quyết phần CPU đã đo.

Đã loại khỏi nguyên nhân trực tiếp của lượt lỗi: Top-K (chưa hỏi câu nào); Event/Entity LLM (đã tắt); E2/token quota (E2 tắt, quota 0); backlog cũ (lượt schema riêng vẫn lỗi); vector sai chiều (677 KU đều dense 1024, graph kiểm tra hợp lệ); lỗi checksum của 677 KU (0 mismatch).

**Workflow cần hướng tới và thứ tự sửa**

1. Một producer FOUNDATION cho mỗi version. Document job hoàn tất sau index được xác minh; bỏ nhánh dựng foundation inline trùng. Không bỏ parsing, ACL, idempotency hay kiểm chứng manifest.
2. FOUNDATION làm KU/E0/E1 theo version. Graph/tree là job theo project/snapshot được gộp yêu cầu và tính từ dữ liệu đã commit; không rebuild toàn project trong mỗi document FOUNDATION.
3. Đưa graph CPU ra khỏi event loop của API; giảm tính lặp cosine/finite/norm/LSH bằng tiền tính và tận dụng phép tính vector phù hợp. Giữ semantic signal, deterministic output và checksum; không dùng phép bỏ dense của đối chứng làm bản sửa chất lượng.
4. Giữ phân loại lỗi gốc và retryable qua các lớp. Lỗi mạng tạm thời retry đúng policy; lỗi cấu hình/ACL/manifest thực sự không được đổi thành retry vô hạn. Thông điệp log an toàn cần có exception class, stage và cause class.
5. Tách budget cho network, FOUNDATION và graph job; outer deadline phải tương thích với công việc bên trong. Tăng timeout đơn thuần không giải quyết chặn event loop hoặc công việc bị lặp.
6. Gom truy vấn evidence/checksum và kiểm tra fingerprint/cache trước phép tính graph nặng, nhưng vẫn kiểm chứng snapshot/ACL/currentness khi publish.
7. Đo HTTP từ process client riêng. Giữ cả benchmark retrieval-only để so cấu hình cũ lẫn full product benchmark; không so p50 retrieve-only đã warmup với p50 QA có synthesis/judge.
8. Bổ sung test với vài trăm KU dense, heartbeat/event-loop responsiveness, hai producer/queue thật và chuỗi lỗi HTTP→retry. Sau đó chạy lại đủ corpus, không chỉnh Top-K theo ground truth hoặc bỏ câu lỗi.

Chưa thực hiện các bản sửa trên. Chưa có kết quả Recall/precision/QA latency mới, vì lượt full product đã thất bại ở chuẩn bị corpus. Điều tra này không chạy lại full VN-MTEB, không chấm lại provider quốc tế và không khôi phục được exception class bị mất của hai request cleanup lịch sử.
