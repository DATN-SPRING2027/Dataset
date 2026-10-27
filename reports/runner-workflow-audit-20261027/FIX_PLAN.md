**Kế hoạch sửa workflow SAG sau điều tra runner — 27/10/2026**

Kế hoạch đã được triển khai và đang xác minh bằng lượt benchmark mới. Xem [FIX_RESULTS.md](./FIX_RESULTS.md) để phân biệt kết quả kiểm thử, lượt chẩn đoán trung gian và benchmark hoàn tất. Căn cứ ban đầu là [REPORT.md](./REPORT.md): graph 677 KU dense chặn event loop khoảng 28,9 giây; ba graph liên tiếp làm timer 30/60 giây trả về sau 74,6 giây; lỗi ingest bị bọc thành non-retryable; FOUNDATION còn hai producer.

**Kết quả cần đạt**

- Một document chỉ hoàn tất ingest sau khi canonical SearchUnit index được xác minh; FOUNDATION/graph/tree không giữ document worker sau mốc đó.
- Một producer FOUNDATION cho mỗi document version/input checksum. E0/E1, dense KU và provenance được giữ đầy đủ.
- Graph và tree tính theo snapshot project, được gộp yêu cầu, không tính lại toàn project trong từng FOUNDATION.
- CPU graph/tree không chạy trên event loop API. Timeout thu hồi được công việc CPU thật.
- Giữ nguyên dense semantic signal, ACL, partition, checksum, temporal validity, publish gates và dynamic Top-K.
- Lỗi mạng tạm thời retry đúng policy; lỗi cấu hình, quyền hoặc dữ liệu không bị retry vô hạn.
- Runner dùng cùng workflow và đo HTTP từ process khác API.

**Luồng sau sửa**

Upload service → canonical parse/dedup → SearchUnit embedding/index → verify manifest → SEARCH_READY và document job SUCCEEDED.

FOUNDATION durable job → embedding còn thiếu/E0/E1 theo version → kiểm chứng và commit DATA_READY → yêu cầu rebuild project.

Project rebuild job → chụp input đã commit → kiểm chứng input/fingerprint → tính graph và routing trong process CPU → kiểm chứng lại snapshot → persist graph/candidate → publish tree theo gates hiện có → ACTIVE.

E2 nếu được cấu hình → enrich chọn lọc → commit evidence/checksum → yêu cầu rebuild project theo cùng cơ chế gộp. Trong lúc chờ graph/tree, dữ liệu SEARCH_READY vẫn có đường hybrid fallback; snapshot cũ không được dùng cho dữ liệu đã mất quyền hoặc hết hiệu lực.

**1. Đóng băng trường hợp lỗi và thêm kiểm tra hồi quy trước khi đổi code**

Thực hiện:

- Giữ nguyên hai run cũ COMPLETED, run bị ABORTED do backlog và run FAILED schema riêng; không reset schema/collection hoặc sửa kết quả cũ thành thành công.
- Giữ tập input kiểm tra: 677 KU dense của project lỗi; thêm một corpus nhỏ có nhiều tài liệu trong cùng project và trường hợp hai project độc lập.
- Thêm test document task có job_queue thật/fake có hành vi enqueue, không dùng job_queue=None để bỏ qua nhánh sau READY.
- Thêm test chuỗi lỗi httpx timeout → index service → document task → queue; kiểm tra attempt và trạng thái document/version/run.
- Thêm test cập nhật version/E2 khi project rebuild đang RUNNING, để xác nhận yêu cầu sau không mất.

Đạt khi: các test phản ánh đúng lỗi hiện tại trước bản sửa; bộ test nhỏ về ACL, manifest, temporal và Top-K vẫn giữ nguyên.

**2. Chỉ giữ worker FOUNDATION làm chủ E0/E1**

File chính:

- D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/jobs/tasks.py
- D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/jobs/knowledge.py
- D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/services/knowledge_service.py
- D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/tests/test_canonical_ingestion_readiness.py

Thay đổi:

- Xóa khối foundation inline sau log document READY. Xóa luôn nhánh dùng field không tồn tại document_fast_graph_enabled; không thêm một flag mới để duy trì hai producer.
- Document job kết thúc sau index đã verify và finalize ingestion run. Discovery/enqueue FOUNDATION vẫn durable, idempotent theo version/input checksum.
- Worker chỉ xử lý embedding cần thiết, rebuild E0/E1 và commit DATA_READY. Bỏ truy vấn toàn bộ project và persist_graph khỏi từng FOUNDATION.
- Sau commit FOUNDATION, enqueue project rebuild. Nếu enqueue gặp sự cố, dữ liệu DATA_READY không bị rollback; bảo đảm discovery/reconciliation của hàng đợi có thể phát hiện yêu cầu còn thiếu.
- Giữ xử lý Event/Entity legacy qua cờ opt-in hiện có; không nhập nó lại vào đường canonical mặc định.
- Giữ khóa version và kiểm chứng input trước commit. Hai lần dispatch cùng input không được tạo hai kết quả logic hoặc ghi đè dữ liệu stale.
- Chuẩn hóa nghĩa trạng thái: SEARCH_READY = tìm kiếm được; DATA_READY = KU/E0/E1 sẵn sàng; tree ACTIVE là trạng thái snapshot riêng. Không thêm enum chỉ để lấp chỗ trống báo cáo.

Đạt khi:

- Một upload dẫn tới một FOUNDATION thành công cho input hiện tại; không còn khối foundation chạy trong document task.
- FOUNDATION có thể thất bại/retry mà không hạ SEARCH_READY đã được xác minh.
- Document worker được giải phóng trước khi project graph chạy.

**3. Dùng job REBUILD_UNIVERSE_TREE hiện có để xây graph + tree theo project**

File chính:

- D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/services/universe_tree_service.py
- D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/services/knowledge_candidate_service.py
- D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/jobs/inproc.py
- D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/jobs/knowledge.py
- Consumer graph trong D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/services/search_unit_retrieval_service.py

Thay đổi:

- Giữ job type/project scheduling hiện có; không thêm broker hay một hàng đợi graph độc lập khi chưa cần.
- Gộp các yêu cầu cùng tenant/project. Mục tiêu mỗi project tối đa một rebuild RUNNING và một follow-up QUEUED.
- Nếu cập nhật đến lúc đang QUEUED: gộp vào job chờ. Nếu đang RUNNING: tạo/gộp một job follow-up, không chỉ trả về job RUNNING rồi làm mất yêu cầu mới.
- Dùng khóa scope trong DB cho scheduling/claim, ngoài khóa nội bộ process, để hai API process không cùng nhận một rebuild của project. Transaction khóa phải ngắn; không giữ transaction dữ liệu qua toàn bộ tính CPU.
- Foundation success, E2 success, version supersede và delete/invalidation đều phải đi qua cùng cơ chế yêu cầu rebuild; rà toàn bộ callers trước khi đổi.
- Chụp danh sách unit, checksum, config và validity dùng cho một build. Trong lúc CPU chạy, cập nhật mới không được nhập lẫn vào snapshot đó.
- Trước publish, kiểm chứng lại input/currentness/ACL. Kết quả stale không được thay tree ACTIVE; follow-up chạy với input mới.
- Kiểm tra consumer graph: pin graph_build_id của snapshot hợp lệ, không gộp tùy tiện các cạnh từ mọi build lịch sử. Dữ liệu mới chưa có graph hợp lệ dùng fallback, thay vì mượn graph stale để tăng recall.
- Đo và rà phần build_routing_snapshot đồng bộ, kể cả lần build lặp khi không có benchmark queries, để chuyển phần CPU nặng vào cùng boundary ở bước 4.

Đạt khi:

- Upload một batch nhiều tài liệu không tạo một whole-project graph trong mỗi FOUNDATION.
- Cập nhật đến trong lúc RUNNING luôn có follow-up và cuối cùng được snapshot ACTIVE bao phủ.
- Hai project không trộn graph/ACL; reader đang giữ snapshot cũ vẫn theo lease/publish contract hiện có.

**4. Đưa tính graph/routing ra khỏi event loop và tối ưu phép tính, giữ kết quả**

File chính:

- D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/services/knowledge_service.py
- D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/services/routing_tree_service.py
- D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/services/knowledge_candidate_service.py
- Lifecycle trong D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/runtime.py và main.py
- Dùng lại mẫu spawn/lifecycle của D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/octx/runner.py và freeze_support của desktop.py.

Thay đổi:

- Tách phần tính thuần CPU khỏi đọc/ghi DB. Process con chỉ nhận payload dữ liệu có thể serialize; không truyền AsyncSession, engine, ORM sống, HTTP client hoặc token provider.
- Process con tính graph và phần clustering/profile/routing nặng, trả dữ liệu candidate. Process cha giữ toàn bộ kiểm chứng DB, persist và publish.
- Bắt đầu với một process CPU được quản lý cho mỗi API process. Dùng lease/admission theo scope để không tạo trùng job giữa các API process. Tăng concurrency chỉ sau khi đo CPU/RAM.
- Khi timeout/hủy/shutdown: terminate/kill và join đúng process con do runtime sở hữu trước khi giải phóng slot; không coi cancel Future là đã dừng CPU. Không publish kết quả từ lease hết hạn.
- Tiền tính kiểm tra finite, vector chuẩn hóa, norm và dấu LSH theo dimension; giữ thứ tự phép cộng/chuẩn hóa cần thiết cho tính deterministic. Không bỏ dense, giảm dimension hoặc sửa ngưỡng/candidate limit để làm benchmark đẹp.
- Ưu tiên stdlib và pattern có sẵn. Chỉ dùng phép tính vector khác nếu kiểm tra parity chứng minh không làm đổi graph ngoài phạm vi được giải thích.

Đạt khi:

- Trên input 677 KU, graph sau refactor cho cùng cạnh, calibration, trọng số và output checksum với bản chuẩn khi algorithm không đổi.
- Kiểm tra thêm vector zero, NaN/Inf, sai dimension, điểm nằm sát ngưỡng và partition khác nhau.
- API health và heartbeat vẫn được xử lý trong khi graph chạy; mục tiêu kiểm tra cục bộ: không có stall hàng giây, heartbeat p95 dưới 100 ms và max dưới 500 ms trong điều kiện đo đã ghi rõ. Đây là tiêu chí kiểm thử, không phải SLA sản phẩm mới.
- Hủy graph không để lại child process tiếp tục tính; không tạo tree ACTIVE từ kết quả stale hoặc incomplete.
- Ghi wall time, CPU, serialization và peak RAM; chỉ công bố mức cải thiện sau phép đo.

**5. Sửa retry, timeout và thông tin lỗi tại shared boundary**

File chính:

- D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/services/search_index_service.py
- D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/jobs/tasks.py
- D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/jobs/inproc.py
- D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/jobs/knowledge.py
- D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/core/config.py và core/errors.py nếu cần dùng domain type hiện có.

Thay đổi:

- Ánh xạ timeout/connect/reset/429/5xx tạm thời sang domain error retryable phù hợp. Giữ cause class khi rethrow. Không bọc mọi lỗi thành ApiError non-retryable.
- Lỗi ACL, dữ liệu/vector/config không hợp lệ, và manifest mismatch thực sự vẫn fail-closed theo phân loại riêng.
- Khi còn retry: Job quay QUEUED, Document quay PENDING/LOADING phù hợp; run/version không bị để lại trạng thái terminal sai. Chỉ final FAILED khi policy hết attempt hoặc lỗi fatal.
- Giữ index cleanup/upsert idempotent theo version để retry không nhân bản điểm hoặc công bố manifest nửa chừng.
- Tách budget FOUNDATION khỏi graph job. Không dùng outer 60 giây để bao một call embedding được phép chờ 120 giây cộng lock/DB/graph.
- Chốt budget theo effective provider timeout, số batch, retry/backoff, thời gian chờ admission và margin commit. Ghi rõ cả SDK retry lẫn job retry; không coi ba attempt của job là chỉ ba provider calls nếu SDK còn retry bên trong.
- Trước hết giữ embedding timeout hiện tại 120 giây; tính và kiểm tra envelope FOUNDATION sau khi graph đã được tách. Không tùy tiện tăng mọi timeout lên 600 giây.
- Deadline UI first-result 30 giây và stream-idle 45 giây giữ nguyên để đo trải nghiệm hiện tại. Retry phục hồi request được báo riêng với các replay dùng đo latency.
- Log an toàn có job/run/project, stage, exception class, cause class, attempt, retryable, elapsed và budget. Không ghi token, header auth hoặc nguyên nội dung tài liệu vào log lỗi.

Đạt khi:

- Timeout đầu tiên rồi provider hồi phục: attempt sau thành công, không reset corpus.
- Lỗi tạm thời hết ba attempt: FAILED với cause rõ ràng.
- Lỗi fatal không được retry vô ích.
- FOUNDATION/graph timeout không làm mất SEARCH_READY; timeout CPU thực sự thu hồi process.

**6. Bỏ N+1 checksum và tra cache bằng input fingerprint trước graph CPU**

File chính:

- D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/services/knowledge_service.py
- D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/services/knowledge_candidate_service.py
- D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/db/models/knowledge.py
- Một migration nếu cần index fingerprint riêng.

Thay đổi:

- Đọc evidence theo batch cho tập unit, dùng chung hàm canonical hóa/checksum. Giữ chunk SQL theo giới hạn driver; không đổi 677 SELECT thành một IN vô hạn cho mọi project.
- Input fingerprint gồm tenant/project, unit IDs và checksum đã xác minh, graph config và phiên bản thuật toán/producer. Không dùng số lượng unit làm cache key.
- Tra build theo fingerprint trước khi tính graph. Dùng metadata hiện có nếu tra cứu và index được rõ ràng; nếu không đủ thì thêm trường input_fingerprint nullable có index cho KnowledgeGraphBuild bằng migration additive. Build cũ vẫn hợp lệ, có thể cache miss lần đầu; không xóa dữ liệu để migrate.
- Cache hit vẫn kiểm chứng checksum/output và currentness cần thiết trước publish. Thay text, evidence, E2, ACL, validity hoặc config phải invalidation đúng.
- Tránh hai job cùng fingerprint tranh insert; xử lý idempotent bằng scope lock/unique constraint phù hợp với mô hình lưu trữ cuối cùng.

Đạt khi:

- Input không đổi không gọi graph CPU lần nữa.
- Evidence/checksum không còn một query cho mỗi KU.
- Thay một thành phần input quan trọng tạo fingerprint khác; cache không phục vụ dữ liệu đã bị thu hồi quyền hoặc superseded.

**7. Sửa cách chạy benchmark và xác minh bằng tải thật**

File chính:

- D:/DoAnTotnghiep/Dataset/sag_benchmark_runtime.py
- D:/DoAnTotnghiep/Dataset/benchmark_support.py
- Hai runner canonical trong Dataset và các test tương ứng.

Thay đổi:

- Chạy API trong process riêng và benchmark client ở process cha/khác. API dùng lifespan, upload service, auth, workers và policy thật. Không dựng pipeline thay thế bằng direct DB insert.
- Child API nhận cấu hình qua cơ chế an toàn; không đưa secret vào command-line/log. Chỉ tắt đúng process benchmark đã tạo, và chờ cleanup.
- Đọc trạng thái readiness qua API/service hiện có hoặc truy vấn read-only đúng scope. Tách các mốc upload, SEARCH_READY, DATA_READY và tree ACTIVE trong báo cáo.
- Giữ hai protocol: retrieval-only fixed-K để đối chiếu baseline cũ; full application dynamic Top-K để đo sản phẩm. Không chọn K theo số ground-truth document của câu hỏi.
- Full QA giữ first pass và hai replay riêng, cùng báo lỗi/timeout. Judge latency không nhập vào latency người dùng. Baseline provider lịch sử được ghi nhãn rõ, không xem là fresh matched run.
- E2 được ghi rõ bật/tắt theo cấu hình thật. E2-selected không được báo thành E2-executed. Không bật E2 bằng wrapper riêng của runner để tăng điểm.
- Fresh run dùng project/collection mới, giữ account và scope hợp lệ; lưu manifest, hash corpus/code, models, policy, latency distribution và kết quả trong DB. Kết quả run lỗi trước vẫn giữ nguyên.

Thứ tự kiểm tra:

1. Test chức năng hiện có và các test hồi quy mới.
2. Snapshot 677 KU: parity graph, CPU worker cancellation và responsiveness.
3. Corpus nhỏ nhiều tài liệu: ingest, FOUNDATION một producer, cập nhật trong khi rebuild RUNNING, publish/fallback.
4. RetrievalCI đủ 81 tài liệu/50 câu; chỉ bắt đầu QA full-pipeline khi corpus đúng điều kiện protocol. Query thêm trong lúc background rebuild để kiểm tra deadline/ACL thực.
5. VN đủ 130 tài liệu/50 câu để kiểm tra tiếng Việt và workload dense khác; E2 smoke riêng nếu endpoint được cấu hình.
6. Ghi p50/p95 retrieval, first token, full QA; error rate, attempt/provider calls, số graph compute/cache hit, peak RAM và stage durations. Không bỏ request lỗi khỏi mẫu.

Đạt khi:

- Không có lỗi document do graph chặn event loop; không có FOUNDATION bị tính lặp bởi inline và worker.
- Readiness/index/ACL/checksum và dynamic Top-K qua các trường hợp chuẩn và lỗi.
- Graph parity qua trước khi đánh giá quality. Recall/precision/faithfulness được báo từ run mới; không hứa trước rằng bằng điểm runner cũ vì protocol và tính năng khác nhau.
- Run lỗi cũ vẫn truy xuất được; run mới có provenance và kết quả DB khớp file.

**Thứ tự chia thay đổi để review và rollback**

1. Orchestration: một FOUNDATION producer; graph/tree theo project, follow-up không mất cập nhật.
2. CPU boundary và math parity: process runner, lifecycle/cancel, graph/routing responsiveness, tối ưu tiền tính.
3. Retry/deadline/error classification: transient/fatal, state transitions và logs.
4. Cache/checksum: batch evidence, fingerprint và migration additive nếu cần.
5. Benchmark client tách process và báo cáo đối chiếu mới.

Mỗi phần có test tập trung trước khi ghép. Không công bố workflow hoàn tất chỉ dựa trên unit tests hoặc smoke hai tài liệu. Giữ compatibility với dữ liệu/index cũ và snapshot ACTIVE cho phần dữ liệu còn hợp lệ; nếu build mới lỗi thì dùng fallback theo contract, không bật lại synchronous whole-project graph trong API để rollback.

**Điểm còn cần xác nhận khi triển khai**

- Budget và concurrency cuối cùng cần số đo sau khi bỏ graph khỏi FOUNDATION; các con số timeout hiện tại không tự trở thành lựa chọn đúng chỉ vì có sẵn.
- Phương án lưu/index input fingerprint chốt sau khi đối chiếu metadata/migration đang dùng; không tạo thêm bảng điều phối khi Job/snapshot hiện có đủ.
- Tách process trên Windows/PyInstaller cần kiểm tra spawn, freeze_support, serialization và hard cancellation bằng đúng entrypoint desktop.
- Exact exception class của hai request Qdrant lịch sử đã mất; bản sửa phải cải thiện quan sát và được xác minh qua lỗi injection mới, không đoán lại log cũ.
