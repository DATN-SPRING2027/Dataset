# [DOC-MEDADM-DB-003] Thiết Kế Bảng Hàng Đợi Tiếp Đón Ngày (reception_queue_tickets) & Thống Kê Tỷ Lệ Vắng Mặt

- **Organization**: `ORG-MED` (`100% Synthetic Continuum Dataset`)
- **Project**: `MED-ADM`
- **Document Type**: `DATABASE_DESIGN`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `MED-U13`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `MEDADM-5`, `MEDADM-14`

> Tính toán thời gian chờ trung bình từ lúc CheckedIn đến lúc hoàn tất thủ tục quầy.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `MED-U13` | `2026-06-30T09:30:00+07:00` | `MED-U05` | `2026-07-01T10:30:00+07:00` | Phân vùng bảng reception_queue_tickets theo ngày phục vụ tổng hợp báo cáo lưu lượng. |

## Đối Soát Trạng Thái Cuối Ca
- Ghi nhận tách biệt lượt hủy chủ động trước giờ hẹn (Cancelled) và lượt không đến (Missed).
