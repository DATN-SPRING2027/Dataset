# [DOC-CLDOBS-ARC-002] Kiến Trúc Pipeline OpenTelemetry Collector & Lấy Mẫu Giữ Lại Lỗi 100% (Tail-Based Sampling)

- **Organization**: `ORG-CLD` (`100% Synthetic Continuum Dataset`)
- **Project**: `CLD-OBS`
- **Document Type**: `ARCHITECTURE`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `CLD-U09`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `CLDOBS-3`, `CLDOBS-11`

> Giữ lại 100% trace có lỗi HTTP 5xx hoặc độ trễ > 1.000ms trong khi lấy mẫu 10% lưu lượng bình thường.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `CLD-U09` | `2026-06-03T10:00:00+07:00` | `CLD-U04` | `2026-06-04T11:20:00+07:00` | Triển khai hàng đợi đệm bộ nhớ giới hạn và bộ lọc khử token nhạy cảm trên span attributes. |

## Bảo Mật & Khử Nhạy Cảm Telemetry
- Tuyệt đối không lưu thông tin định danh cá nhân hay khóa bí mật trong nhãn metric/trace.
