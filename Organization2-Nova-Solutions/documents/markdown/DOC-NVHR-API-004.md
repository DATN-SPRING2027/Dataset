# [DOC-NVHR-API-004] Đặc Tả REST API Hồ Sơ Nhân Sự & Cây Quản Lý Trực Tiếp

- **Organization**: `ORG-NOVA` (`100% Synthetic Continuum Dataset`)
- **Project**: `NOVA-HR`
- **Document Type**: `API_SPECIFICATION`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `NV-U08`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `NVHR-10`, `NVHR-22`

> Hợp đồng API CRUD nhân viên, tra cứu cây cấp dưới và khóa tài khoản thôi việc.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `NV-U08` | `2026-07-02T09:10:00+07:00` | `NV-U03` | `2026-07-03T11:15:00+07:00` | Phê duyệt đặc tả OpenAPI v1.0 cho phân hệ Core HR. |

## Endpoints Chính
- GET /api/v1/employees/org-tree trả về cây phân cấp tối đa 6 tầng.
- POST /api/v1/employees/{id}/termination thu hồi phiên JWT ngay tại thời điểm hiệu lực.
