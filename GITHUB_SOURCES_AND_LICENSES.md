# Nhật Ký Nguồn Tham Chiếu GitHub & Kiểm Soát Giấy Phép (Four-Organization Continuum Dataset)

Tài liệu này ghi nhận đầy đủ kết quả khảo sát thực tế các repository tham chiếu trên GitHub phục vụ thiết kế bộ dataset synthetic bốn organization cho **Continuum AI**, tuân thủ nghiêm ngặt quy tắc sử dụng nguồn của workspace `F:\LEARN KÌ 8\ĐATN`.

---

## 1. Bảng Tổng Hợp Phiên Bản, Commit, Giấy Phép & Thời Điểm Truy Cập

| Organization Dataset | Vai trò nguồn | URL Repository / Tài liệu | Tag / Release đã chọn | Commit SHA đã kiểm chứng | Thời điểm truy cập (`+07:00`) | Giấy phép & Điều kiện áp dụng |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Org 1 — Northstar** (`Dataset/Project1`) | Nguồn cảm hứng domain thương mại điện tử đa dự án (từ baseline v1.0–v1.3) | `https://github.com/bagisto/bagisto` | `v2.2.x` (baseline tham chiếu domain) | Ghi nhận tại `Dataset/Project1/README.md` | Kiểm tra lại `2026-10-28T08:17:08+07:00` | **MIT License** — chỉ tham khảo tên phân hệ thương mại điện tử (Catalog, Cart, Checkout, Inventory, Order, Payment, Search); không chép code PHP/Laravel. |
| **Org 2 — Nova Solutions** (`Dataset/Organization2-Nova-Solutions`) | Repo chính tham khảo nghiệp vụ HR, Chấm công, Nghỉ phép | `https://github.com/orangehrm/orangehrm` | `v5.9` | `56e23b3b09e7af29317a0943523b825843fff527` | `2026-10-28T08:17:08+07:00` | **`GPL-3.0-or-later`** (copyleft mạnh) — **Tuyệt đối không sao chép** code, SQL migration, tài liệu hay hình ảnh của OrangeHRM để tránh nhiễm điều khoản copyleft vào dataset. |
| **Org 3 — CloudOps Services** (`Dataset/Organization3-CloudOps-Services`) | Repo chính tham khảo lịch trực, gom cảnh báo, shelve và escalation | `https://github.com/roxy-wi/IncidentRelay` | `v2.4.0` | `21ea27d92927242ed499b7584a276f47cb1c68cd` | `2026-10-28T08:17:08+07:00` | **`Elastic-2.0`** (*Elastic License 2.0* — **source-available, KHÔNG phải giấy phép mã nguồn mở OSI**) — **Tuyệt đối không sao chép** code, schema hay tài liệu gốc. |
| **Org 3 — CloudOps Services** (`Dataset/Organization3-CloudOps-Services`) | Danh mục bổ sung tham khảo cách mô tả & phân tích sự cố | `https://github.com/danluu/post-mortems` | `master` | `630562e55281ff28961704e8042a7dc9569a96e7` | `2026-10-28T08:17:08+07:00` | **`license: null`** (Repo không có file `LICENSE`; là danh mục liên kết tới các bài postmortem bên thứ ba, mỗi bài chịu bản quyền riêng của đơn vị xuất bản) — **Không chép văn bản** từ bất kỳ bài viết liên kết nào. |
| **Org 4 — MediFlow** (`Dataset/Organization4-MediFlow`) | Repo chính tham khảo ranh giới định danh hành chính, địa điểm, lịch trực và quyền | `https://github.com/openmrs/openmrs-core` | `2.8.10` / `master` | `0755f785f7d237a7a2e9d9f4e76aff43b7613ad3` | `2026-10-28T08:17:08+07:00` | **`MPL-2.0` kèm *OpenMRS Public License Exhibit B (Healthcare Disclaimer)*** — Chỉ tham khảo khái niệm hành chính; loại trừ hoàn toàn thực thể bệnh án lâm sàng; không chép code Java/XML. |
| **Org 4 — MediFlow** (`Dataset/Organization4-MediFlow`) | Tài liệu bổ trợ về đăng ký hành chính, trạng thái lịch hẹn và hàng đợi lễ tân | `https://github.com/openmrs/openmrs-contrib-o3-docs/blob/main/content/en-US/docs/configure-o3/configure-patient-management.mdx` | `main` | `3a0da981e31e224a467a4432df2a65cb8dfdfe7b` | `2026-10-28T08:17:08+07:00` | **`MPL-2.0`** — Chỉ tham khảo ý tưởng cấu hình biểu mẫu đăng ký, trạng thái lịch hẹn và tùy chọn bảo vệ số điện thoại khi xuất bảng tính; tự viết mới 100% bằng tiếng Việt. |

---

## 2. Chi Tiết Các Tài Nguyên Đã Khảo Sát & Phân Loại Ba Tầng Thông Tin

### 2.1. Organization 2 — Nova Solutions (`orangehrm/orangehrm` @ `v5.9`)
- **File & Issue đã kiểm tra thực tế**:
  - `LICENSE`, `README.md`, cây thư mục `src/plugins/` (`orangehrmPimPlugin`, `orangehrmLeavePlugin`, `orangehrmAttendancePlugin`, `orangehrmAdminPlugin`).
  - Các public issue công khai để hiểu bài toán thực tế của phần mềm HR: `#1964`, `#1965`, `#1966` (các tình huống cấu hình ca, tính ngày nghỉ và phân quyền quản lý trực tiếp).
- **Phân biệt rạch ròi 3 tầng thông tin**:
  1. *Đã xác minh từ nguồn*: OrangeHRM v5.9 tách mô-đun PIM (hồ sơ nhân sự & dây chuyền Report-To), Attendance (punch in/out) và Leave (quỹ phép, nghỉ một phần ngày, lịch nghỉ lễ); phát hành theo `GPL-3.0-or-later`.
  2. *Do nhóm tự thiết kế*: Kiến trúc Modular Monolith trên PostgreSQL 16 của **Nova Solutions**, phạm vi hợp đồng cho khách hàng ~300 nhân viên (**Minh Phát — 312 nhân sự**), loại trừ Payroll/BHXH, phương pháp **Waterfall 6 cổng giai đoạn**, quyết định tách yêu cầu thay đổi `CR-2026-08` và sổ cái `leave_balance_ledger NUMERIC(5,2)`.
  3. *Dữ liệu synthetic 100%*: Toàn bộ 23 nhân sự (`NV-U01..19`, `MP-U01..04`, email `@*.invalid`), 128 task, 84 Task Note, 24 Project Document, 36 Work Report, sự kiện nghỉ việc `NV-U19`, nghỉ ốm `NV-U09`, mất điện mưa bão Quận 7 `NV-U13` và 56 câu hỏi benchmark.
- **Giới hạn tuân thủ**: Không khẳng định OrangeHRM phát triển theo Waterfall; không khẳng định OrangeHRM có sẵn Task Note hay Work Report của Continuum; không gán sự kiện cá nhân cho bất kỳ contributor nào của OrangeHRM.

### 2.2. Organization 3 — CloudOps Services (`roxy-wi/IncidentRelay` @ `v2.4.0` & `danluu/post-mortems`)
- **File & Issue đã kiểm tra thực tế**:
  - `roxy-wi/IncidentRelay`: `LICENSE`, `LICENSING.md` (xác minh `Elastic-2.0`), `README.md`, cấu trúc `app/modules/`, `app/services/`, `app/scheduler_worker.py`, `docs/incidents/`, `docs/scheduling/`, và các public issue `#127`, `#128`, `#130`.
  - `danluu/post-mortems`: `README.md` (danh mục phân loại nhóm nguyên nhân sự cố hạ tầng: sai lệch cấu hình biên/WAF, khóa bảng khi deploy schema, bão hòa connection pool).
- **Phân biệt rạch ròi 3 tầng thông tin**:
  1. *Đã xác minh từ nguồn*: IncidentRelay `v2.4.0` có khái niệm gom nhóm cảnh báo (`AlertGroup`), tạm ẩn cảnh báo có thời hạn tự mở lại (`shelving`), chính sách leo thang nhiều bước (`escalation policy`), ghi đè lịch trực (`on-call override`) và giám sát xung nhịp (`heartbeat`); mã nguồn chịu điều khoản `Elastic-2.0`. Repo `danluu/post-mortems` không có giấy phép chung (`license: null`).
  2. *Do nhóm tự thiết kế*: Bối cảnh dịch vụ SRE đa tenant **CloudOps Services**, phương pháp **Kanban liên tục** với giới hạn WIP và SLE (`KBP-*`), mô hình tách `auth_pool` / `reporting_pool` trên PgBouncer và quy trình khóa sửa tay WAF bằng Terraform.
  3. *Dữ liệu synthetic 100%*: Toàn bộ 23 người dùng (`CLD-U01..18`, `FL-U01..03`, `VC-U01..02`), 3 bot 24/7 (`CLD-BOT-*`), 3 sự cố giả lập (`INC-2026-0818`, `INC-2026-0902` lễ Quốc khánh 02/09, `INC-2026-0926` Thứ Bảy), 128 task, 81 Task Note, 24 Project Document, 36 Work Report và 56 câu hỏi benchmark.
- **Giới hạn tuân thủ**: Không sao chép bất kỳ dòng code/tài liệu `Elastic-2.0` hay bài postmortem bên thứ ba nào; không khẳng định IncidentRelay dùng Kanban.

### 2.3. Organization 4 — MediFlow (`openmrs/openmrs-core` @ `2.8.10` & `openmrs-contrib-o3-docs`)
- **File & PR đã kiểm tra thực tế**:
  - `openmrs/openmrs-core`: `LICENSE` (MPL-2.0 + Healthcare Disclaimer), `README.md`, cây đối tượng hành chính `api/src/main/java/org/openmrs/` (`Person`, `PatientIdentifier`, `Provider`, `Location`, `Visit`, `Role`, `Privilege`), hoạt động PR công khai (`#6758`).
  - `openmrs/openmrs-contrib-o3-docs`: `LICENSE` (MPL-2.0) và file `content/en-US/docs/configure-o3/configure-patient-management.mdx` (cấu hình biểu mẫu đăng ký, trạng thái lịch hẹn `Requested/Scheduled/CheckedIn/Completed/Cancelled/Missed`, phân loại `Scheduled/WalkIn`, hàng đợi tiếp đón và cờ bảo mật `includePhoneNumberInExcelSpreadsheet: false`).
- **Phân biệt rạch ròi 3 tầng thông tin**:
  1. *Đã xác minh từ nguồn*: Tài liệu O3 mô tả vòng đời trạng thái lịch hẹn phòng khám ngoại trú, cấu hình trường đăng ký và tùy chọn không xuất số điện thoại ra file Excel.
  2. *Do nhóm tự thiết kế*: Mô hình quản lý dự án **Hybrid** cấp project (3 dự án sản phẩm `MED-REG`, `MED-APT`, `MED-ADM` kết hợp 4 cổng Milestone + 5 Sprint 2 tuần; 1 dự án thực địa `MED-PIL` chạy theo cổng Milestone không dùng Sprint), luồng đánh giá 3 phản hồi từ phòng khám (`CFB-2026-01` duyệt, `CFB-2026-02` bác bỏ, `CFB-2026-03` chờ đánh giá) và ranh giới **100% phi lâm sàng**.
  3. *Dữ liệu synthetic 100%*: Phòng khám giả lập **An Khang**, đối tác nhắn tin giả lập **VietNotify**, 22 người dùng (`@*.invalid`), 15 Sprint, 128 task, 82 Task Note, 24 Project Document, 36 Work Report và 56 câu hỏi benchmark. **Không có bất kỳ bệnh án, chẩn đoán, đơn thuốc hay thông tin bệnh nhân thật nào.**

---

## 3. Cam Kết Kiểm Toán An Toàn Bản Quyền & Đạo Đức Dữ Liệu

1. **Zero Copied Upstream Assets**: 0% mã nguồn, câu chữ tài liệu, biểu đồ, ảnh chụp hay dữ liệu mẫu từ các kho `GPL-3.0-or-later`, `Elastic-2.0`, `MPL-2.0` hoặc bài viết postmortem ngoài được sao chép vào bốn gói dataset.
2. **Zero Real Person Attribution**: Mọi nhân vật, email (`@*.invalid`), mã hồ sơ hành chính và các sự kiện nghỉ ốm, mưa bão, làm lại (rework) hay nghỉ việc đều là giả lập 100%, không gắn với bất kỳ cá nhân hay tổ chức có thật nào.
3. **Zero Clinical / Real PII Content**: Được kiểm tra tự động bằng bộ test `Dataset/tests/test_four_organizations.py`.
