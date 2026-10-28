# [DOC-CLDINC-DES-005] Thiết Kế Bảng Điều Hành Kanban Sự Cố & Đề Xuất v2 Tự Động Đóng Sự Cố (Đang Chờ Duyệt)

- **Organization**: `ORG-CLD` (`100% Synthetic Continuum Dataset`)
- **Project**: `CLD-INC`
- **Document Type**: `DESIGN`
- **Current Snapshot Status**: `PENDING_REVIEW`
- **Author (`created_by`)**: `CLD-U17`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `CLDINC-16`, `CLDINC-25`

> v1 hiển thị giới hạn WIP đã duyệt; v2 đề xuất để bot tự đóng sự cố SEV-1 sau 15 phút xanh đang chờ đánh giá rủi ro.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `CLD-U17` | `2026-06-16T09:30:00+07:00` | `CLD-U03` | `2026-06-17T10:40:00+07:00` | Phê duyệt giao diện làn ưu tiên EXPEDITE_P0 tách biệt trên bảng Kanban. |
| v2 | `PENDING_REVIEW` | `CLD-U17` | `2026-10-14T10:30:00+07:00` | `-` | `-` | Đề xuất cho phép bot tự động chuyển sự cố SEV-1 sang RESOLVED sau 15 phút metric hồi phục (chưa được duyệt). |

## Hiển Thị Làn Khẩn Cấp Kanban
- Tô nổi bật cảnh báo chạm trần WIP để nhóm dừng kéo thẻ thường quy mới.
