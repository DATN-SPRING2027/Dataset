# [DOC-NVLEV-ARC-004] Thiết Kế Luồng Phê Duyệt 2 Cấp & Ủy Quyền Duyệt Thay Khi Quản Lý Đi Công Tác

- **Organization**: `ORG-NOVA` (`100% Synthetic Continuum Dataset`)
- **Project**: `NOVA-LEV`
- **Document Type**: `ARCHITECTURE`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `NV-U05`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `NVLEV-6`, `NVLEV-14`

> Máy trạng thái đơn nghỉ phép và quy tắc ủy quyền có thời hạn (Delegated Approver).

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `NV-U05` | `2026-07-09T10:00:00+07:00` | `NV-U02` | `2026-07-10T11:20:00+07:00` | Phê duyệt state machine SUBMITTED -> LINE_APPROVED -> HR_APPROVED / REJECTED / PARTIALLY_CANCELLED. |

## Chống Tự Duyệt (No Self-Approval)
- Ràng buộc approver_id != applicant_id ở cả tầng service và database check.
