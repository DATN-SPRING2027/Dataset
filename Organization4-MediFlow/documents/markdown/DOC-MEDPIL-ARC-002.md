# [DOC-MEDPIL-ARC-002] Kiến Trúc Triển Khai Môi Trường Pilot Cô Lập, Kết Nối TLS Đôi & Cổng Sandbox VietNotify

- **Organization**: `ORG-MED` (`100% Synthetic Continuum Dataset`)
- **Project**: `MED-PIL`
- **Document Type**: `ARCHITECTURE`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `MED-U16`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `MEDPIL-4`, `MEDPIL-12`

> Bảo mật đường truyền từ quầy tiếp đón phòng khám An Khang về cụm đám mây MediFlow.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `MED-U16` | `2026-07-09T09:45:00+07:00` | `MED-U06` | `2026-07-10T10:30:00+07:00` | Thiết lập mTLS cho webhook trạng thái gửi tin từ đối tác VietNotify. |

## Cô Lập Môi Trường Pilot
- Tách riêng hoàn toàn khóa ký webhook của phòng khám Pilot An Khang.
