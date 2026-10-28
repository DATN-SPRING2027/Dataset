# Organization 4 — MediFlow: Nền Tảng Quản Lý Lịch Hẹn & Tiếp Đón Hành Chính Phòng Khám (Hybrid)

**Trạng thái:** Hoàn thành bộ dataset synthetic kiểm chứng được (`v1.0.0`, `as_of_date = 2026-10-16`); tái tạo 100% bằng `python -X utf8 -B Dataset/Organization4-MediFlow/tools/generate_org.py`. Chưa seed MongoDB runtime của Continuum.

## 1. Bối cảnh nghiệp vụ, Ranh giới phi lâm sàng & Phương pháp Hybrid
- **Tổ chức chính (`ORG-MED`)**: Công ty sản phẩm giả lập **MediFlow** triển khai thử nghiệm (Pilot) nền tảng quản lý lịch làm việc bác sĩ, đặt lịch hẹn và hàng đợi tiếp đón hành chính cho **Phòng khám Đa khoa An Khang (`ORG-ANKHANG`)**, tích hợp cổng tin nhắn giả lập **VietNotify (`ORG-VIETNOTIFY`)**.
- **Ranh giới dữ liệu nghiêm ngặt**: **100% dữ liệu hành chính synthetic** (mã `AK-PAT-XXXXXX`, đuôi email `.invalid`, che mặt nạ SĐT `***-***-482`). **Tuyệt đối không chứa** bệnh án lâm sàng, chẩn đoán, xét nghiệm, đơn thuốc hay PII người thật.
- **Phương pháp quản lý cấp project (Hybrid)**:
  - Ba dự án sản phẩm (`MED-REG`, `MED-APT`, `MED-ADM`) vận hành theo **Hybrid**: hội tụ theo 4 cổng Milestone (`MS-MED-01..04`) và phát triển qua **5 Sprint 2 tuần/dự án** (`15` sprints tổng cộng: `S1..S4` `COMPLETED` sạch 100% không còn task dở dang, `S5` là Sprint `ACTIVE` duy nhất mỗi dự án).
  - Dự án triển khai thực địa (`MED-PIL`) quản trị theo cổng Milestone không chia Sprint (`methodology = "WATERFALL"`, `sprint_id = null`), chứng minh mô hình quản lý thuộc về từng project.
- **Tình huống thực tế nổi bật**:
  1. **Phân loại phản hồi từ Demo M2 (`structured/clinic_feedback_log.jsonl`)**: Chấp thuận `CFB-2026-01` (cho phép `RECEPTION_SHIFT_LEAD` dời lịch hàng loạt có kiểm toán tại `MEDAPT-18`, `DOC-MEDAPT-REQ-001` v2); **Từ chối** `CFB-2026-02` (xuất Excel kèm SĐT đầy đủ tại `DOC-MEDADM-EXPORT-006` `REJECTED`, `MEDADM-30` `CANCELLED`, giữ `include_phone_in_excel_export = false`); giữ `CFB-2026-03` (khóa đặt lịch 30 ngày) ở trạng thái **phản hồi chưa duyệt** (`DOC-MEDAPT-DES-005` v2 `PENDING_REVIEW`).
  2. **Mưa bão làm Spillover Sprint & Lùi cổng Milestone M3**: Sự cố đứt cáp mưa bão cuối Sprint 4 (`DIS-MED-STORM-01` với `MED-U15`) khiến `MEDAPT-25` phải rollover sang `MEDAPT-S5` (`spillover_count = 1`) và lùi mốc sẵn sàng Pilot `MS-MED-03` từ `08/10` sang `12/10` sau buổi diễn tập ca trực Thứ Bảy `10/10/2026` (`OC-MED-PILOT-SAT-1010`).
  3. **Bàn giao nhân sự**: `MED-U18` nghỉ việc cuối Sprint 1 (`2026-08-21`, giao cho `MED-U09`); `MED-U10` nghỉ phép ốm hành chính giữa Sprint 3 (`10–11/09/2026`, giao `MEDAPT-15` cho `MED-U11`).

## 2. Nguồn tham chiếu GitHub & Giới hạn bản quyền
- Tham khảo khái niệm hành chính từ `openmrs/openmrs-core` (`2.8.10` / commit `0755f785f7d237a7a2e9d9f4e76aff43b7613ad3`, giấy phép `MPL-2.0` kèm *Healthcare Disclaimer*) và tài liệu cấu hình `openmrs/openmrs-contrib-o3-docs` (`main` commit `3a0da981e31e224a467a4432df2a65cb8dfdfe7b`, `MPL-2.0`, file `configure-patient-management.mdx`).
- **Không sao chép** bất kỳ mã nguồn, tài liệu hay mô hình lâm sàng nào của OpenMRS; không khẳng định OpenMRS dùng Hybrid. Xem chi tiết tại [../GITHUB_SOURCES_AND_LICENSES.md](../GITHUB_SOURCES_AND_LICENSES.md).

## 3. Phạm vi Continuum đã chốt & Quy mô gói dữ liệu
- **Không có Team / Không có lịch sử AI Chat / Không có entity Notebook thứ tư**.
- **Đủ 3 dạng Group Note**: `82` `TASK_NOTE` (`knowledge_eligible=false`), `24` `PROJECT_DOCUMENT` (`28` versions, kèm 6 file DOCX), `36` `WORK_REPORT` (`DAILY` & `WEEKLY`, `MEMBER` & `LEADER`).
- **Evaluation**: `56` benchmark cases trong `evaluation/benchmark_cases.jsonl` (`review_status = "unreviewed"` / `"chưa duyệt"`).
