# [DOC-MEDAPT-REQ-001] FRS Quản Lý Lịch Trực Bác Sĩ, Vòng Đời Lịch Hẹn & Quyền Lễ Tân Dời Lịch Hộ (Cập Nhật Sau Demo M2)

- **Organization**: `ORG-MED` (`100% Synthetic Continuum Dataset`)
- **Project**: `MED-APT`
- **Document Type**: `REQUIREMENT`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `MED-U07`
- **Displayed Content Version**: `v2` (`APPROVED`)
- **Linked Tasks**: `MEDAPT-1`, `MEDAPT-18`, `MEDAPT-19`

> v1 quy định vòng đời lịch hẹn chuẩn; v2 bổ sung luồng Lễ tân trưởng dời lịch hàng loạt có kiểm toán theo phản hồi được duyệt CFB-2026-01.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `MED-U07` | `2026-05-26T09:20:00+07:00` | `MED-U04` | `2026-05-27T11:00:00+07:00` | Baseline vòng đời lịch hẹn Requested -> Scheduled -> CheckedIn -> Completed / Cancelled / Missed. |
| v2 | `APPROVED` | `MED-U07` | `2026-09-03T09:30:00+07:00` | `MED-U02` | `2026-09-04T10:45:00+07:00` | Cập nhật chính thức theo quyết định duyệt phản hồi Demo M2 (CFB-2026-01): cho phép Lễ tân trưởng dời lịch hàng loạt khi ca bác sĩ thay đổi. |

## Vòng Đời Trạng Thái Lịch Hẹn Chuẩn Hóa
- Trạng thái hợp lệ: Requested, Scheduled, CheckedIn, Completed, Cancelled, Missed.
- Không cho phép dời lịch đối với các bản ghi đã ở trạng thái Completed hoặc Cancelled.

## Quyền Dời Lịch Hộ Có Kiểm Toán (Theo Phản Hồi Được Duyệt CFB-2026-01)
- Chỉ vai trò RECEPTION_SHIFT_LEAD hoặc Quản trị vận hành mới được kích hoạt dời lịch thay người khám khi phát sinh thay đổi lịch bác sĩ.
- Mỗi thao tác bắt buộc lưu actor_id, old_slot_id, new_slot_id, reschedule_reason và gửi tin nhắn xác nhận giờ mới.

## Bảng Tham Chiếu Chi Tiết
| Mã Quy Tắc | Vai Trò Thực Thi | Điều Kiện Bắt Buộc |
| :--- | :--- | :--- |
| BR-APT-01 | Mọi vai trò đặt lịch | Không vượt quá sức chứa tối đa của slot 15 phút |
| BR-APT-02 (CFB-2026-01) | RECEPTION_SHIFT_LEAD | Bắt buộc có reschedule_reason + ghi audit_log + gửi thông báo |
