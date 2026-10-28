# [DOC-NVLEV-DB-002] Thiết Kế Cơ Sở Dữ Liệu Nghỉ Phép Chuẩn Hóa v2.0 (Sổ Cái Bút Toán NUMERIC(5,2) Cho Nửa Ngày)

- **Organization**: `ORG-NOVA` (`100% Synthetic Continuum Dataset`)
- **Project**: `NOVA-LEV`
- **Document Type**: `DATABASE_DESIGN`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `NV-U12`
- **Displayed Content Version**: `v2` (`APPROVED`)
- **Linked Tasks**: `NVLEV-19`, `NVLEV-23`, `NVLEV-24`

> Bản thiết kế chính thức thay thế DOC-NVLEV-DB-001-LEGACY để khắc phục triệt để lỗi hoàn thừa 0.5 ngày phép khi hủy đơn một phần trong UAT.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `CHANGES_REQUESTED` | `NV-U12` | `2026-09-18T10:00:00+07:00` | `NV-U05` | `2026-09-21T10:30:00+07:00` | Chuyển cột duration sang NUMERIC(4,1). |
| v2 | `APPROVED` | `NV-U12` | `2026-09-22T09:10:00+07:00` | `NV-U01` | `2026-09-22T16:30:00+07:00` | Phê duyệt kiến trúc sổ cái leave_balance_ledger NUMERIC(5,2) kèm hoàn trả SUM(day_fraction) chính xác tuyệt đối. |

## Nguyên Nhân Gốc Lỗi UAT Hủy Phép Nửa Ngày
- Trong bản thiết kế cũ (DOC-NVLEV-DB-001-LEGACY), hàm hoàn phép đếm số bản ghi ngày nghỉ thay vì cộng trường trọng số ngày, làm đơn 2.5 ngày khi hủy buổi chiều cuối lại được hoàn 1.0 ngày thay vì 0.50 ngày.

## Thiết Kế Chuẩn Hóa v2.0 (Hiệu Lực Chính Thức)
- Bảng leave_request_items lưu day_fraction NUMERIC(5,2) CHECK (day_fraction IN (0.50, 1.00)).
- Bảng leave_balance_ledger ghi bút toán đối ứng (+0.50 hoặc -0.50) trong cùng transaction có khóa dòng trên leave_entitlements.

## Bảng Tham Chiếu Chi Tiết
| Bảng | Cột Cốt Lõi | Ràng Buộc Nghiệp Vụ |
| :--- | :--- | :--- |
| leave_request_items | day_fraction NUMERIC(5,2) | Chỉ nhận 0.50 hoặc 1.00; ngày lễ/cuối tuần = 0 (không tạo item trừ phép) |
| leave_balance_ledger | delta_days NUMERIC(5,2) | Tổng đại số delta_days luôn khớp used_days trên leave_entitlements |
