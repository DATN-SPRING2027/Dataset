# [DOC-NVHR-DB-003] Thiết Kế Cơ Sở Dữ Liệu Core HR (employees, employment_contracts, report_to_edges)

- **Organization**: `ORG-NOVA` (`100% Synthetic Continuum Dataset`)
- **Project**: `NOVA-HR`
- **Document Type**: `DATABASE_DESIGN`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `NV-U08`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `NVHR-5`, `NVHR-9`

> Đặc tả bảng dữ liệu nhân sự, hợp đồng và cạnh đồ thị quản lý trực tiếp.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `NV-U08` | `2026-06-25T10:00:00+07:00` | `NV-U03` | `2026-06-26T10:40:00+07:00` | Thiết kế bảng chuẩn hóa 3NF cho hồ sơ hành chính nhân sự. |

## Cấu Trúc Bảng Chính
- Bảng employees lưu thông tin hành chính giả lập; cột work_email dùng miền nội bộ khách hàng.
- Partial unique index trên report_to_edges(subordinate_id) WHERE reporting_mode = 'DIRECT' AND effective_to IS NULL.
