# [DOC-MEDAPT-DB-001-LEGACY] [LƯU TRỮ / ĐÃ THAY THẾ] Thiết Kế Bảng Đặt Lịch Hẹn v1.0 Chỉ Kiểm Tra Trùng Ở Tầng Ứng Dụng

- **Organization**: `ORG-MED` (`100% Synthetic Continuum Dataset`)
- **Project**: `MED-APT`
- **Document Type**: `DATABASE_DESIGN`
- **Current Snapshot Status**: `ARCHIVED`
- **Author (`created_by`)**: `MED-U10`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `MEDAPT-4`

> Thiết kế ban đầu kiểm tra slot trống bằng câu lệnh SELECT thông thường gây lỗi đặt trùng (double-booking) khi 2 quầy lễ tân bấm cùng lúc trong buổi Demo M2.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `MED-U10` | `2026-06-23T09:30:00+07:00` | `MED-U04` | `2026-06-24T10:30:00+07:00` | Thiết kế bảng appointment_bookings chưa có khóa dòng và ràng buộc mức CSDL. |

## Cảnh Báo Ngừng Hiệu Lực
- Đã lưu trữ ngày 09/09/2026; xem thiết kế chuẩn hóa tại DOC-MEDAPT-DB-002 v2.
