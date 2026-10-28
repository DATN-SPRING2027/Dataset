# [DOC-CLDINC-API-004] Đặc Tả API Webhook Tiếp Nhận Cảnh Báo, Xác Nhận ACK & Ghi Nhận Override Lịch Trực

- **Organization**: `ORG-CLD` (`100% Synthetic Continuum Dataset`)
- **Project**: `CLD-INC`
- **Document Type**: `API_SPECIFICATION`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `CLD-U13`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `CLDINC-6`, `CLDINC-14`

> Hợp đồng API idempotent nhận sự kiện cảnh báo và xác thực chữ ký khóa tích hợp.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `CLD-U13` | `2026-05-26T09:20:00+07:00` | `CLD-U03` | `2026-05-27T10:15:00+07:00` | Chuẩn hóa khóa chống trùng deduplication_key trên POST /api/v1/alerts/ingest. |

## Endpoints Điều Phối Ca Trực
- POST /api/v1/oncall/overrides bắt buộc người nhận ca thay đang ở trạng thái ACTIVE trong ORG-CLD.
