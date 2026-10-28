# [DOC-CLDOBS-API-004] Đặc Tả API Dead-Man-Switch Heartbeat Watchdog Giám Sát Tiến Trình Nền 24/7

- **Organization**: `ORG-CLD` (`100% Synthetic Continuum Dataset`)
- **Project**: `CLD-OBS`
- **Document Type**: `API_SPECIFICATION`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `CLD-U12`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `CLDOBS-8`, `CLDOBS-19`

> Cơ chế phát hiện tiến trình cron/worker âm thầm treo bằng xung nhịp định kỳ mỗi 60 giây.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `CLD-U12` | `2026-07-08T09:20:00+07:00` | `CLD-U04` | `2026-07-09T11:00:00+07:00` | Phê duyệt POST /api/v1/heartbeats/{monitor_slug}/ping và quy tắc kích hoạt cảnh báo sau 3 chu kỳ trễ. |

## Giám Sát Chủ Động Worker Nền
- Chính cơ chế Heartbeat này đã phát hiện sớm sự cố nghẽn xác thực ngày lễ 02/09/2026 lúc 09:12+07:00.
