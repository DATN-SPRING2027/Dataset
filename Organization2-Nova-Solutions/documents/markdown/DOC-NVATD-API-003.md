# [DOC-NVATD-API-003] Đặc Tả API Đồng Bộ Máy Chấm Công & Xuất CSV Đối Soát Tăng Ca (Cập Nhật Theo CR-2026-08)

- **Organization**: `ORG-NOVA` (`100% Synthetic Continuum Dataset`)
- **Project**: `NOVA-ATD`
- **Document Type**: `API_SPECIFICATION`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `NV-U11`
- **Displayed Content Version**: `v2` (`APPROVED`)
- **Linked Tasks**: `NVATD-11`, `NVATD-27`

> v1 đồng bộ batch vân tay; v2 bổ sung endpoint xuất CSV giờ tăng ca đủ điều kiện nghỉ bù theo phần được duyệt của CR-2026-08.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `NV-U11` | `2026-07-07T09:30:00+07:00` | `NV-U04` | `2026-07-08T10:20:00+07:00` | Phê duyệt API ingest batch tối đa 1.000 bản ghi quét vân tay/lần. |
| v2 | `APPROVED` | `NV-U11` | `2026-09-25T10:15:00+07:00` | `NV-U02` | `2026-09-28T09:45:00+07:00` | Bổ sung GET /api/v1/attendance/overtime-comp-export.csv theo quyết định CR-2026-08 Phase 1. |

## Đồng Bộ Máy Chấm Công Idempotent
- POST /api/v1/attendance/punches:batch nhận tối đa 1.000 sự kiện/lần với chữ ký X-Device-Signature.

## Xuất CSV Đối Soát Tăng Ca (Phạm Vi Duyệt Của CR-2026-08)
- GET /api/v1/attendance/overtime-comp-export.csv chỉ dành cho vai trò HR/C&B Admin, phục vụ đối soát thủ công giờ nghỉ bù trong Giai đoạn 1.

## Bảng Tham Chiếu Chi Tiết
| Endpoint | Method | Phạm Vi CR-2026-08 |
| :--- | :--- | :--- |
| /api/v1/attendance/punches:batch | POST | Baseline v1.0 |
| /api/v1/attendance/overtime-comp-export.csv | GET | Được duyệt bổ sung ở Phase 1 |
