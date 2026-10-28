# [DOC-CLDINC-REQ-001] Chính Sách Phân Loại Sự Cố (SEV-0..SEV-3), Leo Thang Ca Trực 5 Phút & Shelve Có Thời Hạn

- **Organization**: `ORG-CLD` (`100% Synthetic Continuum Dataset`)
- **Project**: `CLD-INC`
- **Document Type**: `REQUIREMENT`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `CLD-U03`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `CLDINC-1`, `CLDINC-3`, `CLDINC-9`

> Quy chuẩn điều phối cảnh báo Kanban 24/7: tự động escalate sang Secondary sau 5 phút không ACK và giới hạn shelve tối đa 120 phút.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `CLD-U03` | `2026-04-28T09:30:00+07:00` | `CLD-U01` | `2026-04-29T10:45:00+07:00` | Ban hành chính sách phân loại sự cố, SLA nhận cảnh báo (ACK) và quy tắc tạm ẩn cảnh báo trùng. |

## Phân Loại Mức Độ Nghiêm Trọng & SLA Phản Hồi
- SEV-0 (ngừng dịch vụ đa tenant hoặc mất xác thực cốt lõi): ACK <= 5 phút, cập nhật bản tin trạng thái mỗi 30 phút.
- SEV-1 (suy giảm nghiêm trọng một phân hệ hoặc chặn nhầm luồng tích hợp đối tác lớn): ACK <= 15 phút.

## Quy Tắc Leo Thang Lịch Trực & Tạm Ẩn (Shelving)
- Nếu kỹ sư Primary On-Call không xác nhận (ACK) trong 5 phút, luồng Escalation tự động gọi Secondary On-Call và thông báo Incident Lead.
- Chỉ được tạm ẩn (shelve) nhóm cảnh báo trùng tối đa 120 phút khi đang thực thi giảm nhẹ tạm thời; hết hạn hệ thống tự động unshelve.

## Bảng Tham Chiếu Chi Tiết
| Mức Sự Cố | Thời Gian ACK Tối Đa | Quy Tắc Đóng Sự Cố |
| :--- | :--- | :--- |
| SEV-0 | 5 phút (tự động sang Secondary nếu quá hạn) | Không được đóng hoàn toàn khi mới có workaround tạm thời |
| SEV-1 | 15 phút | Bắt buộc gắn mã task khắc phục nguyên nhân gốc ở CLD-INF/CLD-OBS |
