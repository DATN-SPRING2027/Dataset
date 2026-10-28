# [DOC-NVATD-DB-002] Thiết Kế Bảng Dữ Liệu Chấm Công (work_shifts, raw_punch_logs, daily_attendance_records)

- **Organization**: `ORG-NOVA` (`100% Synthetic Continuum Dataset`)
- **Project**: `NOVA-ATD`
- **Document Type**: `DATABASE_DESIGN`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `NV-U10`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `NVATD-5`, `NVATD-8`

> Tách biệt log quét vân tay thô bất biến và bản ghi công ngày đã chuẩn hóa.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `NV-U10` | `2026-06-29T10:10:00+07:00` | `NV-U04` | `2026-06-30T11:00:00+07:00` | Chuẩn hóa khóa chống trùng (device_serial, punch_timestamp, employee_code). |

## Thiết Kế Chống Trùng Dữ Liệu Máy Vân Tay
- Unique constraint uq_device_emp_punch ngăn ghi đúp khi thiết bị đồng bộ lại sau mất mạng.
