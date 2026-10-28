# [DOC-MEDAPT-API-003] Đặc Tả API Đặt Lịch Hẹn & Dời Lịch Hàng Loạt Có Kiểm Toán (POST /api/v1/appointments:bulk-reschedule)

- **Organization**: `ORG-MED` (`100% Synthetic Continuum Dataset`)
- **Project**: `MED-APT`
- **Document Type**: `API_SPECIFICATION`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `MED-U11`
- **Displayed Content Version**: `v2` (`APPROVED`)
- **Linked Tasks**: `MEDAPT-8`, `MEDAPT-18`, `MEDAPT-25`

> v1 đặt lịch cá nhân; v2 bổ sung endpoint dời lịch hàng loạt phục vụ quầy tiếp đón khi ca bác sĩ thay đổi.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `MED-U11` | `2026-07-14T09:30:00+07:00` | `MED-U04` | `2026-07-15T10:30:00+07:00` | Phê duyệt API tra cứu khung giờ trống và đặt lịch đơn lẻ. |
| v2 | `APPROVED` | `MED-U11` | `2026-09-14T09:30:00+07:00` | `MED-U04` | `2026-09-15T11:00:00+07:00` | Bổ sung POST /api/v1/appointments:bulk-reschedule theo quyết định CFB-2026-01. |

## Hợp Đồng API Dời Lịch Hàng Loạt
- Nếu bất kỳ slot đích nào không đủ chỗ trống, toàn bộ batch quay lui nguyên tử và trả về HTTP 409 SLOT_CAPACITY_EXCEEDED.
