# [DOC-NVHR-ARC-002] Kiến Trúc Tổng Thể Hệ Thống NovaHRMS Modular Monolith & Phân Quyền Dữ Liệu

- **Organization**: `ORG-NOVA` (`100% Synthetic Continuum Dataset`)
- **Project**: `NOVA-HR`
- **Document Type**: `ARCHITECTURE`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `NV-U03`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `NVHR-4`, `NVHR-6`

> Thiết kế kiến trúc 3 tầng tách biệt module Core HR, Attendance và Leave với kiểm soát truy cập theo đơn vị nhà máy/văn phòng.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `NV-U03` | `2026-06-18T09:30:00+07:00` | `NV-U01` | `2026-06-19T14:20:00+07:00` | Phê duyệt kiến trúc Modular Monolith trên PostgreSQL 16 + Redis cache phiên đăng nhập. |

## Kiến Trúc Modular Monolith
- Ba phân hệ hr_core, attendance và leave dùng chung PostgreSQL 16 schema tách biệt khóa ngoại rõ ràng, giảm chi phí vận hành cho doanh nghiệp 300 nhân sự.
- Mọi thay đổi hồ sơ hợp đồng và số dư phép đều ghi vào bảng audit_trail bất biến.
