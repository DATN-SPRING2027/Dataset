# [DOC-CLDOBS-DB-003] Thiết Kế Bảng Chuỗi Thời Gian Telemetry & Giới Hạn Cardinality Nhãn Đa Tenant

- **Organization**: `ORG-CLD` (`100% Synthetic Continuum Dataset`)
- **Project**: `CLD-OBS`
- **Document Type**: `DATABASE_DESIGN`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `CLD-U09`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `CLDOBS-7`, `CLDOBS-14`

> Kiểm soát số lượng chuỗi thời gian hoạt động và chính sách nén lưu trữ nóng 30 ngày / ấm 90 ngày.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `CLD-U09` | `2026-06-24T09:40:00+07:00` | `CLD-U04` | `2026-06-25T10:15:00+07:00` | Cấm đưa request_id hoặc user_id vào nhãn metric có độ phân tán cao (high cardinality). |

## Chống Bùng Nổ Cardinality
- Tự động từ chối metric mới vượt quá 50.000 chuỗi hoạt động trên một job thu thập.
