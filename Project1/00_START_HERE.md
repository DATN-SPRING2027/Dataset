# Bộ Dữ Liệu Northstar Commerce v1.0 — Hướng Dẫn Vận Hành & Khai Thác

## 1. Bối cảnh kịch bản (Dataset Scenario)
Bộ dữ liệu mô phỏng công ty công nghệ hư cấu **Northstar Commerce Systems**, đang xây dựng nền tảng thương mại điện tử đa tenant (multi-tenant ecommerce platform) cho khách hàng merchant pilot là **Meridian Outfitters**, tích hợp với đối tác cổng thanh toán **PulsePay Network**.
- Nguồn cảm hứng domain và công nghệ: Dự án mã nguồn mở **Bagisto** (kiến trúc Laravel + Vue.js: https://github.com/bagisto/bagisto).
- **Tính tổng hợp (Synthetic)**: 100% dữ liệu nhân sự, công ty, ticket, thẻ thanh toán, sự cố và tài liệu đều là dữ liệu giả lập phục vụ kiểm thử và demo. Mọi địa chỉ email sử dụng tên miền an toàn `example.invalid`. Không chứa bất kỳ bí mật, API key thật hay dữ liệu cá nhân nào.

## 2. Quy mô dữ liệu chuẩn (Canonical Data Scale)
- **3 Tổ chức (Organizations)**: `ORG-NSC` (Northstar), `ORG-MERIDIAN` (Meridian), `ORG-PULSEPAY` (PulsePay).
- **10 Phòng ban (Departments)**: 8 phòng ban Northstar, 1 Merchandising (Meridian), 1 API Ops (PulsePay).
- **74 Hồ sơ thành viên (Members)**: 60 nhân sự nội bộ Northstar, 8 nhân sự Meridian, 6 nhân sự PulsePay. Trong đó có 71 thành viên active và 3 cựu nhân viên (inactive, quyền hạn đã bị thu hồi).
- **8 Dự án (Projects)**: `NSC-CAT`, `NSC-SRCH`, `NSC-CART`, `NSC-CHKO`, `NSC-PAY`, `NSC-INV`, `NSC-ORD`, `NSC-PLAT`.
- **104 Sprints**: 13 sprint liên tiếp, mỗi sprint 14 ngày tính cả ngày đầu/cuối. Sprint 13 chạy từ 2026-09-29 đến hết 2026-10-12 và có issue cùng WIP thực tế.
- **180 Ngày giả lập (Simulation Window)**: Từ `2026-04-16` đến `2026-10-12` (gồm đúng **128 ngày làm việc - weekdays**).
- **Đúng 1.400 Bản ghi tài liệu logic (Logical Documents)**: Được đăng ký đầy đủ trong `structured/documents.jsonl`.
- **Đúng 2.500 Jira-like Issues**: Đầy đủ bình luận (comments), lịch sử trạng thái (changelog), quyền sở hữu, độ ưu tiên, ngày hết hạn, nhãn dán.
- **Bình luận theo ngữ cảnh**: Comment phù hợp trạng thái và tiêu đề từng issue, với nội dung đa dạng để hỗ trợ tìm kiếm và RAG.
- **120 Bộ test case chuẩn (Evaluation Cases)**: Bao phủ RAG chất lượng cao, ACL đa tầng, tiến độ dự án, trích xuất bảng DOCX và xử lý tình huống biên.

## 3. Kiến trúc đóng gói: File vật lý vs Bản ghi logic
Để đáp ứng nghiêm ngặt giới hạn hệ thống (**dưới 160 file vật lý tổng cộng trong thư mục Dataset**):
- **Tổng số file vật lý trong v1**: Đúng **107 files** (gồm 56 bundles + 10 docx + 12 formal md + 6 fixtures + 12 jsonl + 6 eval + 4 docs + 1 tool).
- **Tổng số file trong toàn bộ Dataset** (bao gồm 39 file seed v0.1 + 1 file snapshot zip + 107 file v1): Đúng **147 files <= 160 files**.
- `manifest.json` ghi SHA-256 và kích thước byte cho mọi file trong `v1`, ngoại trừ chính manifest để tránh tự tham chiếu.
- **Cách ánh xạ sang 1.400 tài liệu logic**:
  - **56 Monthly Markdown Bundles**: 8 dự án × 7 tháng (tháng 4 đến tháng 10/2026) lưu trữ 1.373 bản ghi cập nhật kỹ thuật trên 128 ngày làm việc (93 ngày có 11 docs, 35 ngày có 10 docs). Mỗi bản ghi có tiêu đề cấp 3 và thẻ neo HTML rõ ràng (ví dụ: `<a id="doc-cat-20260416-01"></a>`).
  - **10 Tài liệu DOCX trang trọng**: Quy chuẩn kiến trúc, API contract, test plan, bảo mật, RCA, runbook...
  - **12 Tài liệu Markdown trang trọng**: Company charter, PRD, ADR hiện tại và superseded, chính sách đổi trả, biên bản họp...
  - **5 Fixture files đặc biệt**: File duplicate, thiếu metadata, link hỏng, xung đột mốc thời gian, orphan Jira key.
  - Tổng cộng: 1.373 + 10 + 12 + 5 = **1.400 Logical Documents**!

## 4. Thứ tự nạp dữ liệu khuyến nghị (Ingestion Pipeline)
1. **Thực thể nền tảng**: `organizations` → `departments` → `members` → `access_groups` → `group_memberships`.
2. **Dự án & Sprints**: `projects` → `sprints` → `project_memberships`.
3. **Tiến độ và nhiệm vụ**: `issues` → `issue_comments` → `issue_changelog`.
4. **Nạp kho tài liệu (Content Ingestion)**:
   - Nạp các file DOCX trong `documents/docx/` và Markdown trong `documents/markdown/formal/`.
   - Phân đoạn 56 bundles trong `documents/markdown/bundles/` theo các thẻ neo `<a id="..."></a>` để tạo đúng 1.373 chunks tài liệu tương ứng với `structured/documents.jsonl`.
5. **Đánh chỉ mục vector & tìm kiếm**:
   - Gắn nhãn `access_groups`, `classification`, và `scope` vào từng chunk.
   - Áp dụng bộ lọc ACL trước khi retrieval (Pre-filtering).
6. **Bộ dữ liệu kiểm thử (Evaluation)**:
   - Nạp các file trong `evaluation/` vào namespace riêng biệt, **tuyệt đối không đưa gold answers vào index demo**.

## 5. Hướng dẫn sử dụng Dataset_Catalog.xlsx
1. Mở file `Dataset_Catalog.xlsx` bằng Microsoft Excel hoặc LibreOffice Calc.
2. **Tab Overview**: Xem tổng quan chỉ số KPI, biểu đồ phân bố trạng thái Jira issue và bảng tiến độ 8 dự án.
3. **Tab Sprints**: Tra cứu 104 sprint của 8 dự án, xem mục tiêu sprint và trạng thái active/closed.
4. **Tab Documents**: Sử dụng bộ lọc (AutoFilter) theo `project_id`, `scope`, `classification`, `status` hoặc `format`.
5. **Tab Issues**: Tra cứu 2.500 ticket theo `status` (Blocked, Done...), `sprint_id`, `assignee_id`, hoặc `priority`.
6. **Tab Test Cases**: Xem 120 kịch bản test chuẩn cho RAG, ACL và Analytics.
