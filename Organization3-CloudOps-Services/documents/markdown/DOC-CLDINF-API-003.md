# [DOC-CLDINF-API-003] Đặc Tả Luồng Đối Soát Trôi Cấu Hình Hàng Giờ (Hourly Terraform & WAF Drift API)

- **Organization**: `ORG-CLD` (`100% Synthetic Continuum Dataset`)
- **Project**: `CLD-INF`
- **Document Type**: `API_SPECIFICATION`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `CLD-U16`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `CLDINF-6`, `CLDINF-24`

> Hợp đồng báo cáo sai lệch giữa trạng thái hạ tầng thực tế và nhánh main GitOps.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `CLD-U16` | `2026-06-18T10:15:00+07:00` | `CLD-U05` | `2026-06-19T10:40:00+07:00` | Chuẩn hóa payload sự kiện drift gửi từ worker CLD-BOT-TF-DRIFT sang bảng Kanban. |

## Tự Động Phát Hiện Lệch Cấu Hình
- Quét định kỳ mỗi 60 phút trên toàn bộ module WAF, Security Group và PgBouncer ConfigMap.
