# [DOC-CLDOBS-REQ-001] Khung Chỉ Số SLI/SLO Đa Tenant (99.95% Availability) & Cảnh Báo Tốc Độ Đốt Ngân Sách Lỗi

- **Organization**: `ORG-CLD` (`100% Synthetic Continuum Dataset`)
- **Project**: `CLD-OBS`
- **Document Type**: `REQUIREMENT`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `CLD-U04`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `CLDOBS-1`, `CLDOBS-5`, `CLDOBS-18`

> Định nghĩa SLO khả dụng 99.95%/tháng và cảnh báo đa cửa sổ (multi-window burn-rate) giảm nhiễu ca trực.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `CLD-U04` | `2026-05-06T09:10:00+07:00` | `CLD-U01` | `2026-05-07T10:30:00+07:00` | Phê duyệt ngưỡng SLO 99.95% cho API xác thực & thanh toán, độ trễ P99 <= 450ms. |

## Tiêu Chuẩn Cảnh Báo Dựa Trên Triệu Chứng Người Dùng
- Ưu tiên cảnh báo theo tỷ lệ lỗi 5xx và độ trễ P99 thực tế thay vì xung nhịp CPU thoáng qua.
