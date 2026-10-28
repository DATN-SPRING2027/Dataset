# Ingestion Contract — Organization 4: MediFlow (Hybrid v1.0.0)

1. **Tenant & Partner Isolation**: Chỉ nạp `ORG-MED` làm tenant chính; `ORG-ANKHANG` (phòng khám đối tác) và `ORG-VIETNOTIFY` (cổng nhắn tin đối tác) dùng để kiểm chứng cách ly đa tenant (`DENY`) và nguồn gốc phản hồi thực địa.
2. **Hybrid Sprint & Milestone Rules**:
   - `structured/sprints.jsonl` chứa 15 Sprint của 3 dự án `HYBRID` (`MED-REG`, `MED-APT`, `MED-ADM`): mỗi dự án có 4 Sprint `COMPLETED` (không chứa bất kỳ task mở nào) và đúng 1 Sprint `ACTIVE` (`S5`). Dự án `MED-PIL` có `sprint_id = null` trên toàn bộ 32 task.
   - Cổng Milestone và nhật ký phản hồi phòng khám lưu tại `structured/milestones.jsonl` và `structured/clinic_feedback_log.jsonl`. Phản hồi có `decision_status = "PENDING_EVALUATION"` tuyệt đối không được coi là quy tắc đã có hiệu lực.
3. **Ranh giới Phi Lâm Sàng & Quyền Riêng Tư**: 100% dữ liệu hành chính giả lập; cấm nạp dữ liệu bệnh án thật hoặc mở cờ `include_phone_in_excel_export`.
4. **Ba dạng Group Note & Tách biệt Evaluation**: `TASK_NOTE` luôn có `knowledge_eligible = false`; chỉ nạp phiên bản `APPROVED` mới nhất của `PROJECT_DOCUMENT` không bị `ARCHIVED` và các `WORK_REPORT` `APPROVED`. Không nạp `evaluation/benchmark_cases.jsonl` và `fixtures/negative_cases.json` vào database ứng dụng.
