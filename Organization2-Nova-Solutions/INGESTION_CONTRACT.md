# Ingestion Contract — Organization 2: Nova Solutions (Waterfall v1.0.0)

1. **Tenant & IAM Scope**: Chỉ nạp `ORG-NOVA` làm tenant chính trên Continuum; các bản ghi `ORG-MINHPHAT` là đối tác khách hàng dùng cho kiểm thử cách ly đa tenant (`DENY`) và truy vết biên bản UAT/CR.
2. **Waterfall Constraint**: `structured/sprints.jsonl` rỗng (`[]`) và toàn bộ `128` task trong `structured/tasks.jsonl` có `sprint_id = null`. Tiến độ cổng giai đoạn lưu tại `structured/waterfall_phase_gates.jsonl` và yêu cầu thay đổi lưu tại `structured/change_requests.jsonl` (`DATASET_METADATA_ONLY` cho tới khi Continuum mở bảng milestone/gate riêng).
3. **Ba dạng Group Note**:
   - `structured/task_notes.jsonl`: `noteType = TASK_NOTE`, `status = CONFIRMED`, `knowledge_eligible = false` (cấm đưa vào index tri thức chính thức).
   - `structured/project_documents.jsonl` + `structured/document_versions.jsonl`: Chỉ nạp phiên bản `latest_approved_version_number` của tài liệu không bị `ARCHIVED` / `REJECTED` / `DRAFT` khi có runtime consumer.
   - `structured/work_reports.jsonl`: Báo cáo `MEMBER` do `TEAM_LEADER` hoặc `ADMIN` duyệt; báo cáo `LEADER` bắt buộc do Organization `ADMIN` (`NV-U01`, `NV-U02`) duyệt. Chỉ bản `APPROVED` mới có `knowledge_eligible = true`.
4. **Lịch làm việc & Bàn giao**: Chuẩn `+07:00`, hành chính `08:00–12:00` & `13:00–17:00` (không có hoạt động người dùng `12:00–13:00`), OT tối `17:00–22:00`, tuân thủ ngày lễ Việt Nam và các cửa sổ vắng mặt trong `structured/disruption_events.jsonl`.
5. **Tách biệt Evaluation & Fixtures**: Không nạp `evaluation/benchmark_cases.jsonl` (`review_status = "unreviewed"`) và `fixtures/negative_cases.json` vào cơ sở dữ liệu sản phẩm.
