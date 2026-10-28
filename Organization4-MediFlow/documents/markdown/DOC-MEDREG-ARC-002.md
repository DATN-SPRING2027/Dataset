# [DOC-MEDREG-ARC-002] Kiến Trúc Băm Định Danh Liên Lạc (Salted HMAC Lookup) & Bảo Vệ Dữ Liệu Hành Chính

- **Organization**: `ORG-MED` (`100% Synthetic Continuum Dataset`)
- **Project**: `MED-REG`
- **Document Type**: `ARCHITECTURE`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `MED-U03`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `MEDREG-2`, `MEDREG-8`

> Tách bảng thông tin liên lạc được mã hóa khỏi bảng chỉ mục tìm kiếm nhanh tại quầy lễ tân.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `MED-U03` | `2026-06-08T09:20:00+07:00` | `MED-U01` | `2026-06-09T10:30:00+07:00` | Phê duyệt kiến trúc mã hóa cột liên lạc AES-256-GCM kèm khóa tra cứu HMAC. |

## Cơ Chế Tra Cứu Không Giải Mã Hàng Loạt
- Mọi thao tác mở xem đầy đủ số liên lạc để xác nhận lịch đều ghi nhật ký kiểm toán.
