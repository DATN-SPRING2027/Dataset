# Continuum AI — Data Dictionary, Contract Alignment & Import Specification

Tài liệu này định nghĩa từ điển dữ liệu (Data Dictionary), quy tắc chuyển đổi ID/enum, đối chiếu contract thực tế giữa `Dataset` và mã nguồn `DATN_BE` / `DATN_FE` (kiểm chứng ngày `2026-10-28`), thứ tự phụ thuộc khi xây dựng công cụ nạp (importer) trong tương lai và các khoảng trống runtime hiện hành.

> **Trạng thái quan trọng:** Toàn bộ bốn gói dữ liệu (`Project1`, `Organization2-Nova-Solutions`, `Organization3-CloudOps-Services`, `Organization4-MediFlow`) là bộ chuẩn dữ liệu tái lập được trên đĩa. **Chưa thực hiện seed vào MongoDB và chưa có consumer AI/SAG tự động tiêu thụ outbox trong task này.**

---

## 1. Phân Loại Trạng Thái Hỗ Trợ (`support_status`)

Mọi tệp và trường dữ liệu trong bốn organization được gắn rõ vào một trong năm nhóm:

| Mã phân loại | Ý nghĩa kỹ thuật | Quy tắc xử lý khi viết Importer sau này |
| :--- | :--- | :--- |
| **`API_SUPPORTED`** | Đã có HTTP endpoint và DTO khớp trực tiếp trong `DATN_BE` (`04-api-inventory.yaml`, `iam`, `task/workspace`, `capture`). | Có thể gọi qua API ứng dụng nếu chấp nhận `createdAt = now()` và `actor = currentUser`. |
| **`IMPORTER_REQUIRED`** | Thực thể/trường có trong schema MongoDB của Continuum nhưng muốn giữ nguyên lịch sử thời gian (`created_at`, `reviewed_at`), tác giả lịch sử (bao gồm nhân sự đã `SUSPENDED`/`REMOVED`) hoặc chuỗi `task_events` thì không thể đi qua HTTP API thông thường. | Bắt buộc dùng script/admin-importer chuyên dụng có kiểm tra khóa ngoại, idempotent theo `continuum_id_mapping.jsonl` và chỉ chạy trên môi trường đích được Thang phê duyệt. |
| **`DATASET_METADATA_ONLY`** | Siêu dữ liệu mô phỏng bối cảnh dự án chưa có collection riêng trong runtime Continuum hiện tại (ví dụ: cổng giai đoạn Waterfall, chính sách WIP Kanban, lịch trực ca, nhật ký phản hồi phòng khám, cửa sổ mưa bão/nghỉ ốm, tổ chức đối tác bên ngoài). | Giữ ở tầng metadata kiểm chứng timeline và provenance; **không tự sửa schema/migration BE** để ép nạp các bảng này khi chưa có thiết kế sản phẩm. |
| **`EVALUATION_ONLY`** | Câu hỏi benchmark, đáp án chuẩn (`expected_answer`), `mandatory_points`, `must_not_cite` và bộ `negative_cases.json`. | **Tuyệt đối cấm nạp** vào MongoDB ứng dụng, vector index hoặc prompt của hệ thống AI được đánh giá. |
| **`NOT_YET_AVAILABLE`** | Tính năng đã có định hướng kiến trúc hoặc outbox chờ nhưng chưa có runtime consumer/service hoạt động end-to-end (ví dụ: pipeline tiêu thụ `work_note_CaptureOutbox` sang SAG/vector index, luồng handover runtime tự động). | Ghi nhận rõ là khoảng trống runtime; không tuyên bố đã tích hợp AI chỉ vì dataset có cờ `knowledge_eligible`. |

---

## 2. Đối Chiếu Nguồn Sự Thật Giữa `DATN_BE`, `DATN_FE` & Tài Liệu Cũ

Khi rà soát mã nguồn ngày `2026-10-28`, các điểm khác biệt sau đã được xác minh và chuẩn hóa:

1. **Ba dạng Group Note theo xác nhận của Thang vs `capture` service**:
   - Trong `DATN_BE/src/services/capture/domain/work-note.enums.ts`, một collection `work_notes` (kèm `work_note_versions`) phục vụ đa hình qua `WorkNoteType`:
     - Dạng 1 (**Task Note** — note trong tab công việc): `noteType = TASK_NOTE`, trạng thái `CONFIRMED | ARCHIVED`, gắn `taskId` bắt buộc, **không có luồng trình duyệt/phê duyệt tri thức** (`knowledge_eligible = false`).
     - Dạng 2 (**Project Document** — tài liệu dự án): `noteType = PROJECT_DOCUMENT`, `documentType` thuộc `REQUIREMENT | ARCHITECTURE | DESIGN | DATABASE_DESIGN | API_SPECIFICATION | TECHNICAL_SPECIFICATION`, vòng đời phiên bản `DRAFT | PENDING_REVIEW | CHANGES_REQUESTED | APPROVED | REJECTED | ARCHIVED`, cấm tự duyệt (`reviewer != author`).
     - Dạng 3 (**Work Report** — báo cáo công việc): `noteType = WORK_REPORT`, `frequency` thuộc `DAILY | WEEKLY`, `reportScope` thuộc `MEMBER | LEADER`. Trong `capture-acl.helper.ts` và `work-report-settings.service.ts`:
       - Báo cáo `MEMBER` do thành viên thường tạo, được `TEAM_LEADER` của dự án hoặc Organization `ADMIN` duyệt (`reviewer != author`).
       - Báo cáo `LEADER` do `TEAM_LEADER` của dự án tạo, **chỉ Organization `ADMIN` (Manager cấp tổ chức)** mới có quyền duyệt (`reviewer != author`).
       - Trạng thái quá hạn nộp **không phải** là một giá trị của `WorkNoteStatus`; runtime biểu diễn bằng bản ghi `status = "DRAFT"` kết hợp tính toán hạn nộp (`is_overdue = true`, `roster_submission_state = "OVERDUE"`).
   - **Không tạo entity `Notebook` thứ tư**; `Document/research-docs/01_MVP_SCOPE.md` là tài liệu phạm vi nghiên cứu ban đầu, còn enum/ACL thực tế tuân theo `DATN_BE/src/services/capture/`.
2. **Task Priority & Subtask Depth (`DATN_BE/src/services/task/workspace/`)**:
   - `TaskPriority` trong `DATN_BE` và `DATN_FE/src/lib/queries/tasks/useTasks.ts` chỉ gồm `LOW | MEDIUM | HIGH` (không có `CRITICAL` hay `URGENT` như Jira mặc định). Trong Org 1 (`Project1`), các Jira-like issue giữ nguyên thang Jira lịch sử ở `issues.jsonl`, còn `work_tasks.jsonl` và toàn bộ `tasks.jsonl` của Org 2, 3, 4 tuân thủ nghiêm ngặt `LOW | MEDIUM | HIGH`.
   - Subtask chỉ cho phép tối đa **1 cấp con** (`parent.parentId == null`); mỗi project chỉ có tối đa **1 Sprint `ACTIVE`**; Sprint `COMPLETED` không được chứa task mở (`TODO | IN_PROGRESS | IN_REVIEW | BLOCKED`); chuyển sang `BLOCKED`, `CANCELLED` hoặc mở lại bắt buộc có `reason >= 5` ký tự.
3. **Team & Lịch sử AI Chat**:
   - Xác nhận từ mã nguồn `DATN_BE/src/services/iam/` và quyết định của Thang: **không có entity Team / Team Membership**; quyền được kiểm soát trực tiếp qua `OrganizationMembership`, `ProjectMembership` và các mã role tường minh `ADMIN` (cấp org), `TEAM_LEADER` / `MEMBER` (cấp project).
   - **Không tạo hay seed lịch sử AI Chat** trong cả bốn gói dataset.
4. **Khoảng trống Outbox -> AI Index**:
   - `DATN_BE/src/services/capture` có ghi sự kiện sang bảng outbox khi phê duyệt tài liệu/báo cáo, nhưng hiện chưa có consumer runtime nối tự động sang chỉ mục RAG/SAG. Do đó cờ `knowledge_eligible` trong dataset được xếp loại `IMPORTER_REQUIRED` / `NOT_YET_AVAILABLE` để hướng dẫn bộ lọc indexer tương lai.

---

## 3. Từ Điển Trường Dữ Liệu Cốt Lõi (Field-Level Mapping)

### 3.1. IAM: Organization, User, Membership & Role Assignment

| File nguồn (`structured/`) | Trường nguồn | Kiểu | Bắt buộc | Đích Continuum (`DATN_BE`) | Quy tắc chuyển đổi & Validation | Hỗ trợ |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- |
| `organizations.jsonl` | `org_id` / `continuum_org_id` | `string` / `hex24` | Có | `organizations._id` | Ánh xạ 1–1 qua `continuum_id_mapping.jsonl`. Chỉ nạp organization có `is_primary_continuum_tenant = true`; các org khách hàng/đối tác là `DATASET_METADATA_ONLY`. | `IMPORTER_REQUIRED` |
| `organizations.jsonl` | `plan` | `enum` | Có | `organizations.plan` | `FREE \| ENTERPRISE` | `API_SUPPORTED` |
| `users.jsonl` | `user_id` / `continuum_user_id` | `string` / `hex24` | Có | `users._id` | Email bắt buộc chữ thường, kết thúc bằng `.invalid` (`SAFE_EMAIL_RE`), không dùng mật khẩu thật. | `IMPORTER_REQUIRED` |
| `users.jsonl` | `status` | `enum` | Có | `users.status` | `ACTIVE \| SUSPENDED \| PENDING_INVITE`. Nhân sự đã nghỉ việc (`left_at != null`) mang `SUSPENDED`. | `IMPORTER_REQUIRED` |
| `users.jsonl` | `department_label`, `job_title` | `string` | Không | Hồ sơ hiển thị / Metadata | Chỉ dùng để hiển thị bối cảnh nghiệp vụ; **tuyệt đối không dùng để suy diễn quyền hệ thống**. | `DATASET_METADATA_ONLY` |
| `organization_memberships.jsonl` | `organization_id`, `user_id`, `status` | `string`, `enum` | Có | `organization_members` | `PENDING_INVITE \| ACTIVE \| SUSPENDED \| REMOVED`. Nhân sự offboard chuyển `REMOVED`. | `IMPORTER_REQUIRED` |
| `projects.jsonl` | `project_id`, `code`, `visibility`, `status`, `created_by` | `string`, `enum` | Có | `projects` | `code` khớp `^[A-Z0-9]{2,10}$`, duy nhất trong org; `visibility` thuộc `PRIVATE \| PUBLIC`; `status` thuộc `ACTIVE \| ARCHIVED`. | `API_SUPPORTED` |
| `projects.jsonl` | `methodology` | `enum` | Có | Metadata cấp project | `WATERFALL \| KANBAN \| HYBRID \| AGILE`. Quy định việc project có dùng Sprint hay không. | `DATASET_METADATA_ONLY` |
| `project_memberships.jsonl` | `project_id`, `user_id`, `status` | `string`, `enum` | Có | `project_members` | `ACTIVE \| INACTIVE`; cấm gán user thuộc organization khác vào project nội bộ. | `API_SUPPORTED` |
| `role_assignments.jsonl` | `organization_id`, `project_id`, `user_id`, `role_code` | `string`, `enum` | Có | `organization_member_roles` / `project_member_roles` | `ADMIN` bắt buộc `project_id = null`; `TEAM_LEADER` bắt buộc có `project_id`; `MEMBER` hợp lệ ở cả hai cấp. | `API_SUPPORTED` |

### 3.2. Task Workspace: Sprint, Task, Checklist, Comment, Worklog & Event

| File nguồn (`structured/`) | Trường nguồn | Kiểu | Bắt buộc | Đích Continuum (`DATN_BE`) | Quy tắc chuyển đổi & Validation | Hỗ trợ |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- |
| `sprints.jsonl` | `sprint_id`, `project_id`, `status`, `start_date`, `end_date` | `string`, `enum`, `date` | Tùy mô hình | `sprints` | `PLANNED \| ACTIVE \| COMPLETED`. Rỗng (`[]`) với project `WATERFALL` / `KANBAN`. Tối đa 1 `ACTIVE` sprint/project; sprint `COMPLETED` không chứa task mở. | `IMPORTER_REQUIRED` |
| `tasks.jsonl` (Org 1: `work_tasks.jsonl`) | `task_id`, `key`, `type`, `status`, `priority` | `string`, `enum` | Có | `tasks` | `key` khớp `^[A-Z0-9]{2,10}-[1-9][0-9]*$`; `type`: `TASK \| BUG \| STORY`; `status`: `TODO \| IN_PROGRESS \| IN_REVIEW \| BLOCKED \| DONE \| CANCELLED`; `priority`: `LOW \| MEDIUM \| HIGH`. | `IMPORTER_REQUIRED` |
| `tasks.jsonl` | `parent_id`, `sprint_id`, `steps`, `labels`, `completed_at` | hỗn hợp | Tùy chọn | `tasks` | `parent_id` tối đa 1 cấp; `steps` <= 50 mục `{id, text, done, order}`; `completed_at != null` khi và chỉ khi `status == "DONE"`. | `API_SUPPORTED` |
| `tasks.jsonl` | `waterfall_phase_id`, `kanban_class_of_service`, `milestone_id`, `incident_id`, `disruption_id`, `spillover_count`, `work_mode`, `is_overtime` | hỗn hợp | Không | Metadata truy vết mô phỏng | Phục vụ kiểm chứng phương pháp quản lý, OT buổi tối, ca trực và bàn giao; lưu ngoài DTO HTTP chuẩn nếu import qua API. | `DATASET_METADATA_ONLY` |
| `task_comments.jsonl` | `comment_id`, `task_id`, `author_id`, `actor_type`, `body`, `created_at` | `string` | Có | `task_comments` | `1 <= len(body) <= 5000`; `created_at >= task.created_at`. Nếu `actor_type == "system_bot"` cần ánh xạ sang tài khoản tích hợp khi nạp. | `IMPORTER_REQUIRED` |
| `task_worklogs.jsonl` | `worklog_id`, `task_id`, `author_id`, `minutes`, `logged_at` | `string`, `int` | Có | `task_worklogs` | `1 <= minutes <= 1440`; `author_id` thuộc thành viên dự án và không nằm trong cửa sổ nghỉ ốm/bão/offboard. | `IMPORTER_REQUIRED` |
| `task_events.jsonl` | `event_id`, `task_id`, `type`, `from_status`, `to_status`, `reason`, `occurred_at` | `string` | Có | `task_events` | Chuỗi thời gian đơn điệu tăng; kiểm tra ma trận chuyển trạng thái hợp lệ và `reason >= 5` ký tự khi `BLOCKED` / `CANCELLED` / mở lại. | `IMPORTER_REQUIRED` |

### 3.3. Ba Dạng Group Note (`capture` Service) & Evaluation

| File nguồn | Trường cốt lõi | Đích Continuum (`DATN_BE`) | Quy tắc nghiệp vụ & Ranh giới tri thức | Hỗ trợ |
| :--- | :--- | :--- | :--- | :--- |
| `structured/task_notes.jsonl` | `note_id`, `task_id`, `author_id`, `status="CONFIRMED"`, `accomplishments`, `approach`, `reason`, `knowledge_eligible=false`, `is_temporary_workaround` | `work_notes` (`noteType = TASK_NOTE`) | Gắn trực tiếp vào tab công việc của task. **Luôn đặt `knowledge_eligible = false`** để không trộn ghi chú nháp/workaround tạm thời vào nguồn tri thức chuẩn. | `IMPORTER_REQUIRED` |
| `structured/project_documents.jsonl` + `document_versions.jsonl` (Org 1: `documents.jsonl` + `document_reviews.jsonl`) | `document_id`, `document_type`, `status`, `created_by`, `version_number`, `reviewed_by`, `file_path` (`.md`), `rendition_paths` (`.docx`) | `work_notes` (`noteType = PROJECT_DOCUMENT`) + `work_note_versions` | Cấm tự duyệt (`reviewed_by != author_id`). Chỉ phiên bản `APPROVED` mới nhất của tài liệu không bị `ARCHIVED` mới có `knowledge_eligible = true`. | `IMPORTER_REQUIRED` (`NOT_YET_AVAILABLE` cho auto-RAG consumer) |
| `structured/work_report_settings.jsonl` + `work_reports.jsonl` | `report_id`, `member_id`, `report_scope` (`MEMBER \| LEADER`), `frequency` (`DAILY \| WEEKLY`), `period_start`, `period_end`, `status`, `is_overdue`, `reviewed_by`, `document_ids`, `source_task_ids` | `work_report_settings` + `work_notes` (`noteType = WORK_REPORT`) | `MEMBER` duyệt bởi `TEAM_LEADER` hoặc `ADMIN`; `LEADER` duyệt **duy nhất bởi Org `ADMIN`**. Trường `source_task_ids` là `DATASET_METADATA_ONLY` (DTO HTTP không nhận trực tiếp). | `IMPORTER_REQUIRED` |
| `evaluation/benchmark_cases.jsonl` (Org 1: `evaluation/*.jsonl`) & `fixtures/negative_cases.json` | `case_id`, `principal_id`, `question`, `expected_answer`, `source_ids`, `must_not_cite`, `review_status="unreviewed"` | Bộ chấm điểm độc lập bên ngoài DB | Toàn bộ câu hỏi synthetic mới tạo mang `review_status = "unreviewed"` (`"chưa duyệt"`), chờ 2 người độc lập nghiệm thu trước khi đóng băng gold cuối. | `EVALUATION_ONLY` |

---

## 4. Thứ Tự Phụ Thuộc Khi Nhập (Import Dependency Order) & Giới Hạn Backdating

Khi nhóm phát triển công cụ import trong một task riêng đã được xác nhận môi trường đích:

1. **Bước 1 — Tenant & Users**: Nạp `organizations` (chỉ primary org của gói) -> `users` (tạo tài khoản không mật khẩu thật, giữ trạng thái `ACTIVE`/`SUSPENDED`).
2. **Bước 2 — Memberships & Explicit Roles**: Nạp `organization_memberships` -> `role_assignments` cấp org (`ADMIN`/`MEMBER`) -> `projects` -> `project_memberships` -> `role_assignments` cấp project (`TEAM_LEADER`/`MEMBER`).
3. **Bước 3 — Sprints & Tasks (2 pha cha–con)**: Nạp `sprints` (nếu có) -> nạp các `tasks` gốc (`parent_id = null`) -> nạp các subtask 1 cấp (`parent_id != null`) -> nạp `task_comments`, `task_worklogs`, `task_events`.
4. **Bước 4 — Group Notes (3 dạng)**: Nạp `task_notes` -> nạp `project_documents` kèm `document_versions` và tệp đính kèm -> nạp `work_report_settings` và `work_reports`.
5. **Giới hạn Actor/Timestamp qua HTTP API**: Các REST API hiện tại của `DATN_BE` tự gán `createdAt = new Date()` và lấy `userId` từ JWT hiện hành. Do đó **không được gọi tuần tự REST API thường nếu mục tiêu là bảo toàn lịch sử 6 tháng (`2026-04..2026-10`) và tác giả đã offboard**; phải viết importer tầng repository/admin script có kiểm tra `continuum_id_mapping.jsonl` để chạy lại không sinh bản ghi trùng (idempotent upsert) và hỗ trợ xóa sạch theo `dataset_batch_id` khi rollback.
