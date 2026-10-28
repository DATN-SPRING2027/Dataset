# [DOC-NVATD-ARC-004] Thiết Kế Bộ Máy Ghép Cặp Giờ Vào/Ra Ca Đêm Vắt Qua 00:00 (Cross-Midnight Pairing)

- **Organization**: `ORG-NOVA` (`100% Synthetic Continuum Dataset`)
- **Project**: `NOVA-ATD`
- **Document Type**: `ARCHITECTURE`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `NV-U04`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `NVATD-12`, `NVATD-15`

> Giải quyết bài toán ca bảo trì nhà máy 22:00–06:00 sáng hôm sau không bị tách nhầm thành hai ngày thiếu quét thẻ.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `NV-U04` | `2026-07-14T09:20:00+07:00` | `NV-U01` | `2026-07-15T11:30:00+07:00` | Áp dụng cửa sổ neo ca (shift anchor window +-4 giờ) thay vì cắt cứng 00:00. |

## Thuật Toán Shift Anchor Window
- Gắn punch-out dựa trên phân ca đã gán thay vì ngày dương lịch đơn thuần.
