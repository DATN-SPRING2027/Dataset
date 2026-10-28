# [DOC-MEDADM-ARC-002] Kiến Trúc Phân Quyền RBAC Nội Bộ Phòng Khám & Màn Hình Gọi Số Quầy Tiếp Đón Ẩn Danh

- **Organization**: `ORG-MED` (`100% Synthetic Continuum Dataset`)
- **Project**: `MED-ADM`
- **Document Type**: `ARCHITECTURE`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `MED-U05`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `MEDADM-3`, `MEDADM-11`

> Màn hình tivi sảnh chờ chỉ hiển thị mã vé tiếp đón (ví dụ Q-108) và chữ cái viết tắt tên để bảo đảm riêng tư.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `MED-U05` | `2026-06-16T10:00:00+07:00` | `MED-U01` | `2026-06-17T10:40:00+07:00` | Phê duyệt ma trận đặc quyền RECEPTIONIST, RECEPTION_SHIFT_LEAD và CLINIC_OPERATIONS_VIEWER. |

## Hiển Thị Ẩn Danh Tại Sảnh Chờ
- Sử dụng mã vé ngày Q-XXX kết hợp số quầy tiếp đón.
