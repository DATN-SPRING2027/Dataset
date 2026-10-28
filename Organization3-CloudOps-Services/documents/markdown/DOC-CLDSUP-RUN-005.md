# [DOC-CLDSUP-RUN-005] Quy Trình Xử Lý Sự Cố Chặn Nhầm Webhook Đối Tác (Từ Bài Học INC-2026-0926 Của FinLedger)

- **Organization**: `ORG-CLD` (`100% Synthetic Continuum Dataset`)
- **Project**: `CLD-SUP`
- **Document Type**: `TECHNICAL_SPECIFICATION`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `CLD-U14`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `CLDSUP-21`, `CLDSUP-23`

> Hướng dẫn xác minh chữ ký HMAC-SHA256 và danh sách dải IP đối tác trước khi can thiệp rule WAF.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `CLD-U14` | `2026-09-30T10:00:00+07:00` | `CLD-U06` | `2026-10-01T10:45:00+07:00` | Chuẩn hóa phối hợp Tier-3 và Edge SRE để replay an toàn các sự kiện webhook bị từ chối HTTP 403. |

## Quy Trình Replay Webhook An Toàn
- Kiểm tra idempotency_key trước khi kích hoạt gửi bù hàng đợi webhook.
