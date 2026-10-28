# [DOC-MEDPIL-API-003] Đặc Tả Webhook Nhận Trạng Thái Tin Nhắn Nhắc Hẹn Từ Cổng VietNotify

- **Organization**: `ORG-MED` (`100% Synthetic Continuum Dataset`)
- **Project**: `MED-PIL`
- **Document Type**: `API_SPECIFICATION`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `MED-U16`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `MEDPIL-7`, `MEDPIL-25`

> Xử lý callback DELIVERED / FAILED để nhân viên lễ tân chủ động gọi xác nhận các lịch dời khẩn.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `MED-U16` | `2026-08-11T09:30:00+07:00` | `MED-U06` | `2026-08-12T10:15:00+07:00` | Phê duyệt POST /api/v1/integrations/vietnotify/delivery-receipts. |

## Xử Lý Lỗi Gửi Thông Báo
- Hiển thị danh sách cần xác nhận lại trên bảng điều khiển lễ tân trưởng.
