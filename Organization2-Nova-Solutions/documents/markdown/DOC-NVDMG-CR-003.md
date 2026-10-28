# [DOC-NVDMG-CR-003] Biên Bản Đánh Giá Tác Động & Quyết Định Yêu Cầu Thay Đổi CR-2026-08 (Nghỉ Bù Tăng Ca)

- **Organization**: `ORG-NOVA` (`100% Synthetic Continuum Dataset`)
- **Project**: `NOVA-DMG`
- **Document Type**: `REQUIREMENT`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `NV-U07`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `NVATD-27`, `NVLEV-29`, `NVDMG-19`

> Tài liệu quản trị thay đổi Waterfall chốt việc tách CR-2026-08: duyệt xuất CSV đối soát ở Phase 1, hoãn sổ cái tự động nghỉ bù sang Phase 2.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `NV-U07` | `2026-09-22T13:30:00+07:00` | `NV-U01` | `2026-09-23T15:00:00+07:00` | Quyết định chính thức của Hội đồng Kiểm soát Thay đổi (CCB) giữa Nova Solutions và Minh Phát. |

## Bối Cảnh Đề Xuất Của Khách Hàng
- Ngày 21/09/2026 (giữa giai đoạn UAT), Giám đốc Nhân sự Minh Phát đề xuất thêm quy chế quy đổi giờ tăng ca cuối tuần thành quỹ nghỉ bù tự động hết hạn sau 90 ngày.

## Phân Tích Tác Động Waterfall
- Nếu đưa toàn bộ bộ máy tự động tính/trừ/hết hạn nghỉ bù vào Phase 1 sẽ phải thiết kế lại bảng leave_entitlements vừa chốt và làm trễ mốc Go-Live 30/10/2026 ít nhất 3 tuần.

## Quyết Định Chính Thức Của CCB
- Hạng mục được duyệt vào Phase 1: Bổ sung API và nút xuất CSV đối soát giờ tăng ca hợp lệ (task NVATD-27, tài liệu DOC-NVATD-API-003 v2).
- Hạng mục hoãn sang Phase 2: Sổ cái tự động cộng/trừ và hết hạn quỹ nghỉ bù (task NVLEV-29 chuyển trạng thái CANCELLED ở Phase 1).

## Bảng Tham Chiếu Chi Tiết
| Hạng Mục Trong CR-2026-08 | Quyết Định CCB | Mã Task Liên Quan |
| :--- | :--- | :--- |
| Xuất CSV đối soát giờ OT đủ điều kiện nghỉ bù | DUYỆT LÀM TRONG PHASE 1 | NVATD-27 (DONE) |
| Tự động quy đổi & hết hạn 90 ngày quỹ nghỉ bù | HOÃN SANG HỢP ĐỒNG PHASE 2 | NVLEV-29 (CANCELLED) |
