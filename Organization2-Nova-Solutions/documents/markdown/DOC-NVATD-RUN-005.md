# [DOC-NVATD-RUN-005] Quy Trình Vận Hành Agent Đồng Bộ Vân Tay Tại Nhà Máy Bình Dương Khi Mất Mạng WAN

- **Organization**: `ORG-NOVA` (`100% Synthetic Continuum Dataset`)
- **Project**: `NOVA-ATD`
- **Document Type**: `TECHNICAL_SPECIFICATION`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `NV-U18`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `NVATD-18`, `NVATD-29`

> Hướng dẫn lưu đệm SQLite cục bộ tối đa 7 ngày và đối soát bù sau khi có mạng trở lại.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `NV-U18` | `2026-08-27T10:00:00+07:00` | `NV-U04` | `2026-08-28T10:45:00+07:00` | Phê duyệt SOP xử lý mất kết nối WAN nhà máy. |

## Cơ Chế Lưu Đệm Khi Đứt Cáp
- Không làm mất dữ liệu chấm công trong tối đa 7 ngày mất mạng liên tục.
