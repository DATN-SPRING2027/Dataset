# [DOC-CLDINF-ARC-001] Kiến Trúc Hạ Tầng Kubernetes Đa Tenant, Quản Trị WAF Qua Terraform IaC & Khóa Chống Sửa Tay

- **Organization**: `ORG-CLD` (`100% Synthetic Continuum Dataset`)
- **Project**: `CLD-INF`
- **Document Type**: `ARCHITECTURE`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `CLD-U05`
- **Displayed Content Version**: `v2` (`APPROVED`)
- **Linked Tasks**: `CLDINF-1`, `CLDINF-23`, `CLDINF-24`

> v1 kiến trúc cụm đa tenant; v2 cập nhật sau sự cố Thứ Bảy 26/09 (INC-2026-0926) bắt buộc khóa chỉnh sửa rule WAF ngoài GitOps.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `CLD-U05` | `2026-05-14T09:30:00+07:00` | `CLD-U01` | `2026-05-15T10:30:00+07:00` | Phê duyệt kiến trúc cụm Kubernetes phân tách workload và tường lửa biên WAF. |
| v2 | `APPROVED` | `CLD-U05` | `2026-09-29T09:30:00+07:00` | `CLD-U01` | `2026-09-30T11:10:00+07:00` | Siết chặt quản trị WAF bằng Terraform sau sự cố INC-2026-0926 chặn nhầm webhook FinLedger. |

## Kiểm Soát Trôi Cấu Hình (Terraform & WAF Drift)
- Sự cố INC-2026-0926 chiều Thứ Bảy 26/09 xảy ra do một rule chặn rate-limit sửa tay trên console làm chặn nhầm HTTP 403 đối với dải IP ký số của đối tác FinLedger.
- Từ bản v2, quyền chỉnh sửa console WAF ở chế độ thường trực bị chuyển về Read-Only; mọi thay đổi rule bắt buộc đi qua Terraform PR kèm kiểm thử danh sách allowlist webhook đối tác.
