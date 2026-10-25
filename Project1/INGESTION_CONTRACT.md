# Ingestion Contract — Northstar Commerce Dataset v1.3

## 1. Định dạng nội dung, Lịch làm việc & Quy cách đóng gói
- **Canonical Content Formats**: Markdown (.md) và Word (.docx).
- **Múi giờ, Giờ hành chính, Nghỉ trưa, OT & Ngày lễ Việt Nam**:
  - Toàn bộ dấu thời gian thực thi của con người và bot đều dùng chuẩn ISO 8601 kèm múi giờ Việt Nam `+07:00` (`YYYY-MM-DDTHH:MM:SS+07:00`).
  - **Giờ hành chính (Regular Working Hours)**: `08:00–12:00` và `13:00–17:00` (nghỉ trưa `12:00–13:00` tuyệt đối không có hoạt động của nhân sự).
  - **Khung giờ Tăng ca / Overtime (OT)**: `17:00–22:00+07:00` (từ 5h chiều đến 10h tối theo giờ Việt Nam), được gắn nhãn tường minh `is_overtime: true`, `overtime_hours`, và `work_mode: "evening_overtime"`.
  - **Nghỉ Thứ Bảy, Chủ Nhật & 5 Ngày Lễ Việt Nam**: Nhân sự nghỉ vào Thứ Bảy, Chủ Nhật và 5 ngày lễ quốc gia trong kỳ (`2026-04-27` nghỉ bù Giỗ Tổ Hùng Vương, `2026-04-30`, `2026-05-01`, `2026-09-01`, `2026-09-02`), tổng cộng đúng **123 ngày làm việc chính thức (official working days)** trên 128 ngày trong tuần.
  - **Ngoại lệ OT Cuối tuần (Weekend Incident War-Room)**: Chỉ phát sinh vào 3 ngày Thứ Bảy (`2026-08-29`, `2026-09-26`, `2026-10-10`) trong khung `17:00–22:00+07:00` (`work_mode: "weekend_incident_ot"`) cho 6 ticket sự cố P0/P1 & Canary (`CHKO-012`, `CHKO-015`, `PAY-002`, `PAY-003`, `CHKO-005`, `PLAT-005`).
  - **Hệ thống tự động / Bot 24/7**: 4 bot hệ thống (`BOT-SFTP-SYNC` lúc `02:00:00+07:00`, `BOT-INV-EXPIRY` lúc `03:30:00+07:00`, `BOT-CI-RUNNER`, `BOT-ALERT-MANAGER`) hoạt động 24/7 kể cả ban đêm, cuối tuần và ngày lễ (`actor_type: "system_bot"`).
  - **Cách tính `business_hours_elapsed`**: Tổng thời gian giao nhau (intersection) của khoảng `[created_at, updated_at]` với hai ca hành chính `08:00–12:00` và `13:00–17:00` trên các ngày làm việc chính thức (loại trừ cuối tuần và 5 ngày lễ Việt Nam), cộng với `overtime_hours`, làm tròn 1 chữ số thập phân.
- **Physical Packaging**:
  - Toàn bộ 1.373 bản ghi cập nhật kỹ thuật hàng ngày được đóng gói thành đúng 56 file Markdown bundle theo từng dự án và từng tháng (`documents/markdown/bundles/<PROJECT>-<YYYY-MM>.md`).
  - Lịch trình cập nhật diễn ra trên đúng **123 ngày làm việc chính thức (official working days)** trong khoảng từ `2026-04-16` đến `2026-10-12` (20 ngày đầu có 12 tài liệu/ngày và 103 ngày tiếp theo có 11 tài liệu/ngày = 1.373 tài liệu). Không tạo cập nhật của con người vào cuối tuần hoặc ngày lễ Việt Nam.
  - Mỗi bản ghi tài liệu logic trong bundle sở hữu thẻ neo định danh duy nhất (ví dụ `<a id="doc-cat-20260416-01"></a>`) và mã băm `content_sha256` độc lập theo 12 mẫu cấu trúc tài liệu chuyên biệt.
  - Có 10 tài liệu DOCX canonical, 8 DOCX rendition được liên kết với Markdown canonical, và 43 tài liệu Markdown formal.

## 2. Định danh, Khóa ngoại & Trích dẫn RAG
- **Khóa chính**: `document_id` (ví dụ `DOC-CAT-20260416-01`) và `issue_id` / `issue_key` (ví dụ `CAT-001`) là định danh bất biến.
- **Markdown/DOCX rendition**: Bản Word xuất từ Markdown giữ cùng `canonical_document_id`; `rendition_paths` trỏ đến file DOCX và không tạo logical document/chunk trùng lặp.
- **Requirement/test IDs**: `structured/requirements.jsonl` lưu 64 FR và 10 NFR; `structured/functional_test_cases.jsonl` lưu 84 test chức năng có liên kết requirement; kết quả mô phỏng nằm trong `structured/test_execution_results.jsonl` được phân bổ thực thi bởi đội ngũ 5 QA (`M-010`, `M-037`..`M-040`).
- **Phạm vi tài liệu cấp công ty (Organization-level Scope)**: Các tài liệu chiến lược chung của công ty (Charter, Meeting Decisions) có `project_id: null`, `organization_id: "ORG-NSC"`, và `scope: "organization"`.
- **Khớp nối thời gian Issue - Document**: Mọi `source_issue_key` liên kết trong tài liệu đều tồn tại trong `issues.jsonl` và có ngày tạo `issue.created_at[:10] <= document.created_at[:10]`.
- **Ánh xạ mã tham chiếu ngoại vi**: Mã tham chiếu đối tác `INT-001` được ánh xạ chuẩn xác vào ticket chính quy `CAT-008`. Mã `NONEXISTENT-999` chỉ xuất hiện duy nhất trong fixture kiểm thử lỗi mồ côi `fixtures/orphan_issue_reference.md`.
- **Trích dẫn nguồn RAG**: Khi trả về nguồn tham khảo cho người dùng, công cụ retrieval bắt buộc trả về `file_path` cùng với `section_anchor` chính xác.

## 3. Quy chuẩn kiểm soát quyền truy cập (ACL Pre-filtering)
- **Quy tắc vàng**: Bộ lọc ACL phải được áp dụng **TRƯỚC** khi tính toán khoảng cách vector ranking và trích xuất snippet văn bản.
- Tuyệt đối không để rò rỉ tiêu đề, trích đoạn hoặc tín hiệu tồn tại của tài liệu khi người dùng không thuộc nhóm quyền cho phép.
- **Cách ly đa tenant**: Người dùng thuộc tenant Meridian Outfitters (`ORG-MERIDIAN`) và đối tác PulsePay (`ORG-PULSEPAY`) chỉ tham gia dự án với vai trò `external_collaborator`, giữ đúng nhóm `GRP-MERIDIAN` / `GRP-PULSEPAY` và tuyệt đối không được kế thừa nhóm nội bộ (`GRP-CHECKOUT`, `GRP-CATALOG`, v.v.) của Northstar.
- **Cựu nhân viên (Inactive Staff) & Nghỉ phép (PTO)**: Nhân viên đã nghỉ việc (`M-018`, `M-045`, `M-070`, `account_status: inactive`) bị thu hồi toàn bộ phiên đăng nhập và nhóm quyền (`status: revoked`) ngay tại ngày `left_at`. Không có bất kỳ issue mở hay hoạt động nào sau `left_at`; các ticket đang dở dang được bàn giao (`field: "assignee"`) trước hoặc đúng ngày nghỉ.

## 4. Mô hình Agile Sprint, Spillover & Cách tính Story Points
- Mỗi dự án có 13 sprint liên tiếp, mỗi sprint dài 14 ngày tính cả ngày bắt đầu và kết thúc, từ `2026-04-14` đến `2026-10-12`.
- Các Sprint 1..12 đã đóng (`status: "closed"`) chỉ chứa các issue đã hoàn tất (`Done`). Toàn bộ các issue chưa hoàn thành từ Sprint trước đều được tự động chuyển tiếp (Spillover) sang `Sprint 13` (`status: "active"`, từ `2026-09-29` đến `2026-10-12`) kèm lịch sử `field: "sprint"` trong `issue_changelog.jsonl` và trường `spillover_count`.
- Chỉ số **Active Sprint WIP Story Points** (dùng cho PRG-011, PRG-012) được định nghĩa là: Tổng `story_points` của tất cả các issue thuộc dự án đó, nằm trong sprint đang active (`current_sprint_id`), và có trạng thái là `In Progress` hoặc `In Review`.

## 5. Quy chuẩn Mã băm Toàn vẹn (Canonical Checksum)
- Mã băm `content_sha256` của từng section trong Markdown bundle được tính toán trên đoạn văn bản chuẩn hóa:
  - Bắt đầu từ dòng tiêu đề `### [DOC-SRCH-20261012-12] ...` cho đến dòng phân cách `---`.
  - Toàn bộ ký tự xuống dòng được chuẩn hóa thành `\n` (LF), cắt bỏ khoảng trắng thừa ở đầu/cuối (`strip()`), và mã hóa UTF-8 trước khi băm SHA-256.

## 6. File Inventory trong Manifest
- `manifest.json` ghi `file_inventory` với đường dẫn tương đối trong `Project1`, kích thước byte và SHA-256 của từng file vật lý.
- Inventory được sắp xếp theo đường dẫn và bao gồm toàn bộ file trong package `Project1`, ngoại trừ chính `manifest.json` để tránh checksum tự tham chiếu. `physical_files_in_v1` vẫn tính cả manifest.

## 7. Namespace và dữ liệu test
- Nạp `evaluation/` (179 test cases) vào namespace benchmark riêng; không đưa gold answer, expected value hoặc expected ACL decision vào index demo.
- `fixtures/` chứa test-only duplicate, thiếu metadata, broken link, timestamp/policy conflict, cross-tenant canary, offboarded author và attachment.

## 8. Work Task, Task Note và vòng đời review (v1.3)
- `structured/work_tasks.jsonl` có 48 Work Task synthetic; `task_id` là định danh 24 hex ổn định cho benchmark, **không phải ID MongoDB đang tồn tại**. `source_issue_key` ánh xạ về Jira-like issue; không nạp đè `issues.jsonl`.
- `structured/task_notes.jsonl` có 48 ghi nhận công việc trỏ đến `task_id` cùng project. `TASK_NOTE` luôn `CONFIRMED` nhưng `knowledge_eligible=false`: không đưa note vào index tri thức chính thức.
- `structured/document_reviews.jsonl` có 58 event review. Chỉ phiên bản `APPROVED` mới đủ điều kiện làm nguồn; bản `DRAFT_SAVED` tiếp theo không thay thế phiên bản đã duyệt. Đây là dữ liệu mô phỏng, không phải event outbox runtime.
- `structured/documents.jsonl` là snapshot tại `as_of_date`: `recorded_at` giữ mốc ghi nội dung; `updated_at` không sớm hơn event review cuối cùng và `status` phản ánh sự kiện duyệt/lưu trữ cuối cùng của tài liệu.
- Fixture `FIX-CONFLICT-POLICY` là test-only và có event `ARCHIVED`; nó không trở thành nguồn chính thức. ADR cũ `DOC-PAY-ADR-001` vẫn mang trạng thái legacy `Superseded`, không bị giả lập thành một sự kiện review hợp lệ vì tác giả không có Project Membership trong NSC-PAY.
- `structured/work_reports.jsonl` có 8 báo cáo kỳ với `document_ids` và `source_task_ids` làm provenance. `source_task_ids` là metadata dataset, không nằm trong DTO Work Report của ứng dụng.
- `evaluation/workflow_cases.jsonl` có 21 ca gold theo kênh `workspace`, `access` và `knowledge`; chỉ dùng trong namespace evaluation. Không khẳng định AI ingestion runtime hiện đã tiêu thụ Work Note events.
- Trong workflow cases, `target_resource_ids` là tài nguyên đang kiểm tra, `source_ids` chỉ chứa nguồn được phép dùng làm đáp án, `must_not_cite` là nguồn bị cấm trích dẫn. Ba trường không được đánh đồng; ca `DENY` luôn có `source_ids: []`.
- Kiểm tra project/tenant membership trước khi trả tiêu đề, snippet hoặc tín hiệu tồn tại; thành viên đã offboard không có quyền hiện tại.
