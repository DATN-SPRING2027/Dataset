# [DOC-CLDINC-RCA-002] Báo Cáo Hậu Kiểm (Postmortem) Sự Cố SEV-0 Quốc Khánh 02/09 (INC-2026-0902): Bão Kết Nối PgBouncer

- **Organization**: `ORG-CLD` (`100% Synthetic Continuum Dataset`)
- **Project**: `CLD-INC`
- **Document Type**: `TECHNICAL_SPECIFICATION`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `CLD-U08`
- **Displayed Content Version**: `v2` (`APPROVED`)
- **Linked Tasks**: `CLDINC-9`, `CLDINC-10`

> v1 nghi ngờ nhầm lỗi DNS nội bộ đã bị bác bỏ; v2 được phê duyệt xác nhận nguyên nhân gốc là dùng chung pool PgBouncer giữa luồng xác thực và báo cáo nặng.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `CHANGES_REQUESTED` | `CLD-U08` | `2026-09-03T10:15:00+07:00` | `CLD-U01` | `2026-09-04T11:20:00+07:00` | Dự thảo sơ bộ giả thuyết nghẽn phân giải CoreDNS nội bộ (ĐÃ BỊ BÁC BỎ). |
| v2 | `APPROVED` | `CLD-U08` | `2026-09-07T09:40:00+07:00` | `CLD-U01` | `2026-09-08T10:30:00+07:00` | Xác nhận nguyên nhân gốc do cạn kiệt pool PgBouncer dùng chung và chốt hành động phòng ngừa tách pool tại CLDINF-19. |

## Diễn Biến & Leo Thang Ca Trực Ngày Lễ 02/09
- Lúc 09:12+07:00 ngày 02/09/2026, bot CLD-BOT-HEARTBEAT phát hiện mất nhịp dịch vụ xác thực. Do mưa bão làm đứt cáp quang nhà riêng của Primary On-Call CLD-U07 (DIS-CLD-STORM-01), hệ thống tự động leo thang sang Secondary On-Call CLD-U08 lúc 09:17+07:00.

## Phân Biệt Giảm Nhẹ Tạm Thời vs Khắc Phục Nguyên Nhân Gốc
- Giảm nhẹ tạm thời (Temporary Workaround — task CLDINC-9): CLD-U08 ngắt các truy vấn báo cáo treo, điều hướng tạm sang read-replica và shelve cảnh báo trùng 120 phút để khôi phục đăng nhập lúc 09:46+07:00.
- Khắc phục triệt để (Permanent Root-Cause Fix — task CLDINF-19): Tách riêng auth_pool và reporting_pool trên PgBouncer kèm áp ngưỡng statement_timeout=3000ms cho luồng xác thực.

## Bảng Tham Chiếu Chi Tiết
| Hạng Mục | Mã Thực Thi | Tính Chất Kỹ Thuật |
| :--- | :--- | :--- |
| Chuyển hướng read-replica & shelve 120 phút | CLDINC-9 (Task Note workaround) | Giảm nhẹ tạm thời — KHÔNG phải bản sửa gốc |
| Tách auth_pool PgBouncer & áp statement_timeout=3000ms | CLDINF-19 + DOC-CLDINF-DB-002 v2 | Khắc phục triệt để nguyên nhân gốc |
