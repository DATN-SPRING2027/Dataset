# [DOC-NVHR-REQ-001] FRS Phân Hệ Hồ Sơ Nhân Sự, Hợp Đồng & Dây Chuyền Báo Cáo (Minh Phát ~300 Nhân Viên)

- **Organization**: `ORG-NOVA` (`100% Synthetic Continuum Dataset`)
- **Project**: `NOVA-HR`
- **Document Type**: `REQUIREMENT`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `NV-U07`
- **Displayed Content Version**: `v2` (`APPROVED`)
- **Linked Tasks**: `NVHR-1`, `NVHR-2`, `NVHR-22`

> Đặc tả yêu cầu nghiệp vụ Core HR đã ký nghiệm thu cổng Waterfall Phase 2 và cập nhật quy tắc bàn giao quyền quản lý trực tiếp.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `NV-U07` | `2026-05-14T10:15:00+07:00` | `NV-U03` | `2026-05-15T15:10:00+07:00` | Baseline FRS v1.0 cho hồ sơ nhân sự, hợp đồng lao động và địa điểm làm việc. |
| v2 | `APPROVED` | `NV-U07` | `2026-07-08T09:20:00+07:00` | `NV-U02` | `2026-07-09T11:00:00+07:00` | Bổ sung quy tắc chặn vòng lặp dây chuyền quản lý trực tiếp (Report-To cycle detection) và tự động khóa tài khoản khi thôi việc. |

## Phạm Vi Nghiệp Vụ Core HR (Baseline v2.0)
- Hệ thống quản lý 312 nhân viên tại Văn phòng Quận 7 và Nhà máy Bình Dương; tuyệt đối không lưu dữ liệu bảng lương hay tài khoản ngân hàng chi lương.
- Khi ghi nhận quyết định thôi việc (Termination Record), trạng thái nhân sự chuyển sang TERMINATED vào cuối ngày làm việc cuối và thu hồi quyền đăng nhập.

## Quy Tắc Dây Chuyền Quản Lý (Supervisor Report-To)
- Mỗi nhân viên có đúng 01 Quản lý trực tiếp (Direct Supervisor) nhận đơn nghỉ phép bước 1 và tối đa 02 Quản lý phối hợp (Dotted-Line).
- Thuật toán kiểm tra đồ thị có hướng (DAG) chặn mọi thao tác gán quản lý tạo vòng lặp A -> B -> A.

## Bảng Tham Chiếu Chi Tiết
| Mã Quy Tắc | Mô Tả Ràng Buộc | Hành Vi Hệ Thống |
| :--- | :--- | :--- |
| BR-HR-01 | Mã nhân viên MP-XXXX duy nhất toàn doanh nghiệp | Từ chối HTTP 409 nếu trùng mã |
| BR-HR-02 | Chặn vòng lặp cây quản lý trực tiếp (DAG check) | Từ chối HTTP 422 REPORT_TO_CYCLE |
| BR-HR-03 | Phạm vi ngoài hợp đồng Phase 1 | Không lưu và không tính lương/thưởng |
