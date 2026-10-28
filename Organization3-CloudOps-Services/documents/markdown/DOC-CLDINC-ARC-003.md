# [DOC-CLDINC-ARC-003] Kiến Trúc Bộ Gom Nhóm Chống Bão Cảnh Báo (AlertGroup Fingerprint) & Tự Động Unshelve

- **Organization**: `ORG-CLD` (`100% Synthetic Continuum Dataset`)
- **Project**: `CLD-INC`
- **Document Type**: `ARCHITECTURE`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `CLD-U03`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `CLDINC-4`, `CLDINC-7`

> Gom các cảnh báo cùng chữ ký lỗi (service + cluster + error_class) trong cửa sổ trượt để ngăn bão thông báo ca trực.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `CLD-U03` | `2026-05-12T10:00:00+07:00` | `CLD-U01` | `2026-05-13T11:00:00+07:00` | Phê duyệt thuật toán băm SHA-256 fingerprint cho AlertGroup và worker quét hết hạn shelve mỗi 60 giây. |

## Cơ Chế Gom Nhóm & Mở Khóa Tự Động
- Worker CLD-BOT-ALERTGROUP tự động chuyển trạng thái từ SHELVED về OPEN ngay khi hết thời hạn tạm ẩn.
