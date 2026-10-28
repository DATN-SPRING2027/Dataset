"""Deterministic generator for Organization 2 — Nova Solutions (Waterfall HR, Attendance & Leave)."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

PKG_ROOT = Path(__file__).resolve().parents[1]
DATASET_ROOT = PKG_ROOT.parent
sys.path.insert(0, str(DATASET_ROOT / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from continuum_synth import VN_HOLIDAYS_2026, build_working_days  # noqa: E402
from nova_docs_and_eval import REPORT_NARRATIVES, build_nova_doc_specs, build_nova_eval_cases  # noqa: E402
from nova_specs import (  # noqa: E402
    AS_OF_DATE,
    CHANGE_REQUEST_RECORDS,
    DISRUPTION_EVENTS,
    IMPLEMENTATION_ASSUMPTIONS,
    NAMESPACE,
    ORG_ADMIN_IDS,
    ORG_SPECS,
    PRIMARY_ORG_ID,
    PROJECT_SPECS,
    SIM_START,
    SOURCE_ATTRIBUTION,
    USER_SPECS,
    WATERFALL_PHASE_GATES,
)
from org_package_builder import (  # noqa: E402
    build_org_identity_graph,
    build_standard_negative_fixtures,
    build_work_reports_for_org,
    expand_project_tasks,
    make_eval_case,
    materialize_organization_package,
    render_project_documents_and_versions,
)


def _make_waterfall_project_blueprints(pid: str, members: list[str]) -> list[dict[str, Any]]:
    """Create 32 rich Waterfall task blueprints (sprint_id=None) spanning all 6 gated phases."""
    topics = {
        "NOVA-HR": [
            ("Khảo sát quy trình quản lý 312 hồ sơ nhân sự Minh Phát tại Quận 7 & Bình Dương", "STORY", "DONE", "2026-04-20", "WFG-NOVA-01"),
            ("Phân tích ma trận phân quyền xem hồ sơ theo địa điểm Văn phòng / Nhà máy", "TASK", "DONE", "2026-05-04", "WFG-NOVA-01"),
            ("Chốt đặc tả FRS v1.0 cho mã nhân viên MP-XXXX và loại hợp đồng lao động", "STORY", "DONE", "2026-05-20", "WFG-NOVA-02"),
            ("Thiết kế kiến trúc Modular Monolith & ranh giới audit_trail phân hệ Core HR", "TASK", "DONE", "2026-06-16", "WFG-NOVA-03"),
            ("Thiết kế bảng employees, employment_contracts và chỉ mục report_to_edges", "TASK", "DONE", "2026-06-23", "WFG-NOVA-03"),
            ("Thiết kế thuật toán DAG phát hiện vòng lặp dây chuyền quản lý trực tiếp", "TASK", "DONE", "2026-06-30", "WFG-NOVA-03"),
            ("Xây dựng API CRUD nhân viên kèm che mặt nạ số định danh cá nhân", "STORY", "DONE", "2026-07-21", "WFG-NOVA-04"),
            ("Xây dựng dịch vụ kiểm tra hiệu lực nối tiếp của hợp đồng lao động", "TASK", "DONE", "2026-07-28", "WFG-NOVA-04"),
            ("Cài đặt partial unique index đảm bảo đúng 01 Direct Supervisor đang hiệu lực", "TASK", "DONE", "2026-08-04", "WFG-NOVA-04"),
            ("Xây dựng endpoint POST /api/v1/employees/{id}/termination thu hồi JWT tức thời", "STORY", "DONE", "2026-08-11", "WFG-NOVA-04"),
            ("Xây dựng bộ lọc nhân sự theo phòng ban, ca làm việc và trạng thái hợp đồng", "TASK", "DONE", "2026-08-18", "WFG-NOVA-04"),
            ("Tích hợp ghi vết kiểm toán (audit_trail) khi thay đổi người duyệt phép trực tiếp", "TASK", "DONE", "2026-08-24", "WFG-NOVA-04"),
            ("Xây dựng giao diện danh sách nhân sự mật độ cao cho chuyên viên C&B", "STORY", "DONE", "2026-08-28", "WFG-NOVA-04"),
            ("Viết bộ unit test chặn vòng lặp quản lý trực tiếp 3 tầng A->B->C->A", "TASK", "DONE", "2026-09-03", "WFG-NOVA-04"),
            ("Sửa lỗi hiển thị sai phòng ban khi nhân sự điều chuyển từ nhà máy về văn phòng", "BUG", "DONE", "2026-09-15", "WFG-NOVA-05"),
            ("Kiểm thử tích hợp SIT luồng thôi việc tự động khóa đăng nhập và chuyển người duyệt", "TASK", "DONE", "2026-09-17", "WFG-NOVA-05"),
            ("Tối ưu truy vấn đệ quy CTE cho cây sơ đồ tổ chức 312 nhân sự dưới 80ms", "TASK", "DONE", "2026-09-22", "WFG-NOVA-05"),
            ("Xử lý phản hồi UAT: bổ sung cảnh báo hợp đồng thử việc sắp hết hạn trước 7 ngày", "STORY", "DONE", "2026-09-28", "WFG-NOVA-05"),
            ("Sửa lỗi lọc trùng nhân sự kiêm nhiệm Dotted-Line trên báo cáo biên chế", "BUG", "DONE", "2026-09-30", "WFG-NOVA-05"),
            ("Thực thi bộ 36 kịch bản nghiệm thu UAT phân quyền chi nhánh Core HR", "TASK", "DONE", "2026-10-05", "WFG-NOVA-05"),
            ("Chuẩn hóa danh mục chức danh tiếng Việt - tiếng Anh trước đợt cutover", "TASK", "DONE", "2026-10-08", "WFG-NOVA-05"),
            ("Subtask bàn giao nghỉ ốm (DIS-NOVA-SICK-01): hoàn thiện binding UI cây quản lý trực tiếp", "TASK", "DONE", "2026-09-07", "WFG-NOVA-04"),
            ("Subtask kiểm chứng thu hồi token tức thời cho nhân sự nghỉ việc trong ngày", "TASK", "DONE", "2026-08-13", "WFG-NOVA-04"),
            ("Ký xác nhận biên bản kiểm thử UAT phân hệ Hồ sơ nhân sự với Minh Phát", "TASK", "DONE", "2026-10-09", "WFG-NOVA-05"),
            ("Đánh giá hiệu năng bản nháp v2 xuất PDF sơ đồ cây nhân sự (DOC-NVHR-DES-005)", "STORY", "IN_REVIEW", "2026-10-13", "WFG-NOVA-06"),
            ("Rà soát ánh xạ mã quản lý trực tiếp cho 12 tổ trưởng xưởng sản xuất Bình Dương", "TASK", "IN_PROGRESS", "2026-10-13", "WFG-NOVA-06"),
            ("Cập nhật tài liệu hướng dẫn quản trị danh mục phòng ban cho chuyên viên HR", "TASK", "IN_PROGRESS", "2026-10-14", "WFG-NOVA-06"),
            ("Kiểm tra quyền chỉ đọc cho tài khoản kiểm toán nội bộ mùa quyết toán cuối năm", "TASK", "TODO", "2026-10-15", "WFG-NOVA-06"),
            ("Khóa cấu hình danh mục loại hợp đồng trên môi trường Production trước giờ cutover", "TASK", "TODO", "2026-10-16", "WFG-NOVA-06"),
            ("Hủy yêu cầu tích hợp cổng đồng bộ danh bạ LDAP cũ đã ngừng vận hành", "TASK", "CANCELLED", "2026-07-22", "WFG-NOVA-04"),
            ("Đối chiếu quyền truy cập hồ sơ của 4 điều phối viên ca nhà máy trên bản staging", "TASK", "IN_REVIEW", "2026-10-14", "WFG-NOVA-06"),
            ("Chờ Minh Phát chốt quyết định bổ nhiệm trưởng bộ phận kho mới để gán cây duyệt", "TASK", "BLOCKED", "2026-10-12", "WFG-NOVA-06"),
        ],
        "NOVA-ATD": [
            ("Khảo sát 03 máy chấm công vân tay tại Nhà máy Bình Dương và Văn phòng Quận 7", "STORY", "DONE", "2026-04-21", "WFG-NOVA-01"),
            ("Thu thập quy chế ca hành chính, ca sáng/chiều nhà máy và ca bảo trì đêm", "TASK", "DONE", "2026-05-06", "WFG-NOVA-01"),
            ("Chốt đặc tả FRS khấu trừ 60 phút nghỉ trưa (12:00-13:00) và ân hạn trễ 5 phút", "STORY", "DONE", "2026-05-25", "WFG-NOVA-02"),
            ("Thiết kế cơ chế chống ghi đúp raw_punch_logs bằng uq_device_emp_punch", "TASK", "DONE", "2026-06-22", "WFG-NOVA-03"),
            ("Thiết kế bảng work_shifts, shift_assignments và daily_attendance_records", "TASK", "DONE", "2026-06-26", "WFG-NOVA-03"),
            ("Thiết kế chữ ký HMAC xác thực thiết bị đồng bộ vân tay", "TASK", "DONE", "2026-07-03", "WFG-NOVA-03"),
            ("Phát triển worker tiếp nhận batch 1.000 lượt quét vân tay idempotent", "STORY", "DONE", "2026-07-22", "WFG-NOVA-04"),
            ("Cài đặt logic tự động khấu trừ giờ nghỉ trưa 12:00-13:00 cho khối văn phòng", "TASK", "DONE", "2026-07-29", "WFG-NOVA-04"),
            ("Xây dựng giao diện bảng công tháng kèm đánh dấu đi trễ / về sớm / thiếu vân tay", "STORY", "DONE", "2026-08-05", "WFG-NOVA-04"),
            ("Xây dựng luồng phiếu giải trình quên quét vân tay có quản lý trực tiếp phê duyệt", "STORY", "DONE", "2026-08-12", "WFG-NOVA-04"),
            ("Xây dựng API POST /api/v1/attendance/punches:batch và kiểm thử retry mạng chập chờn", "TASK", "DONE", "2026-08-18", "WFG-NOVA-04"),
            ("Cài đặt thuật toán Shift Anchor Window ghép cặp giờ vào/ra ca đêm vắt qua 00:00", "STORY", "DONE", "2026-08-21", "WFG-NOVA-04"),
            ("Viết bộ kiểm thử tự động cho ca đêm 22:00-06:00 chuyển giao sang ngày lễ", "TASK", "DONE", "2026-08-26", "WFG-NOVA-04"),
            ("Xây dựng bộ đối soát giờ tăng ca buổi tối (chỉ tính từ 17:30 khi có phiếu OT duyệt)", "TASK", "DONE", "2026-09-04", "WFG-NOVA-04"),
            ("Sửa lỗi lệch 1 phút khi làm tròn giây từ đầu đọc vân tay cổng phụ Bình Dương", "BUG", "DONE", "2026-09-16", "WFG-NOVA-05"),
            ("Kiểm thử tích hợp bảng công tự động hiển thị ký hiệu nghỉ phép P / P/2 từ NOVA-LEV", "TASK", "DONE", "2026-09-18", "WFG-NOVA-05"),
            ("Đóng gói SQLite buffer mã hóa AES-256 lưu tối đa 7 ngày khi đứt WAN nhà máy", "TASK", "DONE", "2026-08-25", "WFG-NOVA-04"),
            ("Kiểm thử diễn tập ngắt mạng giả lập 48 giờ và đẩy bù FIFO 4.200 lượt quét thẻ", "TASK", "DONE", "2026-09-23", "WFG-NOVA-05"),
            ("Tối ưu tốc độ tổng hợp bảng công tháng 312 nhân sự xuống dưới 3 giây", "TASK", "DONE", "2026-09-29", "WFG-NOVA-05"),
            ("Subtask kiểm thử phân quyền chỉ HR/C&B Admin tải được file đối soát OT", "TASK", "DONE", "2026-09-30", "WFG-NOVA-05"),
            ("Hoàn thành UAT đối chiếu bảng công mẫu tháng 08 của 50 công nhân xưởng đóng gói", "TASK", "DONE", "2026-10-06", "WFG-NOVA-05"),
            ("Cập nhật tài liệu vận hành agent đồng bộ máy chấm công cho IT Minh Phát", "TASK", "DONE", "2026-10-08", "WFG-NOVA-05"),
            ("Sửa lỗi hiển thị nhãn ca gãy trên trình duyệt màn hình hẹp của tổ trưởng xưởng", "BUG", "IN_REVIEW", "2026-10-13", "WFG-NOVA-06"),
            ("Cấu hình lịch khóa sổ chấm công tự động vào 17:00 ngày 03 hằng tháng", "TASK", "IN_PROGRESS", "2026-10-13", "WFG-NOVA-06"),
            ("Kiểm tra đồng bộ NTP trên máy chủ thu thập log chấm công trước ngày Go-Live", "TASK", "IN_PROGRESS", "2026-10-14", "WFG-NOVA-06"),
            ("Chuẩn bị script đối chiếu nhanh tổng giờ OT tháng 10 ngay sau đêm cutover", "TASK", "TODO", "2026-10-15", "WFG-NOVA-06"),
            ("Triển khai API xuất CSV giờ tăng ca đủ điều kiện nghỉ bù theo CR-2026-08 (Phase 1)", "STORY", "DONE", "2026-09-24", "WFG-NOVA-05"),
            ("Subtask viết bài kiểm thử định dạng cột UTF-8 BOM cho CSV đối soát nghỉ bù", "TASK", "DONE", "2026-09-28", "WFG-NOVA-05"),
            ("Kiểm tra cảnh báo thiết bị chấm công mất kết nối quá 30 phút qua webhook nội bộ", "TASK", "IN_REVIEW", "2026-10-15", "WFG-NOVA-06"),
            ("Hủy task thử nghiệm chấm công GPS nền trên điện thoại cá nhân (DOC-NVATD-DES-006 REJECTED)", "STORY", "CANCELLED", "2026-08-19", "WFG-NOVA-04"),
            ("Chờ IT Minh Phát mở tường lửa cổng 8443 cho đầu đọc vân tay dự phòng xưởng số 3", "TASK", "BLOCKED", "2026-10-12", "WFG-NOVA-06"),
            ("Tập huấn thao tác xử lý bảng công ngoại lệ cho chuyên viên C&B", "TASK", "TODO", "2026-10-16", "WFG-NOVA-06"),
        ],
        "NOVA-LEV": [
            ("Khảo sát chính sách phép năm 12/14 ngày, cộng thâm niên 5 năm và nghỉ việc riêng có lương", "STORY", "DONE", "2026-04-22", "WFG-NOVA-01"),
            ("Xác định ma trận phê duyệt 1 cấp (< 3 ngày) và 2 cấp (>= 3 ngày: Supervisor -> HR)", "TASK", "DONE", "2026-05-08", "WFG-NOVA-01"),
            ("Soạn thảo baseline FRS phân hệ Nghỉ phép (do BA NV-U19 thực hiện trước khi nghỉ việc)", "STORY", "DONE", "2026-06-02", "WFG-NOVA-02"),
            ("Thiết kế sơ bộ bảng nghỉ phép v1.0 (sau này được thay thế bởi sổ cái v2.0)", "TASK", "DONE", "2026-06-22", "WFG-NOVA-03"),
            ("Thiết kế lịch ngày lễ Việt Nam và lịch làm việc theo khối Văn phòng / Nhà máy", "TASK", "DONE", "2026-06-29", "WFG-NOVA-03"),
            ("Thiết kế máy trạng thái phê duyệt đơn phép và quy tắc cấm tự phê duyệt", "TASK", "DONE", "2026-07-07", "WFG-NOVA-03"),
            ("Xây dựng bộ tính quỹ phép đầu năm và cộng thêm 1 ngày mỗi 5 năm thâm niên", "STORY", "DONE", "2026-07-23", "WFG-NOVA-04"),
            ("Xây dựng form đăng ký nghỉ nguyên ngày và nửa ngày (Sáng 08-12h / Chiều 13-17h)", "STORY", "DONE", "2026-07-30", "WFG-NOVA-04"),
            ("Xây dựng API nộp đơn, duyệt bước 1, duyệt bước 2 và từ chối kèm lý do bắt buộc", "TASK", "DONE", "2026-08-06", "WFG-NOVA-04"),
            ("Bàn giao kịch bản kiểm thử UAT nghỉ phép từ NV-U19 sang Lead BA NV-U07 trước ngày 14/08", "TASK", "DONE", "2026-08-12", "WFG-NOVA-04"),
            ("Tích hợp tự động loại trừ ngày lễ Quốc khánh (01-02/09) khỏi số ngày phép bị trừ", "TASK", "DONE", "2026-08-19", "WFG-NOVA-04"),
            ("Xây dựng cơ chế ủy quyền người duyệt thay có thời hạn khi Trưởng phòng đi công tác", "STORY", "DONE", "2026-08-25", "WFG-NOVA-04"),
            ("Kiểm tra xung đột đăng ký trùng ca nghỉ phép trên cùng một nhân viên", "TASK", "DONE", "2026-09-01", "WFG-NOVA-04"),
            ("Xây dựng màn hình tra cứu lịch sử biến động quỹ phép cá nhân", "TASK", "DONE", "2026-09-08", "WFG-NOVA-04"),
            ("Kiểm thử SIT luồng đồng bộ đơn phép đã duyệt sang bảng công ngày NOVA-ATD", "TASK", "DONE", "2026-09-15", "WFG-NOVA-05"),
            ("Kiểm tra chặn hủy đơn nghỉ phép thuộc kỳ chấm công đã khóa sổ (HTTP 409)", "TASK", "DONE", "2026-09-17", "WFG-NOVA-05"),
            ("Xử lý cảnh báo khi số người xin nghỉ cùng tổ sản xuất vượt ngưỡng an toàn vận hành", "STORY", "DONE", "2026-09-29", "WFG-NOVA-05"),
            ("Tối ưu truy vấn bảng tổng hợp tồn phép toàn công ty cho phòng Nhân sự", "TASK", "DONE", "2026-09-30", "WFG-NOVA-05"),
            ("Khắc phục lỗi UAT nghiêm trọng: hủy phép nửa ngày (0.5) bị hoàn thừa thành 1.0 ngày (Rework DB v2)", "BUG", "DONE", "2026-09-18", "WFG-NOVA-05"),
            ("Viết bộ kiểm thử 42 kịch bản biên cho phép nửa ngày, nghỉ lễ xen kẽ và hủy từng phần", "TASK", "DONE", "2026-09-29", "WFG-NOVA-05"),
            ("Đối chiếu số liệu sổ cái leave_balance_ledger với leave_entitlements trên 500 giao dịch giả lập", "TASK", "DONE", "2026-09-30", "WFG-NOVA-05"),
            ("Cập nhật thông báo email nội bộ hiển thị rõ số ngày hoàn trả chính xác đến 0.50 ngày", "TASK", "DONE", "2026-10-05", "WFG-NOVA-05"),
            ("Subtask bàn giao mưa bão mất điện Quận 7 (DIS-NOVA-STORM-01): vá hiển thị số dư 0.5 ngày trên cổng duyệt", "BUG", "DONE", "2026-09-24", "WFG-NOVA-05"),
            ("Nghiệm thu lại UAT (Re-test) lỗi hủy phép nửa ngày cùng C&B Minh Phát — Xác nhận PASS", "TASK", "DONE", "2026-10-01", "WFG-NOVA-05"),
            ("Rà soát cấu hình tỷ lệ tính phép theo tháng cho nhân sự mới vào làm giữa năm", "TASK", "IN_REVIEW", "2026-10-13", "WFG-NOVA-06"),
            ("Kiểm tra hiển thị lịch nghỉ chung của phòng ban trên trình duyệt di động", "TASK", "IN_PROGRESS", "2026-10-14", "WFG-NOVA-06"),
            ("Soát xét quyền tra cứu báo cáo tồn phép năm của Giám đốc nhà máy Bình Dương", "TASK", "IN_PROGRESS", "2026-10-15", "WFG-NOVA-06"),
            ("Chuẩn bị kịch bản khóa tạm thao tác tạo đơn phép trong 2 giờ cửa sổ cutover", "TASK", "TODO", "2026-10-15", "WFG-NOVA-06"),
            ("Hoãn sang Phase 2 theo CR-2026-08: Bộ máy tự động quy đổi & hết hạn 90 ngày quỹ nghỉ bù", "STORY", "CANCELLED", "2026-09-22", "WFG-NOVA-05"),
            ("Hủy luồng duyệt phép qua SMS hai chiều do khách hàng chọn dùng cổng web nội bộ", "TASK", "CANCELLED", "2026-07-24", "WFG-NOVA-04"),
            ("Xác minh tính toàn vẹn khóa dòng SELECT FOR UPDATE khi 20 yêu cầu duyệt chạy đồng thời", "TASK", "IN_REVIEW", "2026-10-14", "WFG-NOVA-06"),
            ("Soạn danh sách câu hỏi thường gặp (FAQ) về đăng ký nghỉ nửa ngày cho nhân viên", "TASK", "TODO", "2026-10-16", "WFG-NOVA-06"),
        ],
        "NOVA-DMG": [
            ("Thu thập và kiểm kê cấu trúc 14 file Excel nhân sự & theo dõi phép hiện hữu của Minh Phát", "STORY", "DONE", "2026-04-23", "WFG-NOVA-01"),
            ("Xây dựng quy tắc ánh xạ 18 tên viết tắt bộ phận nhà máy về danh mục phòng ban chuẩn", "TASK", "DONE", "2026-05-12", "WFG-NOVA-01"),
            ("Chốt tiêu chí nghiệm thu chuyển đổi dữ liệu: sai số quỹ phép toàn công ty bằng 0.00 ngày", "STORY", "DONE", "2026-06-03", "WFG-NOVA-02"),
            ("Thiết kế schema bảng tạm stg_hr_employees, stg_leave_balances và stg_quarantine_errors", "TASK", "DONE", "2026-07-13", "WFG-NOVA-03"),
            ("Viết công cụ kiểm tra định dạng mã nhân viên, ngày ký hợp đồng và phát hiện trùng lặp", "TASK", "DONE", "2026-07-24", "WFG-NOVA-04"),
            ("Xây dựng pipeline ETL nạp thử nghiệm danh sách nhân sự từ CSV chuẩn hóa", "STORY", "DONE", "2026-08-03", "WFG-NOVA-04"),
            ("Xây dựng báo cáo đối chiếu tự động tổng số ngày phép đã nghỉ và còn lại theo từng phòng ban", "TASK", "DONE", "2026-08-11", "WFG-NOVA-04"),
            ("Thực hiện Dry-Run chuyển đổi dữ liệu vòng 1 trên bản chụp dữ liệu tháng 07", "TASK", "DONE", "2026-08-20", "WFG-NOVA-04"),
            ("Xử lý 23 bản ghi sai định dạng ngày sinh DD/MM vs MM/DD phát hiện sau Dry-Run vòng 1", "BUG", "DONE", "2026-08-27", "WFG-NOVA-04"),
            ("Viết script nạp cây quản lý trực tiếp (Report-To) và kiểm tra không có nút mồ côi", "TASK", "DONE", "2026-09-04", "WFG-NOVA-04"),
            ("Chuẩn bị dữ liệu nền (seed test data giả lập) cho môi trường kiểm thử SIT & UAT", "TASK", "DONE", "2026-09-10", "WFG-NOVA-04"),
            ("Điều phối phiên kiểm thử liên thông SIT giữa 3 phân hệ HR - Attendance - Leave", "TASK", "DONE", "2026-09-15", "WFG-NOVA-05"),
            ("Tổ chức hướng dẫn nhóm người dùng đại diện Minh Phát thực hiện kiểm thử UAT đợt 1", "STORY", "DONE", "2026-09-18", "WFG-NOVA-05"),
            ("Thực hiện đánh giá tác động kỹ thuật & tiến độ cho yêu cầu thay đổi CR-2026-08", "TASK", "DONE", "2026-09-21", "WFG-NOVA-05"),
            ("Trình Hội đồng CCB phê duyệt biên bản tách phạm vi CR-2026-08 (DOC-NVDMG-CR-003)", "TASK", "DONE", "2026-09-23", "WFG-NOVA-05"),
            ("Thiết kế và diễn tập quy trình sao lưu & quay lui PostgreSQL trong 15 phút", "TASK", "DONE", "2026-10-05", "WFG-NOVA-05"),
            ("Thực hiện Dry-Run chuyển đổi dữ liệu vòng 2 với cấu trúc sổ cái phép NUMERIC(5,2) mới", "STORY", "DONE", "2026-10-06", "WFG-NOVA-05"),
            ("Subtask kiểm chứng tổng số dư phép nạp vào khớp 100% bảng tính đối chứng C&B", "TASK", "DONE", "2026-10-07", "WFG-NOVA-05"),
            ("Cập nhật ma trận truy vết yêu cầu (RTM) sau khi tách phạm vi CR-2026-08", "TASK", "DONE", "2026-09-25", "WFG-NOVA-05"),
            ("Đo kiểm thời gian chạy toàn bộ pipeline cutover đạt 18 phút (dưới ngưỡng 45 phút)", "TASK", "DONE", "2026-10-08", "WFG-NOVA-05"),
            ("Tổng hợp biên bản nghiệm thu có điều kiện cổng UAT Phase 5 (DOC-NVDMG-UAT-004)", "STORY", "DONE", "2026-10-08", "WFG-NOVA-05"),
            ("Xác minh cơ chế khóa ghi tạm thời trên hệ thống cũ trước thời điểm chốt số liệu", "TASK", "DONE", "2026-10-12", "WFG-NOVA-06"),
            ("Tối ưu truy vấn đối soát 90 ngày lịch sử quét vân tay chuyển tiếp", "TASK", "IN_PROGRESS", "2026-10-13", "WFG-NOVA-06"),
            ("Rà soát danh sách tài khoản quản trị hệ thống sẽ bàn giao cho Minh Phát", "TASK", "IN_REVIEW", "2026-10-14", "WFG-NOVA-06"),
            ("Chờ C&B Minh Phát ký xác nhận ngày bắt đầu/kết thúc của 7 hồ sơ nghỉ thai sản chuyển tiếp", "TASK", "BLOCKED", "2026-10-07", "WFG-NOVA-06"),
            ("Subtask diễn tập khôi phục bản sao lưu PostgreSQL trên môi trường staging (11 phút)", "TASK", "DONE", "2026-10-08", "WFG-NOVA-05"),
            ("Chuẩn bị biên bản chốt số dư đầu kỳ để hai bên ký xác nhận trong đêm cutover", "TASK", "IN_REVIEW", "2026-10-15", "WFG-NOVA-06"),
            ("Soạn thảo bản nháp Sổ tay bàn giao vận hành & đào tạo C&B (DOC-NVDMG-HND-006)", "STORY", "IN_PROGRESS", "2026-10-14", "WFG-NOVA-06"),
            ("Lập danh sách kiểm tra (Go/No-Go Checklist) cho buổi họp quyết định vận hành chính thức", "TASK", "IN_PROGRESS", "2026-10-15", "WFG-NOVA-06"),
            ("Hủy phương án nhập lịch sử chấm công giấy năm 2023 do khách hàng chỉ yêu cầu lưu trữ PDF", "TASK", "CANCELLED", "2026-06-10", "WFG-NOVA-02"),
            ("Thực hiện Dry-Run chuyển đổi dữ liệu vòng 3 sau khi nhận đủ 7 hồ sơ thai sản", "STORY", "TODO", "2026-10-16", "WFG-NOVA-06"),
            ("Tổ chức buổi đào tạo thực hành cho chuyên viên Nhân sự & C&B trước ngày Go-Live", "TASK", "TODO", "2026-10-16", "WFG-NOVA-06"),
        ],
    }[pid]

    blueprints: list[dict[str, Any]] = []
    for idx, (title, ttype, st, s_date, wfg_id) in enumerate(topics, start=1):
        bp: dict[str, Any] = {
            "title": title,
            "description": f"[{pid} / {wfg_id}] {title}. Thực hiện trong quy trình Waterfall không dùng Sprint (sprint_id=null), đảm bảo truy vết đầy đủ giữa yêu cầu, thiết kế, kiểm thử và nghiệm thu.",
            "type": ttype,
            "status": st,
            "priority": "HIGH" if (ttype == "BUG" or st == "BLOCKED" or idx in (1, 3, 19, 24, 25, 27)) else ("LOW" if st == "CANCELLED" else "MEDIUM"),
            "start_date": s_date,
            "duration_days": 5 if st == "DONE" else 2,
            "sprint_id": None,  # Strict Waterfall: sprint_id is always None
            "waterfall_phase_id": wfg_id,
            "labels": ["waterfall", pid.lower(), wfg_id.lower()],
        }

        # Wire specific real-world scenarios, subtasks, handovers, OT, and former BA authorship
        if pid == "NOVA-HR":
            if idx == 22:
                bp["parent_seq"] = 13
                bp["assignee_id"] = "NV-U08"
                bp["disruption_id"] = "DIS-NOVA-SICK-01"
                bp["handover_from_user_id"] = "NV-U09"
                bp["handover_date"] = "2026-09-07"
                bp["updated_date"] = "2026-09-09"
                bp["handover_reason"] = "NV-U09 nghỉ ốm sốt xuất huyết 07–09/09/2026; bàn giao sang NV-U08 để kịp cổng SIT."
                bp["task_note"] = {
                    "title": "Bàn giao khẩn khi NV-U09 nghỉ ốm (DIS-NOVA-SICK-01): UI cây quản lý trực tiếp",
                    "accomplishments": "Hoàng Đức Anh (NV-U08) tiếp nhận branch từ NV-U09 sáng 07/09 và hoàn tất binding API cây quản lý trực tiếp đúng hạn 09/09.",
                    "approach": "Giữ nguyên hợp đồng API DOC-NVHR-API-004 và bổ sung kiểm tra chặn chọn chính mình làm supervisor.",
                    "reason": "Tránh trễ mốc đóng code Phase 4 của dự án NOVA-HR khi thành viên phụ trách chính nghỉ ốm 3 ngày.",
                }
            elif idx == 23:
                bp["parent_seq"] = 10
                bp["assignee_id"] = "NV-U18"
            elif idx == 32:
                bp["assignee_id"] = "NV-U07"
                bp["transition_reason"] = "Đang chờ Ban giám đốc Minh Phát ban hành quyết định bổ nhiệm Trưởng kho mới để gán người duyệt trực tiếp."
            elif idx == 30:
                bp["transition_reason"] = "Hủy tích hợp máy chủ LDAP cũ do khách hàng xác nhận đã ngừng sử dụng từ quý 1/2026."

        elif pid == "NOVA-ATD":
            if idx == 20:
                bp["parent_seq"] = 14
                bp["assignee_id"] = "NV-U16"
            elif idx == 27:
                bp["assignee_id"] = "NV-U11"
                bp["updated_date"] = "2026-09-28"
                bp["is_overtime"] = True
                bp["task_note"] = {
                    "title": "Triển khai phần được duyệt của CR-2026-08: API xuất CSV đối soát tăng ca nghỉ bù",
                    "accomplishments": "Hoàn thành endpoint GET /api/v1/attendance/overtime-comp-export.csv theo đúng quyết định CCB tại DOC-NVDMG-CR-003.",
                    "approach": "Chỉ xuất các bản ghi OT đã duyệt kèm mã nhân viên và số phút hợp lệ; không can thiệp bảng quỹ phép năm.",
                    "reason": "Đáp ứng nhu cầu đối soát nghỉ bù trước mắt của C&B Minh Phát mà không làm vỡ kiến trúc Phase 1.",
                }
            elif idx == 28:
                bp["parent_seq"] = 27
                bp["assignee_id"] = "NV-U16"
                bp["updated_date"] = "2026-09-29"
            elif idx == 30:
                bp["transition_reason"] = "Bị từ chối tại DOC-NVATD-DES-006 do thu thập GPS nền trên điện thoại cá nhân vi phạm quyền riêng tư."
            elif idx == 31:
                bp["assignee_id"] = "NV-U18"
                bp["transition_reason"] = "Chờ bộ phận IT Minh Phát mở rule firewall cổng 8443 từ VLAN xưởng số 3 về máy chủ đồng bộ."

        elif pid == "NOVA-LEV":
            if idx == 3:
                bp["created_by"] = "NV-U19"
                bp["assignee_id"] = "NV-U19"
                bp["updated_date"] = "2026-06-11"
            elif idx == 10:
                bp["created_by"] = "NV-U02"
                bp["assignee_id"] = "NV-U07"
                bp["handover_from_user_id"] = "NV-U19"
                bp["handover_date"] = "2026-08-13"
                bp["updated_date"] = "2026-08-14"
                bp["disruption_id"] = "DIS-NOVA-OFFBOARD-01"
                bp["handover_reason"] = "Bàn giao toàn bộ tài liệu đặc tả & bộ kịch bản UAT trước khi BA NV-U19 nghỉ việc ngày 2026-08-14."
            elif idx == 19:
                bp["assignee_id"] = "NV-U12"
                bp["rework"] = True
                bp["is_overtime"] = True
                bp["updated_date"] = "2026-09-23"
                bp["rework_reason"] = "Cần bổ sung khóa dòng SELECT FOR UPDATE và bảng sổ cái leave_balance_ledger theo review DOC-NVLEV-DB-002."
                bp["task_note"] = {
                    "title": "Xử lý gốc lỗi UAT hoàn thừa phép nửa ngày (0.5 -> 1.0 ngày)",
                    "accomplishments": "Chuyển đổi hoàn toàn logic hoàn phép từ đếm dòng sang cộng đại số SUM(day_fraction) NUMERIC(5,2) trên bảng leave_balance_ledger.",
                    "approach": "Quay lui bước Thiết kế CSDL (lưu trữ DOC-NVLEV-DB-001-LEGACY, ban hành DOC-NVLEV-DB-002 v2) và chạy migration bù dữ liệu UAT.",
                    "reason": "Khắc phục triệt để lỗi nghiệp vụ nghiêm trọng phát hiện trong UAT Phase 5 trước khi nghiệm thu.",
                }
            elif idx == 23:
                bp["parent_seq"] = 19
                bp["assignee_id"] = "NV-U12"
                bp["disruption_id"] = "DIS-NOVA-STORM-01"
                bp["handover_from_user_id"] = "NV-U13"
                bp["handover_date"] = "2026-09-24"
                bp["updated_date"] = "2026-09-25"
                bp["handover_reason"] = "NV-U13 mất điện và mạng diện rộng do bão tại Quận 7 ngày 24-25/09; NV-U12 tiếp nhận vá giao diện hiển thị 0.5 ngày."
                bp["task_note"] = {
                    "title": "Bàn giao khẩn do mưa bão mất điện Quận 7 (DIS-NOVA-STORM-01) cho NVLEV-23",
                    "accomplishments": "Lý Thành Đạt (NV-U12) cập nhật định dạng hiển thị số thập phân 0.50 ngày trên cổng duyệt phép thay cho NV-U13 đang mất kết nối.",
                    "approach": "Đồng bộ kiểu dữ liệu từ API DOC-NVLEV-API-003 và kiểm tra trực tiếp cùng QA NV-U15.",
                    "reason": "Đảm bảo phiên kiểm thử lại (UAT Re-test) với khách hàng Minh Phát không bị đình trệ vì sự cố thời tiết.",
                }
            elif idx == 24:
                bp["assignee_id"] = "NV-U17"
                bp["is_overtime"] = True
                bp["updated_date"] = "2026-10-01"
            elif idx == 29:
                bp["transition_reason"] = "Theo quyết định CCB tại DOC-NVDMG-CR-003, hoãn bộ máy tự động quy đổi quỹ nghỉ bù sang Hợp đồng Phase 2 để bảo vệ mốc Go-Live 30/10."
            elif idx == 30:
                bp["transition_reason"] = "Khách hàng thống nhất chỉ phê duyệt qua cổng Web có xác thực SSO nội bộ, không dùng SMS hai chiều."

        elif pid == "NOVA-DMG":
            if idx == 18:
                bp["parent_seq"] = 17
                bp["assignee_id"] = "NV-U14"
            elif idx == 25:
                bp["assignee_id"] = "NV-U14"
                bp["updated_date"] = "2026-10-12"
                bp["transition_reason"] = "Đang bị chặn (BLOCKED) do chờ bộ phận C&B Minh Phát ký xác nhận ngày nghỉ thực tế của 7 hồ sơ thai sản chuyển tiếp."
                bp["task_note"] = {
                    "title": "Điểm chặn NVDMG-25 trước Dry-Run vòng 3: chờ xác nhận 7 hồ sơ nghỉ thai sản",
                    "accomplishments": "Đã tách riêng 7 bản ghi thiếu ngày kết thúc chế độ thai sản vào bảng cách ly stg_quarantine_errors.",
                    "approach": "Không tự suy đoán ngày đi làm lại để giữ nguyên tắc sai số quỹ phép bằng 0.00 ngày.",
                    "reason": "Bảo đảm tính chính xác pháp lý của hồ sơ nhân sự trước giờ cắt chuyển chính thức.",
                }
            elif idx == 26:
                bp["parent_seq"] = 16
                bp["assignee_id"] = "NV-U18"
                bp["is_overtime"] = True
            elif idx == 30:
                bp["transition_reason"] = "Khách hàng chốt lưu trữ bản chụp bảng công giấy năm 2023 dưới dạng hồ sơ lưu trữ nội bộ, không nạp vào CSDL tác nghiệp."

        blueprints.append(bp)

    return blueprints


def main() -> None:
    sim_start = date.fromisoformat(SIM_START)
    as_of = date.fromisoformat(AS_OF_DATE)
    working_days = build_working_days(sim_start, as_of)

    orgs, users, org_mems, role_assigns, projects, proj_mems = build_org_identity_graph(
        namespace=NAMESPACE,
        primary_org_id=PRIMARY_ORG_ID,
        org_specs=ORG_SPECS,
        user_specs=USER_SPECS,
        org_admin_ids=ORG_ADMIN_IDS,
        project_specs=PROJECT_SPECS,
    )

    unavailable_by_user: dict[str, list[tuple[str, str]]] = {}
    for dis in DISRUPTION_EVENTS:
        unavailable_by_user.setdefault(dis["affected_user_id"], []).append(
            (dis["unavailable_from"], dis["unavailable_to"])
        )
    user_left_at = {u["user_id"]: u["left_at"] for u in users if u.get("left_at")}

    all_tasks, all_comments, all_worklogs, all_events, all_notes = [], [], [], [], []
    regular_members_by_proj: dict[str, list[str]] = {}
    tasks_by_proj: dict[str, list[str]] = {}

    for p_spec, proj in zip(PROJECT_SPECS, projects):
        pid = proj["project_id"]
        reg_members = [m for m in p_spec["member_ids"] if m not in ORG_ADMIN_IDS and m != proj["leader_id"]]
        regular_members_by_proj[pid] = reg_members
        bps = _make_waterfall_project_blueprints(pid, reg_members)
        t_rows, c_rows, w_rows, e_rows, n_rows = expand_project_tasks(
            namespace=NAMESPACE,
            org_id=PRIMARY_ORG_ID,
            project=proj,
            leader_id=proj["leader_id"],
            member_ids=reg_members,
            sim_start=sim_start,
            as_of=as_of,
            task_blueprints=bps,
            unavailable_by_user=unavailable_by_user,
            user_left_at=user_left_at,
        )
        all_tasks.extend(t_rows)
        all_comments.extend(c_rows)
        all_worklogs.extend(w_rows)
        all_events.extend(e_rows)
        all_notes.extend(n_rows)
        tasks_by_proj[pid] = [r["task_id"] for r in t_rows]

    task_id_by_key = {t["key"]: t["task_id"] for t in all_tasks}
    note_id_by_key = {n["task_key"]: n["note_id"] for n in all_notes}

    doc_specs = build_nova_doc_specs(task_id_by_key)
    project_docs, doc_versions = render_project_documents_and_versions(
        pkg_root=PKG_ROOT,
        namespace=NAMESPACE,
        org_id=PRIMARY_ORG_ID,
        org_banner="NOVA SOLUTIONS  •  WATERFALL HRMS DELIVERY",
        doc_specs=doc_specs,
    )
    docs_by_proj: dict[str, list[str]] = {}
    for d in project_docs:
        docs_by_proj.setdefault(d["project_id"], []).append(d["document_id"])

    report_settings, work_reports = build_work_reports_for_org(
        namespace=NAMESPACE,
        org_id=PRIMARY_ORG_ID,
        projects=projects,
        org_admin_list=sorted(ORG_ADMIN_IDS),
        regular_members_by_project=regular_members_by_proj,
        docs_by_project=docs_by_proj,
        tasks_by_project=tasks_by_proj,
        report_narratives=REPORT_NARRATIVES,
    )

    eval_cases = build_nova_eval_cases(make_eval_case, AS_OF_DATE, task_id_by_key, note_id_by_key)

    bundle = {
        "as_of_date": AS_OF_DATE,
        "primary_org_id": PRIMARY_ORG_ID,
        "simulation_window": {
            "start": SIM_START,
            "end": AS_OF_DATE,
            "working_days": len(working_days),
            "vn_holidays_observed": [d.isoformat() for d in sorted(VN_HOLIDAYS_2026) if sim_start <= d <= as_of],
            "timezone": "Asia/Ho_Chi_Minh (+07:00)",
            "regular_hours": "08:00-12:00, 13:00-17:00",
            "overtime_hours": "17:00-22:00",
        },
        "organizations": orgs,
        "users": users,
        "organization_memberships": org_mems,
        "role_assignments": role_assigns,
        "projects": projects,
        "project_memberships": proj_mems,
        "sprints": [],  # Pure Waterfall: zero sprints
        "tasks": all_tasks,
        "task_comments": all_comments,
        "task_worklogs": all_worklogs,
        "task_events": all_events,
        "task_notes": all_notes,
        "project_documents": project_docs,
        "document_versions": doc_versions,
        "work_report_settings": report_settings,
        "work_reports": work_reports,
        "disruption_events": DISRUPTION_EVENTS,
        "oncall_schedules": [],
        "evaluation_cases": eval_cases,
    }

    neg_fixtures = build_standard_negative_fixtures(NAMESPACE, bundle)

    readme_md = f"""# Organization 2 — Nova Solutions: Phần Mềm Quản Lý Nhân Sự, Chấm Công & Nghỉ Phép (Waterfall)

**Trạng thái:** Hoàn thành bộ dataset synthetic kiểm chứng được (`v1.0.0`, `as_of_date = {AS_OF_DATE}`); tái tạo 100% bằng `python -X utf8 -B Dataset/Organization2-Nova-Solutions/tools/generate_org.py`. Chưa seed MongoDB runtime của Continuum.

## 1. Bối cảnh nghiệp vụ & Phương pháp quản lý Waterfall
- **Tổ chức chính (`ORG-NOVA`)**: Công ty gia công phần mềm giả lập **Nova Solutions** triển khai hệ thống quản lý Hồ sơ nhân sự, Ca chấm công và Nghỉ phép cho doanh nghiệp khách hàng khoảng 300 nhân viên (**Minh Phát Corp — `ORG-MINHPHAT`**, 312 nhân sự tại Văn phòng Quận 7 & Nhà máy Bình Dương).
- **Phương pháp chủ đạo**: **Waterfall thuần túy** (`methodology = "WATERFALL"`, `sprints = []`, `sprint_id = null` trên toàn bộ {len(all_tasks)} task), quản trị theo 6 cổng giai đoạn (`structured/waterfall_phase_gates.jsonl`): Khảo sát → FRS Baseline → Thiết kế Kiến trúc/DB/API → Phát triển → SIT/UAT → Chuyển đổi & Bàn giao.
- **Tình huống thực tế nổi bật**:
  1. **Quay lui giai đoạn Waterfall do lỗi UAT nửa ngày (`NVLEV-19`)**: Phát hiện hủy phép nửa ngày (`0.5`) hoàn thừa thành `1.0` ngày; lưu trữ thiết kế cũ `DOC-NVLEV-DB-001-LEGACY` (`ARCHIVED`), ban hành sổ cái `DOC-NVLEV-DB-002` v2 (`APPROVED`) và kiểm thử lại (`NVLEV-24`).
  2. **Kiểm soát thay đổi khách hàng `CR-2026-08` (`DOC-NVDMG-CR-003`)**: Duyệt làm báo cáo xuất CSV đối soát tăng ca (`NVATD-27`) trong Phase 1, đồng thời hoãn bộ máy tự động quỹ nghỉ bù sang Phase 2 (`NVLEV-29` chuyển `CANCELLED`).
  3. **Biến động nhân sự & đời sống**: BA `NV-U19` nghỉ việc ngày `2026-08-14` (thu hồi quyền, bàn giao cho `NV-U07`), kỹ sư `NV-U09` nghỉ ốm (`07–09/09/2026`), kỹ sư `NV-U13` mất điện/mạng do mưa bão tại Quận 7 (`24–25/09/2026`), điểm chặn `NVDMG-25` chờ xác nhận 7 hồ sơ thai sản.

## 2. Nguồn tham chiếu GitHub & Giới hạn bản quyền
- Tham khảo khái niệm nghiệp vụ từ `orangehrm/orangehrm` (tag `v5.9`, commit `56e23b3b09e7af29317a0943523b825843fff527`, giấy phép `GPL-3.0-or-later`, truy cập `2026-10-28T08:17:08+07:00`, kèm public issues `#1964`, `#1965`, `#1966`).
- **Không sao chép** bất kỳ mã nguồn, schema, tài liệu hay tài sản GPL nào của OrangeHRM; không gán sự kiện giả cho contributor thật; không khẳng định OrangeHRM phát triển theo Waterfall. Chi tiết xem tại [../GITHUB_SOURCES_AND_LICENSES.md](../GITHUB_SOURCES_AND_LICENSES.md).

## 3. Phạm vi Continuum đã chốt & Quy mô gói dữ liệu
- **Không có Team / Không có lịch sử AI Chat / Không có entity Notebook thứ tư**.
- **Đủ 3 dạng Group Note bắt buộc**: `{len(all_notes)}` `TASK_NOTE` (`knowledge_eligible=false`), `{len(project_docs)}` `PROJECT_DOCUMENT` (`{len(doc_versions)}` versions, kèm DOCX renditions), `{len(work_reports)}` `WORK_REPORT` (`DAILY` & `WEEKLY`, luồng `MEMBER→Leader` & `LEADER→Org ADMIN Manager`).
- **Evaluation**: `{len(eval_cases)}` benchmark cases trong `evaluation/benchmark_cases.jsonl`, toàn bộ gắn nhãn `review_status = "unreviewed"` (`"chưa duyệt"`), tách biệt khỏi kho tri thức ứng dụng.
- Đối chiếu chi tiết tại [INGESTION_CONTRACT.md](INGESTION_CONTRACT.md), [../CONTINUUM-DATASET-MAPPING.md](../CONTINUUM-DATASET-MAPPING.md) và [../CONTINUUM_DATA_DICTIONARY.md](../CONTINUUM_DATA_DICTIONARY.md).
"""

    ic_md = f"""# Ingestion Contract — Organization 2: Nova Solutions (Waterfall v1.0.0)

1. **Tenant & IAM Scope**: Chỉ nạp `ORG-NOVA` làm tenant chính trên Continuum; các bản ghi `ORG-MINHPHAT` là đối tác khách hàng dùng cho kiểm thử cách ly đa tenant (`DENY`) và truy vết biên bản UAT/CR.
2. **Waterfall Constraint**: `structured/sprints.jsonl` rỗng (`[]`) và toàn bộ `{len(all_tasks)}` task trong `structured/tasks.jsonl` có `sprint_id = null`. Tiến độ cổng giai đoạn lưu tại `structured/waterfall_phase_gates.jsonl` và yêu cầu thay đổi lưu tại `structured/change_requests.jsonl` (`DATASET_METADATA_ONLY` cho tới khi Continuum mở bảng milestone/gate riêng).
3. **Ba dạng Group Note**:
   - `structured/task_notes.jsonl`: `noteType = TASK_NOTE`, `status = CONFIRMED`, `knowledge_eligible = false` (cấm đưa vào index tri thức chính thức).
   - `structured/project_documents.jsonl` + `structured/document_versions.jsonl`: Chỉ nạp phiên bản `latest_approved_version_number` của tài liệu không bị `ARCHIVED` / `REJECTED` / `DRAFT` khi có runtime consumer.
   - `structured/work_reports.jsonl`: Báo cáo `MEMBER` do `TEAM_LEADER` hoặc `ADMIN` duyệt; báo cáo `LEADER` bắt buộc do Organization `ADMIN` (`NV-U01`, `NV-U02`) duyệt. Chỉ bản `APPROVED` mới có `knowledge_eligible = true`.
4. **Lịch làm việc & Bàn giao**: Chuẩn `+07:00`, hành chính `08:00–12:00` & `13:00–17:00` (không có hoạt động người dùng `12:00–13:00`), OT tối `17:00–22:00`, tuân thủ ngày lễ Việt Nam và các cửa sổ vắng mặt trong `structured/disruption_events.jsonl`.
5. **Tách biệt Evaluation & Fixtures**: Không nạp `evaluation/benchmark_cases.jsonl` (`review_status = "unreviewed"`) và `fixtures/negative_cases.json` vào cơ sở dữ liệu sản phẩm.
"""

    manifest = materialize_organization_package(
        pkg_root=PKG_ROOT,
        namespace=NAMESPACE,
        dataset_id="continuum-org2-nova-waterfall-v1",
        version="1.0.0",
        org_display_name="Nova Solutions (HR, Attendance & Leave)",
        methodology_label="WATERFALL",
        bundle=bundle,
        extra_structured_files={
            "structured/waterfall_phase_gates.jsonl": WATERFALL_PHASE_GATES,
            "structured/change_requests.jsonl": CHANGE_REQUEST_RECORDS,
        },
        negative_fixtures=neg_fixtures,
        source_attribution=SOURCE_ATTRIBUTION,
        assumptions=IMPLEMENTATION_ASSUMPTIONS,
        readme_markdown=readme_md,
        ingestion_contract_markdown=ic_md,
    )
    print(
        f"[ORG-2 NOVA] Generated successfully: {manifest['canonical_counts']['physical_files_total']} files, "
        f"{len(all_tasks)} tasks, {len(all_notes)} task notes, {len(project_docs)} docs, "
        f"{len(work_reports)} reports, {len(eval_cases)} eval cases."
    )


if __name__ == "__main__":
    main()
