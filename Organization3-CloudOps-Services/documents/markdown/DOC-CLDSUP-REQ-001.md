# [DOC-CLDSUP-REQ-001] Chính Sách SLA Hỗ Trợ Tier-3 Doanh Nghiệp, Quy Trình Truyền Thông Sự Cố & Đối Soát Tín Dụng Dịch Vụ

- **Organization**: `ORG-CLD` (`100% Synthetic Continuum Dataset`)
- **Project**: `CLD-SUP`
- **Document Type**: `REQUIREMENT`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `CLD-U06`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `CLDSUP-1`, `CLDSUP-9`, `CLDSUP-19`

> Quy định thời gian phản hồi đầu tiên cho khách hàng Enterprise (15 phút với P0) và nguyên tắc minh bạch nguyên nhân gốc.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `CLD-U06` | `2026-05-05T09:30:00+07:00` | `CLD-U02` | `2026-05-06T11:10:00+07:00` | Ban hành khung cam kết SLA hỗ trợ kỹ thuật Tier-3 và quy tắc gửi RCA cho khách hàng trong 3 ngày làm việc. |

## Cam Kết Phản Hồi & Truyền Thông Minh Bạch
- Phản hồi xác nhận đầu tiên cho khách hàng Enterprise trong 15 phút đối với P0 và 60 phút đối với P1.
- Tuyệt đối không gửi giả thuyết sơ bộ chưa được kiểm chứng (như bản nháp RCA v1) ra bản tin chính thức cho khách hàng.

## Cách Ly Dữ Liệu Giữa Các Tenant Trên Bản Tin Sự Cố
- Báo cáo gửi cho một khách hàng (ví dụ FinLedger) không bao giờ được tiết lộ tên, IP hay lưu lượng của bất kỳ tenant nào khác.
