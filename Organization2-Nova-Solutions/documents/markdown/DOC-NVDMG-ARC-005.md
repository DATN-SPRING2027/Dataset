# [DOC-NVDMG-ARC-005] Chiến Lược Sao Lưu, Chuyển Đổi Cuối Tuần Cutover & Kế Hoạch Quay Lui (Rollback Plan)

- **Organization**: `ORG-NOVA` (`100% Synthetic Continuum Dataset`)
- **Project**: `NOVA-DMG`
- **Document Type**: `ARCHITECTURE`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `NV-U18`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `NVDMG-16`, `NVDMG-26`

> Ngưỡng quyết định Go/No-Go và quy trình khôi phục snapshot PostgreSQL trong 15 phút nếu đối soát đầu kỳ lệch.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `NV-U18` | `2026-10-06T10:15:00+07:00` | `NV-U06` | `2026-10-07T11:00:00+07:00` | Phê duyệt kịch bản Rollback trong vòng 15 phút. |

## Tiêu Chí Kích Hoạt Rollback
- Bất kỳ sai lệch số dư phép nào > 0.00 ngày không giải trình được trước mốc khóa sổ.
