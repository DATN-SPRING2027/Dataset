# [DOC-CLDOBS-SLI-006] Đề Xuất Bắn Cảnh Báo Pager Khẩn Cấp Khi CPU Pod Đơn Lẻ Vượt 65% Trong 30 Giây (Bị Từ Chối)

- **Organization**: `ORG-CLD` (`100% Synthetic Continuum Dataset`)
- **Project**: `CLD-OBS`
- **Document Type**: `DESIGN`
- **Current Snapshot Status**: `REJECTED`
- **Author (`created_by`)**: `CLD-U13`
- **Displayed Content Version**: `v1` (`REJECTED`)
- **Linked Tasks**: `CLDOBS-30`

> Đề xuất cảnh báo theo xung CPU ngắn hạn bị từ chối vì tạo bão cảnh báo giả trong lúc HPA đang giãn pod bình thường.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `REJECTED` | `CLD-U13` | `2026-08-20T09:30:00+07:00` | `CLD-U01` | `2026-08-21T11:15:00+07:00` | Đề xuất rule cảnh báo CPU tức thời. |

## Lý Do Bác Bỏ Kỹ Thuật
- Gây mệt mỏi cảnh báo (alert fatigue) nghiêm trọng mà không phản ánh suy giảm dịch vụ thực tế.
