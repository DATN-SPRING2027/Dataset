# [DOC-MEDPIL-DB-004] Quy Tắc Khởi Tạo Dữ Liệu Danh Mục Phòng Khám, Ca Bác Sĩ & Bộ Hồ Sơ Giả Lập Cho Pilot

- **Organization**: `ORG-MED` (`100% Synthetic Continuum Dataset`)
- **Project**: `MED-PIL`
- **Document Type**: `DATABASE_DESIGN`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `MED-U14`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `MEDPIL-9`, `MEDPIL-16`

> Đảm bảo 100% danh mục nạp vào môi trường đào tạo và diễn tập là dữ liệu synthetic an toàn.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `MED-U14` | `2026-08-25T10:00:00+07:00` | `MED-U02` | `2026-08-26T11:00:00+07:00` | Phê duyệt danh mục 6 quầy/phòng lịch hẹn hành chính và bộ kiểm tra không có PII thật. |

## Kiểm Toán Dữ Liệu Synthetic Trước Khi Nạp
- Tuyệt đối không nhập danh sách khách hàng thật từ tệp cũ của phòng khám vào bản thử nghiệm.
