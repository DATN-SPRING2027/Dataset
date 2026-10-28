# [DOC-MEDADM-REQ-001] FRS Hàng Đợi Tiếp Đón Quầy Lễ Tân, Phân Quyền Tác Nghiệp & Cờ Chặn Lộ SĐT Khi Xuất File

- **Organization**: `ORG-MED` (`100% Synthetic Continuum Dataset`)
- **Project**: `MED-ADM`
- **Document Type**: `REQUIREMENT`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `MED-U05`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `MEDADM-1`, `MEDADM-7`, `MEDADM-18`

> Quy định luồng Check-in cho khách đặt trước (Scheduled) và khách vãng lai (WalkIn) cùng cấu hình mặc định không xuất SĐT ra bảng tính.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `MED-U05` | `2026-05-28T09:40:00+07:00` | `MED-U02` | `2026-05-29T11:15:00+07:00` | Phê duyệt quy tắc ưu tiên hàng đợi tiếp đón và chính sách bảo vệ dữ liệu xuất báo cáo. |

## Luồng Tiếp Đón Scheduled vs WalkIn
- Người có lịch Scheduled đến trong khung +-15 phút được cấp số thứ tự ưu tiên theo slot đã đặt; khách WalkIn được xếp vào slot dự phòng gần nhất.

## Chính Sách Xuất Báo Cáo Hành Chính An Toàn
- Tham số include_phone_in_excel_export bắt buộc bằng false để ngăn tệp bảng tính lưu trôi nổi trên máy cá nhân.
