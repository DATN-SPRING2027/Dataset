# [DOC-CLDSUP-DB-004] Thiết Kế Bảng Đối Soát Cam Kết SLA Tháng & Theo Dõi Hành Động Hậu Kiểm (postmortem_action_items)

- **Organization**: `ORG-CLD` (`100% Synthetic Continuum Dataset`)
- **Project**: `CLD-SUP`
- **Document Type**: `DATABASE_DESIGN`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `CLD-U15`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `CLDSUP-8`, `CLDSUP-18`

> Lưu trữ thời gian ngừng dịch vụ hợp lệ để tính mức khấu trừ tín dụng SLA minh bạch.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `CLD-U15` | `2026-07-21T09:30:00+07:00` | `CLD-U06` | `2026-07-22T10:20:00+07:00` | Chuẩn hóa khóa ngoại liên kết incident_id với danh mục hành động phòng ngừa bắt buộc. |

## Truy Vết Khắc Phục Sau Sự Cố
- Không cho phép đánh dấu CLOSED trên postmortem_action_items nếu thiếu bằng chứng kiểm thử tải hoặc PR Terraform.
