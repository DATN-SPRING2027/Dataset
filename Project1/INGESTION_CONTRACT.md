# Ingestion Contract — Northstar Commerce Dataset v1.0

## 1. Định dạng nội dung và quy cách đóng gói
- **Canonical Content Formats**: Markdown (.md) và Word (.docx).
- **Physical Packaging**:
  - Toàn bộ 1.373 bản ghi cập nhật kỹ thuật hàng ngày được đóng gói thành đúng 56 file Markdown bundle theo từng dự án và từng tháng (`documents/markdown/bundles/<PROJECT>-<YYYY-MM>.md`).
  - Lịch trình cập nhật diễn ra trên đúng **128 ngày làm việc (weekdays)** trong khoảng thời gian từ `2026-04-16` đến `2026-10-12`. Đúng 93 ngày có 11 tài liệu và 35 ngày có 10 tài liệu. Không tạo cập nhật vào cuối tuần.
  - Mỗi bản ghi tài liệu logic trong bundle sở hữu thẻ neo định danh duy nhất (ví dụ `<a id="doc-cat-20260416-01"></a>`) và mã băm `content_sha256` độc lập.
  - Tài liệu chuẩn mực, kiến trúc trang trọng và quy chuẩn bảo mật được lưu trữ độc lập trong `documents/docx/` (10 files) và `documents/markdown/formal/` (12 files).

## 2. Định danh, Khóa ngoại & Trích dẫn RAG
- **Khóa chính**: `document_id` (ví dụ `DOC-CAT-20260416-01`) và `issue_id` / `issue_key` (ví dụ `CAT-001`) là định danh bất biến.
- **Phạm vi tài liệu cấp công ty (Organization-level Scope)**: Các tài liệu chiến lược chung của công ty (Charter, Meeting Decisions) có `project_id: null`, `organization_id: "ORG-NSC"`, và `scope: "organization"`. Không sử dụng `project_id: "ORG"` giả mạo.
- **Khớp nối thời gian Issue - Document**: Mọi `source_issue_key` liên kết trong tài liệu đều tồn tại trong `issues.jsonl` và có ngày tạo `issue.created_at <= document.created_at`.
- **Ánh xạ mã tham chiếu ngoại vi**: Mã tham chiếu đối tác `INT-001` được ánh xạ chuẩn xác vào ticket chính quy `CAT-008`. Mã `NONEXISTENT-999` chỉ xuất hiện duy nhất trong fixture kiểm thử lỗi mồ côi `fixtures/orphan_issue_reference.md`.
- **Trích dẫn nguồn RAG**: Khi trả về nguồn tham khảo cho người dùng, công cụ retrieval bắt buộc trả về `file_path` cùng với `section_anchor` chính xác.

## 3. Quy chuẩn kiểm soát quyền truy cập (ACL Pre-filtering)
- **Quy tắc vàng**: Bộ lọc ACL phải được áp dụng **TRƯỚC** khi tính toán khoảng cách vector ranking và trích xuất snippet văn bản.
- Tuyệt đối không để rò rỉ tiêu đề, trích đoạn hoặc tín hiệu tồn tại của tài liệu khi người dùng không thuộc nhóm quyền cho phép.
- **Cách ly đa tenant**: Người dùng thuộc tenant Meridian Outfitters không được phép truy cập tài liệu nội bộ hoặc tài liệu cấu hình của tenant khác.
- **Cựu nhân viên (Inactive Staff)**: Nhân viên đã nghỉ việc (`account_status: inactive`) bị thu hồi toàn bộ phiên đăng nhập và nhóm quyền (`status: revoked`). Lịch sử tham gia (tác giả tài liệu, người giải quyết issue đã hoàn thành trong quá khứ) được giữ nguyên vì tính toàn vẹn kiểm toán.
- **Không có issue mở nào thuộc cựu nhân viên**: Các issue chưa hoàn thành (`status != "Done"`) bắt buộc phải được chuyển giao sang nhân sự active với bản ghi changelog ghi nhận sự kiện chuyển giao `field: "assignee"`.

## 4. Mô hình Sprint & Cách tính Story Points
- Mỗi dự án có 13 sprint liên tiếp, mỗi sprint dài 14 ngày tính cả ngày bắt đầu và kết thúc, từ `2026-04-14` đến `2026-10-12`.
- Sprint 13 chạy từ `2026-09-29` đến hết ngày `2026-10-12`, là sprint duy nhất có `status: "active"`; cả 8 dự án đều có issue được xếp vào sprint này.
- Chỉ số **Active Sprint WIP Story Points** (dùng cho PRG-011, PRG-012) được định nghĩa là: Tổng `story_points` của tất cả các issue thuộc dự án đó, nằm trong sprint đang active (`current_sprint_id`), và có trạng thái là `In Progress` hoặc `In Review`.

## 5. Quy chuẩn Mã băm Toàn vẹn (Canonical Checksum)
- Mã băm `content_sha256` của từng section trong Markdown bundle được tính toán trên đoạn văn bản chuẩn hóa:
  - Bắt đầu từ dòng tiêu đề `### [{doc_id}] ...` cho đến dòng phân cách `---`.
  - Toàn bộ ký tự xuống dòng được chuẩn hóa thành `\n` (LF), cắt bỏ khoảng trắng thừa ở đầu/cuối (`strip()`), và mã hóa UTF-8 trước khi băm SHA-256.
  - Công cụ nạp và kiểm tra tính toàn vẹn bắt buộc áp dụng hàm chuẩn hóa tương tự.

## 6. File Inventory trong Manifest
- `manifest.json` ghi `file_inventory` với đường dẫn tương đối trong `Dataset/v1`, kích thước byte và SHA-256 của từng file vật lý.
- Inventory được sắp xếp theo đường dẫn và bao gồm toàn bộ file trong `v1`, ngoại trừ chính `manifest.json` để tránh checksum tự tham chiếu. `physical_files_in_v1` vẫn tính cả manifest.
- Sau khi sinh dữ liệu, công cụ nạp phải đối chiếu mọi đường dẫn, kích thước và checksum trong inventory với file thực tế.
