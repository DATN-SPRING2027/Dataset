# [DOC-NVLEV-API-003] Đặc Tả API Đăng Ký, Phê Duyệt Đa Cấp & Hủy Một Phần Đơn Nghỉ Phép

- **Organization**: `ORG-NOVA` (`100% Synthetic Continuum Dataset`)
- **Project**: `NOVA-LEV`
- **Document Type**: `API_SPECIFICATION`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `NV-U12`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `NVLEV-9`, `NVLEV-23`

> Hợp đồng API tính số ngày phép thực trừ (loại trừ ngày lễ Việt Nam & ngày nghỉ tuần) và hủy từng phần.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `NV-U12` | `2026-09-23T11:00:00+07:00` | `NV-U05` | `2026-09-24T10:15:00+07:00` | Cập nhật payload POST /api/v1/leave-requests/{id}/cancel-items trả về delta_restored_days chính xác đến 0.5. |

## Quy Tắc Hủy Một Phần Đơn Nghỉ Phép
- Chỉ hoàn trả đúng tổng day_fraction của các item được chọn hủy và chưa khóa kỳ công.
