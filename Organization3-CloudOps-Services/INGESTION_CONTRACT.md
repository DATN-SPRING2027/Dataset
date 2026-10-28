# Ingestion Contract — Organization 3: CloudOps Services (Kanban v1.0.0)

1. **Tenant & Multi-Tenant Isolation**: Chỉ nạp `ORG-CLD` làm tenant vận hành chính; `ORG-FINLEDGER` và `ORG-VINACLOUD` là tổ chức bên ngoài dùng để kiểm chứng rào cản phân quyền đa tenant (`DENY`).
2. **Kanban Constraint**: `structured/sprints.jsonl` rỗng (`[]`) và toàn bộ `128` task có `sprint_id = null`. Chính sách giới hạn WIP, lịch trực ca và danh mục bot 24/7 lưu tại `structured/kanban_wip_policies.jsonl`, `structured/oncall_schedules.jsonl`, `structured/incidents.jsonl` và `structured/system_bots.jsonl`.
3. **24/7 Bot vs Lịch làm việc con người**:
   - Con người trong ngày thường chỉ hoạt động `08:00–12:00`, `13:00–17:00` và OT tối `17:00–22:00+07:00` (cấm `12:00–13:00`).
   - Hoạt động của con người vào tối muộn, cuối tuần hoặc ngày lễ Quốc khánh `02/09` bắt buộc có `work_mode` thuộc `oncall_incident_response` / `weekend_incident_ot` và nằm trong khung lịch trực hợp lệ tại `structured/oncall_schedules.jsonl`.
   - Sự kiện tự động của bot dùng `actor_type = "system_bot"` và `work_mode = "automated_bot"`.
4. **Ba dạng Group Note & Chống nhầm Workaround**: Task Note luôn có `knowledge_eligible = false` (đặc biệt các Task Note gắn `is_temporary_workaround = true` không bao giờ được coi là bản sửa gốc). Chỉ phiên bản `APPROVED` mới nhất của Project Document không bị `ARCHIVED` và các Work Report `APPROVED` mới có `knowledge_eligible = true`.
5. **Tách biệt Evaluation & Fixtures**: Không nạp `evaluation/benchmark_cases.jsonl` và `fixtures/negative_cases.json` vào database ứng dụng.
