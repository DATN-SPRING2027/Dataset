# [DOC-CLDSUP-API-003] Đặc Tả API Xuất Bản Trạng Thái Dịch Vụ (Status Page) & Kiểm Tra Khử Nhạy Cảm Tự Động

- **Organization**: `ORG-CLD` (`100% Synthetic Continuum Dataset`)
- **Project**: `CLD-SUP`
- **Document Type**: `API_SPECIFICATION`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `CLD-U14`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `CLDSUP-7`, `CLDSUP-16`

> Chặn xuất bản bản tin nếu phát hiện địa chỉ IP nội bộ, chuỗi kết nối hoặc mã định danh tenant khác.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `CLD-U14` | `2026-07-02T09:40:00+07:00` | `CLD-U06` | `2026-07-03T11:00:00+07:00` | Thêm bộ kiểm tra regex chặn rò rỉ thông tin hạ tầng nội bộ trên POST /api/v1/status-updates. |

## Kiểm Duyệt Trước Xuất Bản
- Từ chối HTTP 422 nếu nội dung chứa tên bảng nội bộ hoặc thông tin của tenant thứ ba.
