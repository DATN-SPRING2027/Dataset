# Organization 2 — Nova Solutions: Phần Mềm Quản Lý Nhân Sự, Chấm Công & Nghỉ Phép (Waterfall)

**Trạng thái:** Hoàn thành bộ dataset synthetic kiểm chứng được (`v1.0.0`, `as_of_date = 2026-10-16`); tái tạo 100% bằng `python -X utf8 -B Dataset/Organization2-Nova-Solutions/tools/generate_org.py`. Chưa seed MongoDB runtime của Continuum.

## 1. Bối cảnh nghiệp vụ & Phương pháp quản lý Waterfall
- **Tổ chức chính (`ORG-NOVA`)**: Công ty gia công phần mềm giả lập **Nova Solutions** triển khai hệ thống quản lý Hồ sơ nhân sự, Ca chấm công và Nghỉ phép cho doanh nghiệp khách hàng khoảng 300 nhân viên (**Minh Phát Corp — `ORG-MINHPHAT`**, 312 nhân sự tại Văn phòng Quận 7 & Nhà máy Bình Dương).
- **Phương pháp chủ đạo**: **Waterfall thuần túy** (`methodology = "WATERFALL"`, `sprints = []`, `sprint_id = null` trên toàn bộ 128 task), quản trị theo 6 cổng giai đoạn (`structured/waterfall_phase_gates.jsonl`): Khảo sát → FRS Baseline → Thiết kế Kiến trúc/DB/API → Phát triển → SIT/UAT → Chuyển đổi & Bàn giao.
- **Tình huống thực tế nổi bật**:
  1. **Quay lui giai đoạn Waterfall do lỗi UAT nửa ngày (`NVLEV-19`)**: Phát hiện hủy phép nửa ngày (`0.5`) hoàn thừa thành `1.0` ngày; lưu trữ thiết kế cũ `DOC-NVLEV-DB-001-LEGACY` (`ARCHIVED`), ban hành sổ cái `DOC-NVLEV-DB-002` v2 (`APPROVED`) và kiểm thử lại (`NVLEV-24`).
  2. **Kiểm soát thay đổi khách hàng `CR-2026-08` (`DOC-NVDMG-CR-003`)**: Duyệt làm báo cáo xuất CSV đối soát tăng ca (`NVATD-27`) trong Phase 1, đồng thời hoãn bộ máy tự động quỹ nghỉ bù sang Phase 2 (`NVLEV-29` chuyển `CANCELLED`).
  3. **Biến động nhân sự & đời sống**: BA `NV-U19` nghỉ việc ngày `2026-08-14` (thu hồi quyền, bàn giao cho `NV-U07`), kỹ sư `NV-U09` nghỉ ốm (`07–09/09/2026`), kỹ sư `NV-U13` mất điện/mạng do mưa bão tại Quận 7 (`24–25/09/2026`), điểm chặn `NVDMG-25` chờ xác nhận 7 hồ sơ thai sản.

## 2. Nguồn tham chiếu GitHub & Giới hạn bản quyền
- Tham khảo khái niệm nghiệp vụ từ `orangehrm/orangehrm` (tag `v5.9`, commit `56e23b3b09e7af29317a0943523b825843fff527`, giấy phép `GPL-3.0-or-later`, truy cập `2026-10-28T08:17:08+07:00`, kèm public issues `#1964`, `#1965`, `#1966`).
- **Không sao chép** bất kỳ mã nguồn, schema, tài liệu hay tài sản GPL nào của OrangeHRM; không gán sự kiện giả cho contributor thật; không khẳng định OrangeHRM phát triển theo Waterfall. Chi tiết xem tại [../GITHUB_SOURCES_AND_LICENSES.md](../GITHUB_SOURCES_AND_LICENSES.md).

## 3. Phạm vi Continuum đã chốt & Quy mô gói dữ liệu
- **Không có Team / Không có lịch sử AI Chat / Không có entity Notebook thứ tư**.
- **Đủ 3 dạng Group Note bắt buộc**: `84` `TASK_NOTE` (`knowledge_eligible=false`), `24` `PROJECT_DOCUMENT` (`28` versions, kèm DOCX renditions), `36` `WORK_REPORT` (`DAILY` & `WEEKLY`, luồng `MEMBER→Leader` & `LEADER→Org ADMIN Manager`).
- **Evaluation**: `56` benchmark cases trong `evaluation/benchmark_cases.jsonl`, toàn bộ gắn nhãn `review_status = "unreviewed"` (`"chưa duyệt"`), tách biệt khỏi kho tri thức ứng dụng.
- Đối chiếu chi tiết tại [INGESTION_CONTRACT.md](INGESTION_CONTRACT.md), [../CONTINUUM-DATASET-MAPPING.md](../CONTINUUM-DATASET-MAPPING.md) và [../CONTINUUM_DATA_DICTIONARY.md](../CONTINUUM_DATA_DICTIONARY.md).
