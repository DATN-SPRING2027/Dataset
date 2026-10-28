# [DOC-MEDAPT-DB-002] Thiết Kế Cơ Sở Dữ Liệu Lịch Hẹn v2.0: Khóa Tương Tranh Slot & Bảng Kiểm Toán Dời Lịch (reschedule_audits)

- **Organization**: `ORG-MED` (`100% Synthetic Continuum Dataset`)
- **Project**: `MED-APT`
- **Document Type**: `DATABASE_DESIGN`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `MED-U10`
- **Displayed Content Version**: `v2` (`APPROVED`)
- **Linked Tasks**: `MEDAPT-14`, `MEDAPT-15`, `MEDAPT-18`

> Thay thế DOC-MEDAPT-DB-001-LEGACY trong Sprint 3 để chặn tuyệt đối đặt trùng slot và lưu lịch sử dời lịch hàng loạt.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `CHANGES_REQUESTED` | `MED-U10` | `2026-09-07T10:00:00+07:00` | `MED-U04` | `2026-09-08T10:20:00+07:00` | Thêm SELECT FOR UPDATE trên bảng doctor_time_slots. |
| v2 | `APPROVED` | `MED-U10` | `2026-09-09T09:20:00+07:00` | `MED-U01` | `2026-09-09T16:40:00+07:00` | Phê duyệt ràng buộc CHECK (booked_count <= capacity), thứ tự khóa ORDER BY slot_id ASC và bảng reschedule_audits. |

## Chống Đặt Trùng Slot Tuyệt Đối
- Kết hợp SELECT ... FOR UPDATE ORDER BY slot_id ASC với ràng buộc cứng CHECK (booked_count >= 0 AND booked_count <= capacity) ở tầng PostgreSQL.

## Lưu Vết Dời Lịch Theo CFB-2026-01
- Bảng reschedule_audits lưu batch_id, appointment_id, from_slot_id, to_slot_id, performed_by_role và reschedule_reason.
