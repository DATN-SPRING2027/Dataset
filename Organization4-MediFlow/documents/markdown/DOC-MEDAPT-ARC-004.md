# [DOC-MEDAPT-ARC-004] Kiến Trúc Hàng Đợi Outbox Nhắc Lịch Hẹn Qua Cổng Đối Tác Giả Lập VietNotify

- **Organization**: `ORG-MED` (`100% Synthetic Continuum Dataset`)
- **Project**: `MED-APT`
- **Document Type**: `ARCHITECTURE`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `MED-U04`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `MEDAPT-6`, `MEDAPT-20`

> Đảm bảo không mất tin nhắn thông báo giờ hẹn mới khi mạng đối tác chập chờn.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `MED-U04` | `2026-07-28T10:00:00+07:00` | `MED-U01` | `2026-07-29T11:15:00+07:00` | Áp dụng mẫu Transactional Outbox gửi sự kiện nhắc lịch hành chính (chỉ chứa ngày giờ và quầy đón tiếp). |

## Tối Thiểu Hóa Dữ Liệu Qua Kênh Bên Thứ Ba
- Không truyền thông tin chi tiết ngoài giờ hẹn và địa điểm quầy lễ tân.
