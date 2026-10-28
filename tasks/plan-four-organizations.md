# Kế hoạch chuẩn bị dataset cho bốn organization

**Trạng thái:** tài liệu chuẩn bị, chưa tạo/sửa dataset, importer hoặc seed. Áp dụng cho Northstar `Project1`, [Nova](../Organization2-Nova-Solutions/README.md), [CloudOps](../Organization3-CloudOps-Services/README.md) và [MediFlow](../Organization4-MediFlow/README.md). Phải đọc [checklist mapping](../CONTINUUM-DATASET-MAPPING.md). Không coi tài liệu này là bằng chứng runtime/import đã hoạt động.

## Mục tiêu và phạm vi

- Rà soát và bổ sung những gì Northstar còn thiếu; tạo dataset synthetic độc lập cho ba organization mới, đủ project, thành viên, task và **ba dạng Group Note**: Task Note, Project Document, Work Report, với lịch và câu chuyện thực tế như README từng organization.
- Team và Team Membership không thuộc phạm vi. AI Chat là tính năng sản phẩm, không tạo lịch sử AI Chat trong dataset; bộ câu hỏi/gold đánh giá vẫn để riêng.
- Mô hình chủ đạo: Northstar Scrum-like, Nova Waterfall, CloudOps Kanban, MediFlow Hybrid. Mô hình gắn với project; không ép sprint cho Kanban/Waterfall.
- Chuẩn bị tương thích để sau này có thể import, nhưng phải xác minh contract/đường import trước khi khẳng định có thể ship. Không tự seed DB, đổi API, migration, cấu hình hoặc bật AI indexing trong công việc chuẩn bị tài liệu này.

## Căn cứ Northstar và khoảng trống cần xác minh

Northstar v1.3 ghi 8 project, 2.500 Jira-like issue, 48 Work Task, 48 Task Note, 58 review event, 8 Work Report và 179 ca evaluation. Dữ liệu là synthetic, không seed MongoDB; Task Note không tự thành nguồn tri thức. Có generator `Project1/tools/generate_v1.py` và `workflows_v13.py`, test `tests/test_workflows_v13.py`; không sửa JSONL/XLSX trực tiếp. Xem [kiểm kê ban đầu](northstar-gap-baseline.md), [hướng dẫn](../Project1/00_START_HERE.md), [ingestion contract](../Project1/INGESTION_CONTRACT.md) và [plan v1.3](plan-work-task-note-v1.3.md).

Đây là căn cứ để kiểm tra, không mặc định mọi issue cần thành task hay mọi project phải có cùng số lượng. Cần kiểm kê thực tế từng project và hợp đồng mới nhất: project/user/membership/role; task, assignee, parent, sprint khi có, steps, comment/worklog/history; ba dạng Group Note; câu hỏi/evidence chuẩn; ACL và timeline. Phân loại **đã đủ / có nhưng cần bổ sung / chưa có / chưa xác minh**, kèm số lượng và file nguồn. Không gọi dữ liệu benchmark là đã nhập sản phẩm.

## Thứ tự thực hiện

### T0 — Khóa phạm vi và contract

1. Xác minh revision BE/FE, OpenAPI, validators, các trạng thái và quyền hiện hành; phân biệt source, API được đăng ký và runtime đã được kiểm thử. Ghi data dictionary theo bảng trong checklist mapping.
2. **Group Note bắt buộc:** có note trong tab công việc, Project Document (FRS/design...) và Work Report theo kỳ giữa Member–Leader và Leader–Manager. Xác minh mapping, quyền và hành vi duyệt theo contract hiện hành; không tạo Notebook riêng.
3. Chốt hoặc ghi rõ chưa chốt: số project, thành viên, kỳ mô phỏng, ngày lễ, quy mô và môi trường nhập. Quy định file inventory/manifest của Northstar hiện có phải được bảo toàn hoặc thay đổi có kế hoạch; không lặng lẽ bỏ giới hạn cũ.

### T1 — Audit Northstar và tạo ma trận chung

1. Kiểm kê từng loại dữ liệu, số lượng và mức phủ theo project; so với contract Task, ba dạng Group Note: Task Note, Project Document và Work Report.
2. Ghi danh sách thiếu theo field, liên kết, nội dung, quyền, test, người duyệt và thời gian; nêu cách mở rộng generator và hệ quả tới manifest/catalog. Bảo tồn ID, issue và dữ liệu gốc trừ khi có thay đổi cần thiết, có kế hoạch rõ.
3. Soạn mapping source → target, enum, null, foreign key, quyền và provenance; phân biệt trường import được, metadata chỉ trong dataset và evaluation.

### T2 — Thiết kế ba organization mới

Đọc mục **Repo tham chiếu** trong từng README: Nova dùng OrangeHRM; CloudOps dùng IncidentRelay và có thể tham khảo postmortem công khai; MediFlow dùng OpenMRS. Lập nhật ký nguồn gồm URL, commit/release, thời điểm truy cập, file/issue, giấy phép và cách sử dụng. Kiểm tra quyền của từng tài nguyên trước khi sao chép; không tạo sự kiện giả cho người hoặc organization thật. Phân biệt thông tin đã kiểm chứng từ nguồn với nội dung synthetic; Waterfall/Kanban/Hybrid là mô hình giả lập, không suy ra quy trình của repo gốc.

1. Mỗi organization có bối cảnh, project, thành viên và membership, role đúng contract; task/notes/documents/reports và đầy đủ ba dạng Group Note. Thêm chat giữa người chỉ khi phục vụ kịch bản và contract cho phép.
2. Dựng timeline và sự kiện gốc trước: giờ `+07:00`, ngày làm việc, ngày nghỉ, lễ, OT 17:00–22:00, các ngoại lệ có lý do và người trực; phân biệt bot/con người.
3. Tạo chuỗi có thể truy vết: ốm/mưa bão/lỗi/thay đổi yêu cầu → ảnh hưởng → chuyển giao/sửa → task và note → tài liệu/review → báo cáo. Dùng tiếng Việt/Anh và tình huống đa dạng nhưng nhất quán, không sao chép nội dung máy móc giữa organization.
4. Theo từng mô hình, có trạng thái và tài liệu riêng: Nova có duyệt phase/change request; CloudOps có incident, workaround, root cause và bàn giao; MediFlow có feedback, quyết định, sprint và milestone. Đây là nội dung mô phỏng, không tự suy ra mọi thứ đều có entity trong ứng dụng.

### T3 — Generator và kiểm định dữ liệu

Thiết kế generator tái lập cho từng dataset; sửa generator Northstar theo audit, không chỉnh tay output. Dùng ID nguồn ổn định, khóa ngoại, project/org scope, valid enums, chronology, author/reviewer, version và kiểm tra quyền. Xây manifest, data dictionary, catalog và báo cáo số lượng. Ghi rõ field chưa có target, dữ liệu giả lập và giới hạn; không chứa secret hay PII thật.

### T4 — Evaluation có người kiểm tra

Chọn các mốc của mỗi project, tạo checklist và câu hỏi có gold/evidence, nguồn/version, quyền, người duyệt; hai người kiểm tra và xử lý bất đồng. Có ca thiếu nguồn, mâu thuẫn, thay đổi quyết định, bản nháp, truy cập sai scope và người bị thu hồi quyền. Tách tập phát triển khỏi kiểm tra cuối; không index gold hoặc fixture test-only như dữ liệu thật. Đo đúng, thiếu, sai/bịa, nguồn, quyền và chi phí/thời gian nếu thực sự đo.

### T5 — Chuẩn bị đường import và bàn giao

Viết mapping ID, phân loại API/importer/metadata/chưa khả dụng, thứ tự phụ thuộc, báo cáo lỗi và cách chạy lại. Xác minh giới hạn actor/timestamp/history; không giả định API cho phép backdate. Chỉ thực hiện seed sau khi môi trường, contract, cách rollback và phạm vi đã được xác nhận. Kiểm tra số lượng, liên kết, quyền, tải file và chạy lại không trùng trên môi trường an toàn nếu có đường import được duyệt. Không khẳng định end-to-end từ tests dataset.

## Quality gates

- Generator/validator và test liên quan pass; chạy hai lần và so hash để kiểm tra tái lập.
- Kiểm tra khóa ngoại, timeline/lịch, role/scope, trạng thái/phiên bản, review, nội dung và cả fixture sai để xác nhận validator phát hiện lỗi.
- Manifest, inventory, catalog và số lượng khớp output; rà secret, thay đổi ngoài phạm vi và status/diff.
- Có ít nhất một chuỗi nguồn → task → note → document/report → gold cho mỗi organization và một ca từ chối quyền, kèm review của người.
- **Group Note:** mỗi organization phải có đủ Task Note, Project Document và Work Report; kiểm tra report hằng ngày/hằng tuần và hai luồng Member–Leader, Leader–Manager theo contract thực tế.
- Báo cáo phân biệt test dataset, import/API, runtime/AI; nêu phần chưa hỗ trợ và lệnh bàn giao.
