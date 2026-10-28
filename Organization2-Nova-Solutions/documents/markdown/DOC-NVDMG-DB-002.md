# [DOC-NVDMG-DB-002] Đặc Tả Bảng Tạm Staging ETL & Quy Tắc Chuẩn Hóa Mã Phòng Ban / Ngày Vào Làm

- **Organization**: `ORG-NOVA` (`100% Synthetic Continuum Dataset`)
- **Project**: `NOVA-DMG`
- **Document Type**: `DATABASE_DESIGN`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `NV-U14`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `NVDMG-6`, `NVDMG-12`

> Ánh xạ mã bộ phận viết tắt không đồng nhất trong Excel cũ sang danh mục chuẩn.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `NV-U14` | `2026-07-15T09:45:00+07:00` | `NV-U06` | `2026-07-16T10:20:00+07:00` | Phê duyệt schema stg_hr_employees và báo cáo dòng lỗi cách ly (quarantine rows). |

## Xử Lý Dữ Liệu Bẩn
- Không tự động đoán ngày vào làm khi Excel ghi thiếu tháng.
