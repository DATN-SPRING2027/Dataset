# [DOC-CLDINF-DB-002] Chuẩn Vận Hành PostgreSQL/PgBouncer Tách Pool & Quy Trình Migration Expand/Contract Không Gián Đoạn

- **Organization**: `ORG-CLD` (`100% Synthetic Continuum Dataset`)
- **Project**: `CLD-INF`
- **Document Type**: `DATABASE_DESIGN`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `CLD-U11`
- **Displayed Content Version**: `v2` (`APPROVED`)
- **Linked Tasks**: `CLDINF-9`, `CLDINF-10`, `CLDINF-19`, `CLDINF-20`

> Thay thế hoàn toàn sổ tay cũ DOC-CLDINF-RUN-006-LEGACY; quy định migration 3 bước tương thích ngược và tách riêng auth_pool khỏi reporting_pool.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `CHANGES_REQUESTED` | `CLD-U11` | `2026-08-20T10:00:00+07:00` | `CLD-U05` | `2026-08-21T10:30:00+07:00` | Dự thảo quy trình Expand/Contract sau sự cố INC-2026-0818. |
| v2 | `APPROVED` | `CLD-U11` | `2026-09-09T09:15:00+07:00` | `CLD-U01` | `2026-09-10T11:20:00+07:00` | Phê duyệt chính thức kiến trúc 2 pool PgBouncer độc lập (auth_pool & reporting_pool) và chuẩn DDL Expand/Contract. |

## Quy Trình Migration Expand/Contract 3 Bước (Thay Thế DOC-CLDINF-RUN-006-LEGACY)
- Bước 1 (Expand): Chỉ thêm cột nullable hoặc bảng mới kèm lock_timeout=2000ms; tuyệt đối cấm đổi kiểu cột trực tiếp hoặc xóa cột khi pod phiên bản cũ còn đang chạy trong rolling deploy.
- Bước 2 (Dual-Write & Backfill): Đợi 100% pod chuyển sang bản mới và chạy backfill theo lô nhỏ.
- Bước 3 (Contract): Chỉ dọn bỏ cột cũ ở bản phát hành kế tiếp sau khi xác nhận không còn truy vấn đọc/ghi.

## Kiến Trúc Phân Tách Pool PgBouncer Sau Sự Cố Quốc Khánh 02/09
- auth_pool dành riêng cho dịch vụ xác thực và kiểm tra phiên (60 kết nối, statement_timeout=3000ms).
- reporting_pool phục vụ xuất báo cáo và phân tích (tối đa 25 kết nối, trỏ thẳng sang cụm Read-Replica để không bao giờ gây nghẽn đăng nhập).

## Bảng Tham Chiếu Chi Tiết
| Tên Pool PgBouncer | Đích Kết Nối | Giới Hạn Bảo Vệ |
| :--- | :--- | :--- |
| auth_pool | PostgreSQL Primary | pool_size=60, statement_timeout=3000ms |
| reporting_pool | PostgreSQL Read-Replica | pool_size=25, statement_timeout=15000ms |
