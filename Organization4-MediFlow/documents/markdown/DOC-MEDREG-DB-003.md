# [DOC-MEDREG-DB-003] Thiết Kế Cơ Sở Dữ Liệu Hồ Sơ Hành Chính (admin_profiles, profile_identifiers, merge_audits)

- **Organization**: `ORG-MED` (`100% Synthetic Continuum Dataset`)
- **Project**: `MED-REG`
- **Document Type**: `DATABASE_DESIGN`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `MED-U08`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `MEDREG-5`, `MEDREG-11`

> Cấu trúc bảng 3NF cho định danh hành chính và lịch sử gộp hồ sơ trùng.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `MED-U08` | `2026-06-18T10:00:00+07:00` | `MED-U03` | `2026-06-19T11:00:00+07:00` | Chuẩn hóa ràng buộc duy nhất trên mã AK-PAT-XXXXXX và trạng thái gộp hồ sơ. |

## Gộp Hồ Sơ Hành Chính An Toàn
- Giữ nguyên vết ánh xạ từ mã phụ sang mã chính để không hỏng đường dẫn tin nhắn nhắc hẹn.
