# Bộ Dữ Liệu Northstar Commerce v1.3 — Hướng Dẫn Vận Hành & Khai Thác

## 1. Bối cảnh kịch bản (Dataset Scenario)
Bộ dữ liệu mô phỏng công ty công nghệ hư cấu **Northstar Commerce Systems**, đang xây dựng nền tảng thương mại điện tử đa tenant (multi-tenant ecommerce platform) cho khách hàng merchant pilot là **Meridian Outfitters**, tích hợp với đối tác cổng thanh toán **PulsePay Network**.
- Nguồn cảm hứng domain và công nghệ: Dự án mã nguồn mở **Bagisto** (kiến trúc Laravel + Vue.js: https://github.com/bagisto/bagisto).
- **Tính chân thực vận hành (Enterprise Realism v1.2)**:
  - **Múi giờ & Khung giờ làm việc**: Chuẩn giờ Việt Nam `UTC+07:00`. Giờ hành chính `08:00–12:00` và `13:00–17:00` (nghỉ trưa `12:00–13:00` không phát sinh commit/comment của con người).
  - **Tăng ca (Overtime - OT)**: Khung giờ OT buổi tối từ `17:00–22:00+07:00`, tập trung cao ở 2 dự án `At Risk` (`NSC-CHKO`, `NSC-PAY`) và các ngày cuối Sprint, có đánh dấu `is_overtime`, `overtime_hours`, `work_mode` và `business_hours_elapsed`.
  - **Lịch nghỉ Thứ Bảy, Chủ Nhật & 5 Ngày Lễ Việt Nam**: Nhân sự nghỉ Thứ Bảy, Chủ Nhật và 5 ngày lễ (`2026-04-27`, `2026-04-30`, `2026-05-01`, `2026-09-01`, `2026-09-02`) = **123 ngày làm việc chính thức**. Chỉ có 3 ngày Thứ Bảy trực chiến sự cố P0/P1 (`2026-08-29`, `2026-09-26`, `2026-10-10` từ `17:00–22:00+07:00`) và 4 Bot tự động chạy 24/7.
- **Tính tổng hợp (Synthetic)**: 100% dữ liệu nhân sự, công ty, ticket, thẻ thanh toán, sự cố và tài liệu đều là dữ liệu giả lập phục vụ kiểm thử và demo. Mọi địa chỉ email sử dụng tên miền an toàn `example.invalid`.

## 2. Quy mô dữ liệu chuẩn (Canonical Data Scale)
- **3 Tổ chức (Organizations)**: `ORG-NSC` (Northstar), `ORG-MERIDIAN` (Meridian), `ORG-PULSEPAY` (PulsePay).
- **10 Phòng ban (Departments)**: 8 phòng ban Northstar, 1 Merchandising (Meridian), 1 API Ops (PulsePay).
- **74 Hồ sơ thành viên (Members)**: 60 nhân sự nội bộ Northstar, 8 nhân sự Meridian, 6 nhân sự PulsePay. Trong đó có **71 thành viên active** (100% đều tham gia hoạt động trong dự án) và **3 cựu nhân viên** (`M-018`, `M-045`, `M-070`, đã thu hồi quyền và bàn giao toàn bộ việc trước ngày nghỉ).
- **15 Nhóm truy cập**: Cách ly tuyệt đối giữa nhân sự nội bộ Northstar và cộng tác viên bên ngoài (`external_collaborator`).
- **8 Dự án (Projects)**: `NSC-CAT`, `NSC-SRCH`, `NSC-CART`, `NSC-CHKO`, `NSC-PAY`, `NSC-INV`, `NSC-ORD`, `NSC-PLAT` với tỷ lệ hoàn thành phân hóa theo sức khỏe dự án (`On Track` ~68–75% Done vs `At Risk` ~35–38% Done).
- **104 Sprints**: 13 sprint liên tiếp × 8 dự án. Sprints 1..12 đã đóng (0 issue mở bị bỏ quên; toàn bộ việc dở dang được spillover sang Sprint 13 kèm lịch sử chuyển Sprint).
- **180 Ngày giả lập (Simulation Window)**: Từ `2026-04-16` đến `2026-10-12` (128 weekdays = **123 ngày làm việc chính thức** + 5 ngày lễ Việt Nam).
- **1,434 Bản ghi tài liệu logic (Logical Documents)**: Được đăng ký đầy đủ trong `structured/documents.jsonl`; DOCX rendition dùng chung canonical ID với Markdown.
- **Đúng 2.500 Jira-like Issues**: Có cấu trúc phân cấp `parent_key` (Epic -> Story/Task/Bug), vòng lặp review/rework/unblock phi tuyến tính, `2,814` bình luận đa lượt (gồm cả nhân sự, đối tác và 4 bot hệ thống) và `8,377` bản ghi lịch sử chuyển đổi trạng thái/sprint/assignee.
- **Work Task/Note v1.3**: 48 task bản địa ánh xạ từ issue, 48 Task Note, 58 event review tài liệu và 8 Work Report; tất cả là synthetic, không phải seed MongoDB.
- **179 Evaluation Cases** và **84 Functional Test Cases**: Đầy đủ các kịch bản RAG, ACL đa tenant, Analytics OT/Spillover, Ingestion và Edge Cases.

## 3. Kiến trúc đóng gói: File vật lý vs Bản ghi logic
Package `Project1` giữ dưới giới hạn **160 file vật lý** (159 files):
- **56 Monthly Markdown Bundles**: 8 dự án × 7 tháng lưu trữ 1.373 bản ghi cập nhật kỹ thuật trên **123 ngày làm việc chính thức** (20 ngày đầu có 12 docs/ngày, 103 ngày sau có 11 docs/ngày) sử dụng 12 mẫu cấu trúc tài liệu khác nhau.
- **10 DOCX canonical sources** và **8 DOCX renditions**.
- **43 Tài liệu Markdown formal** và **8 Fixture records**.
- Tổng cộng: 1.373 + 10 + 43 + 8 = **1,434 Logical Documents**.

## 4. Thứ tự nạp dữ liệu khuyến nghị (Ingestion Pipeline)
1. **Thực thể nền tảng**: `organizations` → `departments` → `members` → `access_groups` → `group_memberships`.
2. **Dự án & Sprints**: `projects` → `sprints` → `project_memberships`.
3. **Tiến độ và nhiệm vụ**: `issues` → `issue_comments` → `issue_changelog`; tiếp theo `work_tasks` → `task_notes` và `work_reports` theo `source_issue_key`/`task_id`.
4. **Nạp kho tài liệu (Content Ingestion)**:
   - Nạp Markdown canonical trong `documents/markdown/formal/`; DOCX rendition dùng chung `canonical_document_id` nên không tạo chunk trùng.
   - Phân đoạn 56 bundles trong `documents/markdown/bundles/` theo các thẻ neo `<a id="..."></a>` để tạo đúng 1.373 chunks tài liệu tương ứng với `structured/documents.jsonl`.
5. **Đánh chỉ mục vector & tìm kiếm**:
   - Gắn nhãn `access_groups`, `classification`, và `scope` vào từng chunk.
   - Áp dụng bộ lọc ACL trước khi retrieval (Pre-filtering).
6. **Test nghiệp vụ và benchmark**:
   - Test chức năng lấy từ `structured/functional_test_cases.jsonl`; đối chiếu requirement và kết quả trong `structured/test_execution_results.jsonl`.
   - Bộ dữ liệu kiểm thử retrieval/ACL/ingestion/workflow lấy từ `evaluation/` vào namespace riêng biệt, **không đưa gold answers vào index demo**. Task Note không là nguồn tri thức chính thức; Document/Report được duyệt chỉ đủ điều kiện làm nguồn khi có consumer runtime.

## 5. Hướng dẫn sử dụng Dataset_Catalog.xlsx
1. Mở file `Dataset_Catalog.xlsx` bằng Microsoft Excel hoặc LibreOffice Calc.
2. **Tab Overview**: Xem tổng quan chỉ số KPI, biểu đồ phân bố trạng thái Jira issue và bảng tiến độ 8 dự án.
3. **Tab Sprints**: Tra cứu 104 sprint của 8 dự án, xem mục tiêu sprint và trạng thái active/closed.
4. **Tab Documents**: Sử dụng bộ lọc (AutoFilter) theo `project_id`, `scope`, `is_overtime`, `work_mode`, `classification`, `status` hoặc `format`.
5. **Tab Issues**: Tra cứu 2.500 ticket theo `status`, `sprint_id`, `parent_key`, `is_overtime`, `overtime_hours`, `spillover_count`, `assignee_id`, hoặc `priority`.
6. **Tab Evaluation Cases**: Xem 179 kịch bản RAG, ACL, ingestion, tiến độ, analytics và workflow.
7. **Tab Functional Tests**: Lọc 84 test theo project, requirement, actor, priority và kết quả kỳ chạy.
8. **Tab Work Tasks / Task Notes / Document Reviews / Work Reports**: Tra chuỗi nguồn việc làm, ghi nhận, phê duyệt và báo cáo theo ID/project.
