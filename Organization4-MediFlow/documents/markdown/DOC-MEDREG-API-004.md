# [DOC-MEDREG-API-004] Đặc Tả API Đăng Ký Nhanh Quầy Tiếp Đón & Kiểm Tra Trùng Lặp Hồ Sơ Hành Chính

- **Organization**: `ORG-MED` (`100% Synthetic Continuum Dataset`)
- **Project**: `MED-REG`
- **Document Type**: `API_SPECIFICATION`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `MED-U08`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `MEDREG-9`, `MEDREG-16`

> Hợp đồng API tạo hồ sơ trong <= 20 giây thao tác quầy và trả về cảnh báo hồ sơ tương đồng.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `MED-U08` | `2026-07-07T09:15:00+07:00` | `MED-U03` | `2026-07-08T10:20:00+07:00` | Phê duyệt POST /api/v1/admin-profiles và POST /api/v1/admin-profiles:dedup-check. |

## Ràng Buộc Whitelist Schema
- Trả về HTTP 400 UNKNOWN_FIELD nếu client gửi thêm trường ngoài danh mục hành chính đã duyệt.
