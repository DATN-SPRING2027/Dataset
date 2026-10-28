# [DOC-MEDADM-API-004] Đặc Tả API Check-In Quầy Lễ Tân, Cấp Số Thứ Tự & Xuất Báo Cáo Lưu Lượng Đã Khử Định Danh

- **Organization**: `ORG-MED` (`100% Synthetic Continuum Dataset`)
- **Project**: `MED-ADM`
- **Document Type**: `API_SPECIFICATION`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `MED-U13`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `MEDADM-8`, `MEDADM-16`

> Hợp đồng API chuyển trạng thái tiếp đón và tải báo cáo tổng hợp theo ca.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `MED-U13` | `2026-07-16T09:20:00+07:00` | `MED-U05` | `2026-07-17T10:15:00+07:00` | Phê duyệt POST /api/v1/reception/check-in và GET /api/v1/reports/daily-traffic.xlsx. |

## Kiểm Soát Trường Xuất Báo Cáo
- Bỏ qua mọi tham số query cố tình yêu cầu mở khóa cột liên lạc.
