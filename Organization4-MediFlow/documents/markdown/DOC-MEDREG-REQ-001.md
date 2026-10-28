# [DOC-MEDREG-REQ-001] Đặc Tả Yêu Cầu Đăng Ký Hồ Sơ Hành Chính Giả Lập & Ranh Giới Phi Lâm Sàng (Milestone M1)

- **Organization**: `ORG-MED` (`100% Synthetic Continuum Dataset`)
- **Project**: `MED-REG`
- **Document Type**: `REQUIREMENT`
- **Current Snapshot Status**: `APPROVED`
- **Author (`created_by`)**: `MED-U07`
- **Displayed Content Version**: `v1` (`APPROVED`)
- **Linked Tasks**: `MEDREG-1`, `MEDREG-4`, `MEDREG-15`

> Quy định phạm vi đăng ký hành chính tại quầy tiếp đón An Khang (mã AK-PAT-XXXXXX), che mặt nạ số liên lạc và cấm lưu dữ liệu lâm sàng.

## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)
| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| v1 | `APPROVED` | `MED-U07` | `2026-05-19T09:30:00+07:00` | `MED-U02` | `2026-05-20T11:10:00+07:00` | Chốt phạm vi Milestone M1: 100% thông tin hành chính tiếp đón, loại trừ hoàn toàn hồ sơ bệnh án. |

## Ranh Giới Phạm Vi Hành Chính Bắt Buộc
- Chỉ thu thập trường hành chính phục vụ xếp lịch hẹn và tiếp đón tại quầy.
- Cấm tạo trường dữ liệu tự do lưu thông tin chuyên môn y khoa hoặc tệp đính kèm kết quả khám.

## Quy Tắc Chống Trùng Hồ Sơ & Che Mặt Nạ Liên Lạc
- Kiểm tra trùng tổ hợp (họ tên chuẩn hóa + năm sinh + băm SHA-256 số liên lạc) trước khi cấp mã AK-PAT-XXXXXX mới.
- Màn hình tìm kiếm mặc định chỉ hiển thị 3 chữ số cuối của số liên lạc (ví dụ ***-***-482).

## Bảng Tham Chiếu Chi Tiết
| Nhóm Dữ Liệu | Trạng Thái Hỗ Trợ | Ghi Chú Quản Trị |
| :--- | :--- | :--- |
| Mã hành chính AK-PAT-XXXXXX & khung giờ hẹn | HỖ TRỢ CHÍNH THỨC | Phục vụ tiếp đón Pilot Giai đoạn 1 |
| Hồ sơ chuyên môn khám / kết quả xét nghiệm / thuốc | LOẠI TRỪ HOÀN TOÀN | Nằm ngoài phạm vi sản phẩm MediFlow |
