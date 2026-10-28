# [DOC-NVLEV-DB-001-LEGACY] [LƯU TRỮ / ĐÃ THAY THẾ] Thiết Kế Bảng Nghỉ Phép v1.0 Dùng Kiểu Số Nguyên Ngày

- **Organization**: `ORG-NOVA` (`100% Synthetic Continuum Dataset`)
- **Project**: `NOVA-LEV`
- **Document Type**: `DATABASE_DESIGN`
- **Current Snapshot Status**: `ARCHIVED`
- **Author (`created_by`)**: `NV-U12`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `NVLEV-4`

> Bản thiết kế cũ gây lỗi làm tròn 0.5 thành 1 ngày khi hủy một phần đơn nghỉ phép trong UAT; đã bị lưu trữ và thay thế bởi DOC-NVLEV-DB-002.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `NV-U12` | `2026-06-24T09:15:00+07:00` | `NV-U05` | `2026-06-25T11:20:00+07:00` | Thiết kế ban đầu đếm số dòng ngày nghỉ (COUNT rows) khi hoàn phép. |

## Cảnh Báo Tài Liệu Đã Ngừng Hiệu Lực
- Tài liệu này đã bị ARCHIVED ngày 22/09/2026 sau lỗi UAT NVLEV-19; xem DOC-NVLEV-DB-002.
