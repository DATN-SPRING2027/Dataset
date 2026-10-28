# Organization 3 — CloudOps Services: Vận Hành SaaS 24/7, Hỗ Trợ Tier-3 & Điều Phối Sự Cố (Kanban)

**Trạng thái:** Hoàn thành bộ dataset synthetic kiểm chứng được (`v1.0.0`, `as_of_date = 2026-10-16`); tái tạo 100% bằng `python -X utf8 -B Dataset/Organization3-CloudOps-Services/tools/generate_org.py`. Chưa seed MongoDB runtime của Continuum.

## 1. Bối cảnh nghiệp vụ & Phương pháp quản lý Kanban
- **Tổ chức chính (`ORG-CLD`)**: Đơn vị vận hành SRE, giám sát SLO và hỗ trợ kỹ thuật Tier-3 đa tenant (kèm tenant khách hàng doanh nghiệp `ORG-FINLEDGER` và đối tác hạ tầng thượng nguồn `ORG-VINACLOUD` phục vụ kiểm thử cách ly đa tenant).
- **Phương pháp chủ đạo**: **Kanban liên tục** (`methodology = "KANBAN"`, `sprints = []`, `sprint_id = null` trên toàn bộ `128` task), điều tiết bằng giới hạn WIP, SLE và các làn ưu tiên `EXPEDITE_P0` / `FIXED_DATE_SLA` / `STANDARD_FLOW` (`structured/kanban_wip_policies.jsonl`).
- **Tình huống thực tế nổi bật**:
  1. **Sự cố SEV-0 ngày lễ Quốc khánh `02/09/2026` (`INC-2026-0902`)**: Bot 24/7 `CLD-BOT-HEARTBEAT` phát hiện mất nhịp lúc `09:12+07:00`; Primary On-Call `CLD-U07` bị đứt cáp quang mưa bão (`DIS-CLD-STORM-01`) nên tự động leo thang sang Secondary `CLD-U08` lúc `09:17+07:00`. Tách bạch rõ **workaround tạm thời** (`CLDINC-9`, `is_temporary_workaround=true`) với **bản sửa nguyên nhân gốc** tách pool `PgBouncer` (`CLDINF-19`, `DOC-CLDINC-RCA-002` v2 bác bỏ giả thuyết DNS sai ở v1).
  2. **Sự cố lệch cấu hình WAF chiều Thứ Bảy `26/09/2026` (`INC-2026-0926`)**: Bot `CLD-BOT-TF-DRIFT` phát hiện rule sửa tay chặn nhầm webhook `FinLedger`; ca trực cuối tuần `CLD-U10` gỡ chặn khẩn cấp (`CLDINF-23`), Tier-3 hướng dẫn replay 148 sự kiện idempotent (`CLDSUP-21`) và khóa sửa tay bằng Terraform (`CLDINF-24`, `DOC-CLDINF-ARC-001` v2).
  3. **Lưu trữ Runbook lỗi & Bàn giao nhân sự**: Lưu trữ `DOC-CLDINF-RUN-006-LEGACY` (`ARCHIVED`) sau sự cố `INC-2026-0818` để thay bằng chuẩn Expand/Contract (`DOC-CLDINF-DB-002` v2); `CLD-U18` nghỉ việc ngày `2026-08-28`; `CLD-U16` nhận bàn giao kiểm thử tải khi `CLD-U11` nghỉ ốm (`DIS-CLD-SICK-01`).

## 2. Nguồn tham chiếu GitHub & Giới hạn bản quyền
- Tham khảo khái niệm nghiệp vụ từ `roxy-wi/IncidentRelay` (tag `v2.4.0`, commit `21ea27d92927242ed499b7584a276f47cb1c68cd`, giấy phép **`Elastic-2.0` — source-available, không phải OSI open-source**, issues `#127`, `#128`, `#130`) và danh mục cấu trúc phân tích sự cố `danluu/post-mortems` (`master` commit `630562e55281ff28961704e8042a7dc9569a96e7`, không có file LICENSE chung).
- **Tuyệt đối không sao chép** mã nguồn, tài liệu hay nội dung chịu điều khoản `Elastic-2.0` hoặc bài postmortem bên thứ ba; không khẳng định IncidentRelay dùng Kanban. Chi tiết tại [../GITHUB_SOURCES_AND_LICENSES.md](../GITHUB_SOURCES_AND_LICENSES.md).

## 3. Phạm vi Continuum đã chốt & Quy mô gói dữ liệu
- **Không có Team / Không có lịch sử AI Chat / Không có entity Notebook thứ tư**.
- **Đủ 3 dạng Group Note**: `81` `TASK_NOTE` (`knowledge_eligible=false`), `24` `PROJECT_DOCUMENT` (`28` versions, kèm 6 file DOCX), `36` `WORK_REPORT` (`DAILY` & `WEEKLY`, `MEMBER` & `LEADER`).
- **Evaluation**: `56` benchmark cases trong `evaluation/benchmark_cases.jsonl` (`review_status = "unreviewed"` / `"chưa duyệt"`).
