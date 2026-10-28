"""Deterministic generator for Organization 4 — MediFlow (Hybrid Milestone + Sprint Outpatient Scheduling & Admin Registration)."""

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

from continuum_synth import VN_HOLIDAYS_2026, build_working_days, synth_oid  # noqa: E402
from mediflow_docs import REPORT_NARRATIVES, build_mediflow_doc_specs  # noqa: E402
from mediflow_eval import build_mediflow_eval_cases  # noqa: E402
from mediflow_specs import (  # noqa: E402
    AS_OF_DATE,
    CLINIC_FEEDBACK_LOG,
    DISRUPTION_EVENTS,
    IMPLEMENTATION_ASSUMPTIONS,
    MILESTONE_RECORDS,
    NAMESPACE,
    ONCALL_SCHEDULES,
    ORG_ADMIN_IDS,
    ORG_SPECS,
    PRIMARY_ORG_ID,
    PROJECT_SPECS,
    SIM_START,
    SOURCE_ATTRIBUTION,
    SPRINT_WINDOWS,
    SYSTEM_BOTS,
    USER_SPECS,
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


def _build_hybrid_sprints(projects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Create 5 sprints (S1..S4 COMPLETED, S5 ACTIVE) only for HYBRID projects; MED-PIL (WATERFALL) has 0 sprints."""
    sprints: list[dict[str, Any]] = []
    for proj in projects:
        if proj["methodology"] != "HYBRID":
            continue
        pid = proj["project_id"]
        pcode = proj["code"]
        for s_tag, s_name, s_status, s_start, s_end, ms_id in SPRINT_WINDOWS:
            sp_id = f"{pcode}-{s_tag}"
            sprints.append({
                "sprint_id": sp_id,
                "continuum_sprint_id": synth_oid(NAMESPACE, "sprint", sp_id),
                "organization_id": PRIMARY_ORG_ID,
                "project_id": pid,
                "name": f"[{pcode}] {s_name}",
                "status": s_status,
                "start_date": s_start,
                "end_date": s_end,
                "milestone_id": ms_id,
                "goal": f"Hoàn thành mục tiêu {s_tag} của {pid} gắn với cổng {ms_id} trong phạm vi hành chính phi lâm sàng.",
                "synthetic": True,
            })
    return sprints


def _make_mediflow_blueprints(pid: str, pcode: str, methodology: str) -> list[dict[str, Any]]:
    """Build 32 tasks per project: Milestone + Sprint for HYBRID projects, pure Milestone (sprint_id=None) for MED-PIL."""
    topics = {
        "MED-REG": [
            ("Xác lập ranh giới dữ liệu đăng ký hành chính phi lâm sàng tại Milestone M1", "STORY", "DONE", "2026-05-06", "MS-MED-01", None),
            ("Thiết kế cơ chế băm định danh có muối (Salted HMAC Lookup) cho số liên lạc", "TASK", "DONE", "2026-06-02", "MS-MED-01", None),
            ("Chuẩn hóa quy tắc cấp mã hành chính bất biến AK-PAT-XXXXXX không trùng lặp", "TASK", "DONE", "2026-06-09", "MS-MED-01", None),
            ("Chốt whitelist các trường hành chính hợp lệ và chặn trường tự do ngoài phạm vi", "STORY", "DONE", "2026-06-11", "MS-MED-01", None),
            ("Thiết kế bảng admin_profiles, profile_identifiers và merge_audits", "TASK", "DONE", "2026-08-10", "MS-MED-02", "S1"),
            ("Xây dựng dịch vụ mã hóa AES-256-GCM cho thông tin liên hệ dự phòng", "TASK", "DONE", "2026-08-11", "MS-MED-02", "S1"),
            ("Phát triển bộ lọc che mặt nạ số liên lạc mặc định (chỉ hiện 3 số cuối ***-***-482)", "STORY", "DONE", "2026-08-13", "MS-MED-02", "S1"),
            ("Cài đặt chỉ mục tra cứu HMAC tốc độ cao dưới 20ms tại quầy lễ tân", "TASK", "DONE", "2026-08-14", "MS-MED-02", "S1"),
            ("Xây dựng API POST /api/v1/admin-profiles kèm strict schema validation (HTTP 400)", "STORY", "DONE", "2026-08-24", "MS-MED-02", "S2"),
            ("Xây dựng API POST /api/v1/admin-profiles:dedup-check cảnh báo hồ sơ tương đồng", "TASK", "DONE", "2026-08-25", "MS-MED-02", "S2"),
            ("Cài đặt giao dịch gộp 2 mã hành chính trùng và chuyển nguyên tử lịch hẹn tương lai", "STORY", "DONE", "2026-08-26", "MS-MED-02", "S2"),
            ("Xây dựng biểu mẫu đăng ký Walk-In rút gọn 4 trường bắt buộc thao tác phím tắt", "STORY", "DONE", "2026-08-27", "MS-MED-02", "S2"),
            ("Ghi vết kiểm toán bắt buộc mỗi khi lễ tân bấm mở xem đầy đủ số liên lạc", "TASK", "DONE", "2026-09-07", "MS-MED-03", "S3"),
            ("Sửa lỗi phân biệt dấu tiếng Việt khi chuẩn hóa họ tên kiểm tra trùng hồ sơ", "BUG", "DONE", "2026-09-09", "MS-MED-03", "S3"),
            ("Xây dựng cơ chế bật/tắt nhóm trường liên hệ khẩn cấp theo cấu hình quầy", "TASK", "DONE", "2026-09-11", "MS-MED-03", "S3"),
            ("Subtask kiểm thử chuyển hướng mã phụ sang primary_profile_id trên đường dẫn nhắc hẹn", "TASK", "DONE", "2026-09-14", "MS-MED-03", "S3"),
            ("Tối ưu bộ nhớ đệm danh mục tỉnh/thành hành chính trên trình duyệt quầy tiếp đón", "TASK", "DONE", "2026-09-21", "MS-MED-03", "S4"),
            ("Kiểm tra từ chối 100% tệp đính kèm ngoài phạm vi hành chính trên cổng API", "TASK", "DONE", "2026-09-22", "MS-MED-03", "S4"),
            ("Tinh chỉnh thông báo gợi ý gộp hồ sơ trực quan sau góp ý lễ tân An Khang", "STORY", "DONE", "2026-09-24", "MS-MED-03", "S4"),
            ("Chạy bộ kiểm thử tự động 32 ca che mặt nạ dữ liệu và chặn trường lạ (DOC-MEDREG-TST-006)", "TASK", "DONE", "2026-09-25", "MS-MED-03", "S4"),
            ("Kiểm tra không rò rỉ số liên lạc đầy đủ trong toàn bộ log truy vết ứng dụng", "TASK", "DONE", "2026-09-28", "MS-MED-03", "S4"),
            ("Xác minh tốc độ thao tác tạo hồ sơ Walk-In đạt trung bình 16 giây/lượt", "TASK", "DONE", "2026-09-29", "MS-MED-03", "S4"),
            ("Cập nhật tài liệu hướng dẫn quy trình gộp hồ sơ trùng cho Lễ tân trưởng", "TASK", "DONE", "2026-09-30", "MS-MED-03", "S4"),
            ("Đóng kiểm tra điều kiện sẵn sàng phân hệ đăng ký cho cổng Pilot M3", "TASK", "DONE", "2026-10-01", "MS-MED-03", "S4"),
            ("Rà soát bảng thống kê tỷ lệ phát hiện trùng hồ sơ tuần đầu vận hành Pilot", "STORY", "IN_REVIEW", "2026-10-08", "MS-MED-04", "S5"),
            ("Bổ sung phím tắt Alt+N mở nhanh khung tạo hồ sơ khách vãng lai giờ cao điểm", "TASK", "IN_PROGRESS", "2026-10-12", "MS-MED-04", "S5"),
            ("Cập nhật chú giải hướng dẫn nhập năm sinh cho người lớn tuổi chỉ nhớ âm lịch", "TASK", "IN_PROGRESS", "2026-10-13", "MS-MED-04", "S5"),
            ("Soát xét nhật ký mở xem số liên lạc trong 3 ngày đầu thử nghiệm thực địa", "TASK", "IN_REVIEW", "2026-10-14", "MS-MED-04", "S5"),
            ("Chuẩn bị gói cấu hình khóa thay đổi danh mục trường trước kỳ nghiệm thu M4", "TASK", "TODO", "2026-10-15", "MS-MED-04", "S5"),
            ("Hủy thử nghiệm quét ảnh thẻ căn cước qua webcam quầy do vượt phạm vi Pilot M1", "STORY", "CANCELLED", "2026-08-18", "MS-MED-02", "S1"),
            ("Chờ điều phối viên mạng An Khang xác nhận thông số máy in tem mã tại quầy số 2", "TASK", "BLOCKED", "2026-10-12", "MS-MED-04", "S5"),
            ("Tổng hợp phụ lục nghiệm thu phân hệ đăng ký hành chính cho cổng M4", "TASK", "TODO", "2026-10-16", "MS-MED-04", "S5"),
        ],
        "MED-APT": [
            ("Xác định vòng đời 6 trạng thái lịch hẹn hành chính chuẩn cho Milestone M1", "STORY", "DONE", "2026-05-08", "MS-MED-01", None),
            ("Phân tích quy tắc phân ca bác sĩ sáng/chiều và khung slot 15 phút", "TASK", "DONE", "2026-06-03", "MS-MED-01", None),
            ("Thiết kế cơ chế khóa Idempotency-Key chống bấm đúp đặt lịch hẹn", "TASK", "DONE", "2026-06-10", "MS-MED-01", None),
            ("Thiết kế bảng lịch hẹn sơ bộ v1.0 (sau này đã lưu trữ thay bằng DOC-MEDAPT-DB-002)", "TASK", "DONE", "2026-06-22", "MS-MED-02", None),
            ("Xây dựng dịch vụ khởi tạo lịch ca bác sĩ theo tuần và cấu hình sức chứa slot", "STORY", "DONE", "2026-08-10", "MS-MED-02", "S1"),
            ("Thiết lập bảng Transactional Outbox đẩy sự kiện nhắc giờ hẹn sang VietNotify", "TASK", "DONE", "2026-08-12", "MS-MED-02", "S1"),
            ("Xây dựng bộ lọc tìm khung giờ trống theo chuyên khoa hành chính và khung buổi", "TASK", "DONE", "2026-08-14", "MS-MED-02", "S1"),
            ("Xây dựng API POST /api/v1/appointments đặt lịch đơn lẻ cho buổi Demo M2", "STORY", "DONE", "2026-08-24", "MS-MED-02", "S2"),
            ("Xây dựng luồng hủy lịch chủ động trước giờ hẹn và giải phóng chỗ trống", "TASK", "DONE", "2026-08-25", "MS-MED-02", "S2"),
            ("Tích hợp hiển thị trạng thái Scheduled / WalkIn / Teleconsult_Admin_Slot", "TASK", "DONE", "2026-08-26", "MS-MED-02", "S2"),
            ("Sửa lỗi lệch hiển thị slot cuối buổi chiều 16:45 trên trình duyệt máy trạm lễ tân", "BUG", "DONE", "2026-08-27", "MS-MED-02", "S2"),
            ("Xây dựng giao diện lưới lịch bác sĩ tuần v1 phục vụ trình diễn Demo M2", "STORY", "DONE", "2026-08-28", "MS-MED-02", "S2"),
            ("Đánh giá kỹ thuật phản hồi Demo M2 (CFB-2026-01) về quyền Lễ tân dời lịch hộ", "TASK", "DONE", "2026-09-03", "MS-MED-03", None),
            ("Nâng cấp CSDL lịch hẹn v2: khóa SELECT FOR UPDATE ORDER BY slot_id ASC (DOC-MEDAPT-DB-002)", "BUG", "DONE", "2026-09-07", "MS-MED-03", "S3"),
            ("Subtask bàn giao nghỉ ốm (DIS-MED-SICK-01): kiểm thử tương tranh 50 luồng đặt chung 1 slot", "TASK", "DONE", "2026-09-10", "MS-MED-03", "S3"),
            ("Xây dựng bảng kiểm toán bất biến reschedule_audits lưu lý do dời lịch", "TASK", "DONE", "2026-09-11", "MS-MED-03", "S3"),
            ("Cập nhật giao diện hộp thoại dời lịch bắt buộc nhập reschedule_reason >= 10 ký tự", "STORY", "DONE", "2026-09-14", "MS-MED-03", "S3"),
            ("Phát triển API POST /api/v1/appointments:bulk-reschedule theo CFB-2026-01 (tối đa 30 lịch)", "STORY", "DONE", "2026-09-21", "MS-MED-03", "S4"),
            ("Subtask nối sự kiện dời lịch hàng loạt vào hàng đợi thông báo giờ mới VietNotify", "TASK", "DONE", "2026-09-23", "MS-MED-03", "S4"),
            ("Kiểm tra tối thiểu hóa dữ liệu tin nhắn nhắc hẹn (chỉ gửi mã hẹn, giờ và số quầy)", "TASK", "DONE", "2026-09-24", "MS-MED-03", "S4"),
            ("Cài đặt quay lui nguyên tử toàn bộ batch nếu 1 slot đích báo đầy (HTTP 409)", "TASK", "DONE", "2026-09-25", "MS-MED-03", "S4"),
            ("Chặn thao tác dời lịch đối với các cuộc hẹn đã ở trạng thái Completed hoặc Cancelled", "TASK", "DONE", "2026-09-28", "MS-MED-03", "S4"),
            ("Tối ưu tốc độ tải lịch tuần của 6 phòng tư vấn xuống dưới 120ms", "TASK", "DONE", "2026-09-29", "MS-MED-03", "S4"),
            ("Kiểm tra đồng bộ lịch tạm nghỉ đột xuất của bác sĩ với danh sách cần dời lịch", "TASK", "DONE", "2026-09-30", "MS-MED-03", "S4"),
            ("[SPILLOVER S4->S5 DO BÃO] Hoàn tất bộ kiểm thử tự động dời lịch hàng loạt 30 cuộc hẹn", "TASK", "IN_REVIEW", "2026-09-25", "MS-MED-04", "S5"),
            ("Tinh chỉnh bộ lọc khung giờ trống liền kề khi Lễ tân trưởng tìm ca thay thế", "TASK", "IN_PROGRESS", "2026-10-12", "MS-MED-04", "S5"),
            ("Phân tích rủi ro bản nháp phản hồi CFB-2026-03 khóa đặt lịch 30 ngày (chưa phê duyệt)", "STORY", "IN_REVIEW", "2026-10-14", "MS-MED-04", "S5"),
            ("Theo dõi độ trễ đẩy sự kiện nhắc lịch trong tuần đầu vận hành thử nghiệm Pilot", "TASK", "IN_PROGRESS", "2026-10-14", "MS-MED-04", "S5"),
            ("Soạn hướng dẫn xử lý tình huống slot thay thế trong ngày đã kín chỗ cho lễ tân", "TASK", "TODO", "2026-10-15", "MS-MED-04", "S5"),
            ("Hủy luồng tự động chọn đại ca bác sĩ khác chuyên khoa khi dời lịch hàng loạt", "TASK", "CANCELLED", "2026-09-15", "MS-MED-03", "S3"),
            ("Chờ Ban điều hành phòng khám An Khang chốt lịch bảo trì phòng số 4 cuối tháng 10", "TASK", "BLOCKED", "2026-10-12", "MS-MED-04", "S5"),
            ("Đóng gói báo cáo độ ổn định khóa tương tranh slot phục vụ nghiệm thu M4", "TASK", "TODO", "2026-10-16", "MS-MED-04", "S5"),
        ],
        "MED-ADM": [
            ("Xác lập luồng ưu tiên tiếp đón Scheduled vs WalkIn và chính sách ẩn SĐT xuất file", "STORY", "DONE", "2026-05-12", "MS-MED-01", None),
            ("Thiết kế ma trận phân quyền RECEPTIONIST, RECEPTION_SHIFT_LEAD và VIEWER", "TASK", "DONE", "2026-06-04", "MS-MED-01", None),
            ("Thiết kế quy tắc hiển thị ẩn danh mã vé Q-XXX trên màn hình tivi sảnh chờ", "STORY", "DONE", "2026-06-11", "MS-MED-01", None),
            ("Chuẩn hóa quy tắc đối soát tự động trạng thái Missed sau 45 phút cuối ca", "TASK", "DONE", "2026-06-29", "MS-MED-02", None),
            ("Thiết kế bảng reception_queue_tickets phân vùng theo ngày làm việc", "TASK", "DONE", "2026-08-10", "MS-MED-02", "S1"),
            ("Xây dựng khung giao diện bảng gọi số quầy tiếp đón v1 (do MED-U18 làm trước khi nghỉ)", "STORY", "DONE", "2026-08-11", "MS-MED-02", "S1"),
            ("Cài đặt cờ hệ thống cứng include_phone_in_excel_export = false cho mọi báo cáo", "TASK", "DONE", "2026-08-13", "MS-MED-02", "S1"),
            ("Xây dựng API POST /api/v1/reception/check-in cấp số thứ tự ưu tiên theo slot", "STORY", "DONE", "2026-08-24", "MS-MED-02", "S2"),
            ("Bàn giao & hoàn thiện màn hình hàng đợi quầy lễ tân từ MED-U18 sang MED-U09 (DIS-MED-OFFBOARD-01)", "STORY", "DONE", "2026-08-24", "MS-MED-02", "S2"),
            ("Xây dựng màn hình hiển thị sảnh chờ chỉ hiện mã Q-XXX và chữ cái viết tắt tên", "TASK", "DONE", "2026-08-26", "MS-MED-02", "S2"),
            ("Tích hợp luồng xếp khách WalkIn vào khung giờ dự phòng gần nhất trong ca", "TASK", "DONE", "2026-08-27", "MS-MED-02", "S2"),
            ("Trình diễn luồng Check-in và gọi số ẩn danh tại buổi Demo M2 cùng An Khang", "TASK", "DONE", "2026-08-28", "MS-MED-02", "S2"),
            ("Cài đặt middleware chặn HTTP 403 nếu vai trò RECEPTIONIST thường gọi bulk-reschedule", "TASK", "DONE", "2026-09-08", "MS-MED-03", "S3"),
            ("Xây dựng job cuối ca chuyển các lịch Scheduled quá hạn 45 phút sang Missed", "TASK", "DONE", "2026-09-10", "MS-MED-03", "S3"),
            ("Sửa lỗi nhấp nháy danh sách số thứ tự khi có 2 quầy bấm gọi khách cùng giây", "BUG", "DONE", "2026-09-14", "MS-MED-03", "S3"),
            ("Phát triển API xuất báo cáo lưu lượng ngày daily-traffic.xlsx đã khử cột SĐT", "STORY", "DONE", "2026-09-15", "MS-MED-03", "S3"),
            ("Subtask viết bài kiểm thử từ chối mọi query param cố mở khóa cột SĐT khi xuất Excel", "TASK", "DONE", "2026-09-16", "MS-MED-03", "S3"),
            ("Xây dựng bảng chỉ số thời gian chờ trung bình từ lúc CheckedIn tới lúc hoàn tất quầy", "TASK", "DONE", "2026-09-21", "MS-MED-03", "S4"),
            ("Bổ sung bộ lọc đối soát riêng lượt Cancelled báo trước và lượt Missed không đến", "TASK", "DONE", "2026-09-23", "MS-MED-03", "S4"),
            ("Thực thi bộ 28 kịch bản kiểm thử RBAC và ẩn danh sảnh chờ (DOC-MEDADM-TST-005)", "TASK", "DONE", "2026-09-24", "MS-MED-03", "S4"),
            ("Tối ưu cơ chế đẩy WebSocket cập nhật hàng đợi quầy tiếp đón dưới 500ms", "TASK", "DONE", "2026-09-28", "MS-MED-03", "S4"),
            ("Kiểm tra khả năng đọc rõ bảng số Q-XXX trên màn hình tivi 43 inch khoảng cách 5m", "TASK", "DONE", "2026-09-29", "MS-MED-03", "S4"),
            ("Xác nhận thu hồi toàn bộ token cũ và quyền dự án của cựu nhân sự MED-U18", "TASK", "DONE", "2026-08-24", "MS-MED-02", "S2"),
            ("Chốt kiểm tra sẵn sàng phân hệ quầy tiếp đón cho cổng Pilot M3", "TASK", "DONE", "2026-10-01", "MS-MED-03", "S4"),
            ("Triển khai biểu đồ mật độ khách tiếp đón khung cao điểm 08:00–10:00 sáng trong Pilot", "STORY", "IN_REVIEW", "2026-10-09", "MS-MED-04", "S5"),
            ("Tinh chỉnh âm báo gọi số vừa đủ nghe tại khu vực quầy tiếp đón An Khang", "TASK", "IN_PROGRESS", "2026-10-12", "MS-MED-04", "S5"),
            ("Bổ sung thống kê tỷ lệ khách đến đúng khung +-15 phút cho báo cáo tuần Leader", "TASK", "IN_PROGRESS", "2026-10-13", "MS-MED-04", "S5"),
            ("Rà soát phân quyền tài khoản chỉ xem báo cáo tổng hợp của Quản lý phòng khám", "TASK", "IN_REVIEW", "2026-10-14", "MS-MED-04", "S5"),
            ("Chuẩn bị tài liệu hướng dẫn đối soát số liệu cuối ca cho nhân viên tiếp đón", "TASK", "TODO", "2026-10-15", "MS-MED-04", "S5"),
            ("Hủy yêu cầu xuất Excel kèm số điện thoại đầy đủ theo quyết định bác bỏ CFB-2026-02", "STORY", "CANCELLED", "2026-09-03", "MS-MED-03", "S3"),
            ("Chờ đại diện vận hành An Khang thống nhất nhãn ưu tiên hỗ trợ người cao tuổi tại quầy", "TASK", "BLOCKED", "2026-10-13", "MS-MED-04", "S5"),
            ("Hoàn thiện bảng kiểm nghiệm thu phân hệ tiếp đón hành chính cho cổng M4", "TASK", "TODO", "2026-10-16", "MS-MED-04", "S5"),
        ],
        "MED-PIL": [
            ("Lập kế hoạch tổng thể triển khai Pilot An Khang theo 4 cổng Milestone M1–M4", "STORY", "DONE", "2026-05-14", "MS-MED-01", None),
            ("Khảo sát hạ tầng mạng LAN/Wi-Fi và bố trí 2 quầy tiếp đón tại phòng khám đối tác", "TASK", "DONE", "2026-05-25", "MS-MED-01", None),
            ("Ký biên bản cam kết sử dụng 100% dữ liệu hành chính synthetic trong suốt kỳ Pilot", "TASK", "DONE", "2026-06-08", "MS-MED-01", None),
            ("Thiết lập kết nối mTLS và môi trường Pilot cô lập trên cụm đám mây MediFlow", "STORY", "DONE", "2026-07-06", "MS-MED-02", None),
            ("Cấu hình bot tự động MED-BOT-NOTIFY-PROBE kiểm tra luồng callback mỗi 15 phút 24/7", "TASK", "DONE", "2026-07-16", "MS-MED-02", None),
            ("Chuẩn bị kịch bản và dữ liệu mẫu hành chính phục vụ buổi trình diễn Demo M2", "TASK", "DONE", "2026-08-18", "MS-MED-02", None),
            ("Tích hợp webhook nhận biên nhận trạng thái gửi tin từ sandbox VietNotify", "STORY", "DONE", "2026-08-10", "MS-MED-02", None),
            ("Tổ chức buổi Demo Milestone M2 và ghi nhận biên bản phản hồi CFB-2026-01 / CFB-2026-02", "STORY", "DONE", "2026-08-28", "MS-MED-02", None),
            ("Xây dựng bộ kiểm tra tự động chặn mọi email ngoài đuôi .invalid trước khi nạp Pilot", "TASK", "DONE", "2026-08-24", "MS-MED-02", None),
            ("Thiết lập danh mục 6 phòng lịch hẹn hành chính và khung ca mẫu tại An Khang", "TASK", "DONE", "2026-09-04", "MS-MED-03", None),
            ("Cấu hình bảng cảnh báo cho Lễ tân trưởng khi tin nhắn dời lịch báo FAILED 2 lần", "TASK", "DONE", "2026-09-10", "MS-MED-03", None),
            ("Kiểm tra tường lửa giới hạn IP kết nối từ quầy lễ tân An Khang về cổng Pilot", "TASK", "DONE", "2026-09-15", "MS-MED-03", None),
            ("Biên soạn tài liệu tập huấn thao tác quầy tiếp đón và quy tắc bảo vệ dữ liệu", "STORY", "DONE", "2026-09-18", "MS-MED-03", None),
            ("Tổ chức đào tạo thực hành đợt 1 cho nhóm nhân viên lễ tân phòng khám đối tác", "TASK", "DONE", "2026-09-23", "MS-MED-03", None),
            ("Kiểm thử liên thông toàn trình Đăng ký -> Đặt hẹn -> Check-in -> Nhắc lịch sandbox", "TASK", "DONE", "2026-09-25", "MS-MED-03", None),
            ("Chạy script kiểm toán xác nhận 0 bản ghi PII thật và 0 trường lâm sàng trên bản Pilot", "TASK", "DONE", "2026-09-30", "MS-MED-03", None),
            ("Điều chỉnh lịch mở cổng Pilot M3 từ 08/10 sang 12/10 sau sự cố mưa bão cuối Sprint 4", "TASK", "DONE", "2026-10-02", "MS-MED-03", None),
            ("Cấu hình thiết bị router chuyển mạch dự phòng 4G cho quầy tiếp đón phòng khám", "TASK", "DONE", "2026-10-06", "MS-MED-03", None),
            ("Tập huấn bổ sung quy trình dời lịch hàng loạt có ghi lý do cho Lễ tân trưởng", "TASK", "DONE", "2026-10-08", "MS-MED-03", None),
            ("Ban hành Sổ tay vận hành khi mất mạng cục bộ tại quầy tiếp đón (DOC-MEDPIL-RUN-005)", "TASK", "DONE", "2026-10-09", "MS-MED-03", None),
            ("[CA TRỰC PILOT THỨ BẢY 10/10] Diễn tập chuyển mạch mạng 18s & kiểm tra quầy tiếp đón", "STORY", "DONE", "2026-10-10", "MS-MED-03", None),
            ("Subtask kiểm chứng không rớt giao dịch đặt lịch đang mở khi chuyển sang mạng 4G", "TASK", "DONE", "2026-10-12", "MS-MED-03", None),
            ("Chính thức mở cổng vận hành thử nghiệm Pilot Milestone M3 sáng Thứ Hai 12/10/2026", "STORY", "DONE", "2026-10-12", "MS-MED-03", None),
            ("Giám sát sát sao ngày đầu vận hành thử nghiệm tại 2 quầy tiếp đón An Khang", "TASK", "DONE", "2026-10-12", "MS-MED-04", None),
            ("Kiểm tra độ ổn định callback của bot MED-BOT-NOTIFY-PROBE đạt 99.9% tuần đầu Pilot", "TASK", "DONE", "2026-10-13", "MS-MED-04", None),
            ("Thu thập và phân loại phản hồi mới CFB-2026-03 vào danh sách chờ đánh giá chính sách", "TASK", "DONE", "2026-10-13", "MS-MED-04", None),
            ("Đo kiểm thời gian phản hồi trung bình tại quầy tiếp đón trong khung cao điểm sáng", "TASK", "IN_REVIEW", "2026-10-14", "MS-MED-04", None),
            ("Soạn thảo bản nháp Biên bản đánh giá sau tuần Pilot đầu & nghiệm thu M4 (DOC-MEDPIL-SIGN-006)", "STORY", "IN_PROGRESS", "2026-10-15", "MS-MED-04", None),
            ("Đối chiếu danh mục điều kiện tiên quyết liên dự án trước buổi họp nghiệm thu M4", "TASK", "IN_PROGRESS", "2026-10-15", "MS-MED-04", None),
            ("Hủy phương án đặt máy chủ vật lý tại phòng khám do mô hình đám mây mTLS đạt chuẩn độ trễ", "TASK", "CANCELLED", "2026-07-14", "MS-MED-02", None),
            ("Chờ đối tác VietNotify phê duyệt mã template thông báo dời lịch ngoài môi trường sandbox", "TASK", "BLOCKED", "2026-10-12", "MS-MED-04", None),
            ("Tổ chức họp rà soát kết quả Pilot và ký nghiệm thu cổng Milestone M4", "STORY", "TODO", "2026-10-16", "MS-MED-04", None),
        ],
    }[pid]

    blueprints: list[dict[str, Any]] = []
    for idx, (title, ttype, st, s_date, ms_id, sp_tag) in enumerate(topics, start=1):
        sp_id = f"{pcode}-{sp_tag}" if (methodology == "HYBRID" and sp_tag) else None
        bp: dict[str, Any] = {
            "title": title,
            "description": f"[{pid} / {ms_id}" + (f" / {sp_id}" if sp_id else " / Milestone Gate") + f"] {title}. Thực hiện trong phạm vi quản lý lịch hẹn và hồ sơ hành chính giả lập (100% phi lâm sàng).",
            "type": ttype,
            "status": st,
            "priority": "HIGH" if (ttype == "BUG" or st == "BLOCKED" or idx in (1, 14, 18, 21, 25)) else ("LOW" if st == "CANCELLED" else "MEDIUM"),
            "start_date": s_date,
            "duration_days": 4 if st == "DONE" else 2,
            "sprint_id": sp_id,
            "milestone_id": ms_id,
            "labels": [methodology.lower(), pid.lower(), ms_id.lower()],
        }

        if pid == "MED-REG":
            if idx == 16:
                bp["parent_seq"] = 11
                bp["assignee_id"] = "MED-U15"
            elif idx == 30:
                bp["transition_reason"] = "Loại khỏi phạm vi theo cổng Milestone M1 để giữ tối giản biểu mẫu hành chính tiếp đón."
            elif idx == 31:
                bp["assignee_id"] = "MED-U09"
                bp["transition_reason"] = "Đang chờ điều phối viên mạng phòng khám An Khang xác nhận thông số kết nối máy in tem mã tại quầy số 2."

        elif pid == "MED-APT":
            if idx == 14:
                bp["assignee_id"] = "MED-U10"
                bp["rework"] = True
                bp["is_overtime"] = True
                bp["updated_date"] = "2026-09-09"
                bp["rework_reason"] = "Bổ sung thứ tự lấy khóa ORDER BY slot_id ASC theo review DOC-MEDAPT-DB-002 v1 để chống deadlock."
                bp["task_note"] = {
                    "title": "Nâng cấp khóa tương tranh slot lịch hẹn v2 (thay thế DOC-MEDAPT-DB-001-LEGACY)",
                    "accomplishments": "Áp dụng SELECT FOR UPDATE ORDER BY slot_id ASC và CHECK (booked_count <= capacity) trước kỳ nghỉ ốm của MED-U10.",
                    "approach": "Khóa slot theo thứ tự định danh tăng dần khi dời nhiều cuộc hẹn trong cùng giao dịch.",
                    "reason": "Khắc phục triệt để lỗi đặt trùng slot phát hiện khi thử tải đồng thời ở buổi Demo M2.",
                }
            elif idx == 15:
                bp["parent_seq"] = 14
                bp["assignee_id"] = "MED-U11"
                bp["disruption_id"] = "DIS-MED-SICK-01"
                bp["handover_from_user_id"] = "MED-U10"
                bp["handover_date"] = "2026-09-10"
                bp["updated_date"] = "2026-09-11"
                bp["handover_reason"] = "MED-U10 nghỉ phép ốm hành chính 10–11/09/2026 (DIS-MED-SICK-01); bàn giao kiểm thử tương tranh sang MED-U11 để đóng Sprint 3 đúng hạn."
                bp["task_note"] = {
                    "title": "Bàn giao nghỉ ốm DIS-MED-SICK-01: Kiểm thử 50 luồng đặt chung 1 slot lịch hẹn",
                    "accomplishments": "Trịnh Thanh Tùng (MED-U11) hoàn tất bài kiểm thử tương tranh: đúng 1 giao dịch thành công và 49 giao dịch nhận HTTP 409 an toàn.",
                    "approach": "Chạy kiểm thử tích hợp tự động trên PostgreSQL 16 với cấu hình khóa dòng mới của DOC-MEDAPT-DB-002 v2.",
                    "reason": "Đảm bảo đóng trọn vẹn Sprint 3 khi thành viên phụ trách chính nghỉ phép ốm 2 ngày.",
                }
            elif idx == 18:
                bp["assignee_id"] = "MED-U11"
                bp["is_overtime"] = True
                bp["updated_date"] = "2026-09-25"
                bp["task_note"] = {
                    "title": "Triển khai phản hồi được duyệt CFB-2026-01: API Lễ tân trưởng dời lịch hàng loạt",
                    "accomplishments": "Hoàn thành POST /api/v1/appointments:bulk-reschedule giới hạn 30 lịch/lần, bắt buộc quyền RECEPTION_SHIFT_LEAD và reschedule_reason >= 10 ký tự.",
                    "approach": "Ghi vết đầy đủ vào bảng reschedule_audits và đẩy sự kiện thông báo qua Transactional Outbox.",
                    "reason": "Hiện thực hóa yêu cầu thực tế từ Demo M2 sau khi đã được đánh giá phân quyền và phê duyệt chính thức.",
                }
            elif idx == 19:
                bp["parent_seq"] = 18
                bp["assignee_id"] = "MED-U11"
                bp["updated_date"] = "2026-09-28"
            elif idx == 25:
                # Headline Hybrid Spillover task from Sprint 4 -> Sprint 5 due to storm network outage!
                bp["assignee_id"] = "MED-U15"
                bp["disruption_id"] = "DIS-MED-STORM-01"
                bp["spillover_count"] = 1
                bp["spillover_from_sprint_id"] = "MEDAPT-S4"
                bp["spillover_date"] = "2026-10-02"
                bp["updated_date"] = "2026-10-13"
                bp["task_note"] = {
                    "title": "Chuyển tiếp (Spillover) từ MEDAPT-S4 sang MEDAPT-S5 do mưa bão mất mạng (DIS-MED-STORM-01)",
                    "accomplishments": "Sau sự cố đứt cáp viễn thông khu vực cư trú ngày 28–29/09, Hồ Minh Triết (MED-U15) cùng MED-U17 đã chạy bù bộ kiểm thử dời lịch 30 cuộc hẹn và đưa task sang IN_REVIEW trong Sprint 5.",
                    "approach": "Thực hiện rollover tường minh trước khi đóng Sprint 4 để tuân thủ quy tắc không để task dở dang trong COMPLETED sprint.",
                    "reason": "Giải thích rõ nguyên nhân lùi cổng sẵn sàng Pilot MS-MED-03 từ 08/10 sang 12/10.",
                }
            elif idx == 30:
                bp["transition_reason"] = "Hủy tự động gán chéo chuyên khoa để tránh xếp nhầm ca bác sĩ khi lễ tân thao tác nhanh."
            elif idx == 31:
                bp["assignee_id"] = "MED-U12"
                bp["transition_reason"] = "Đang chờ Ban điều hành phòng khám An Khang xác nhận lịch tạm ngưng bảo trì phòng tư vấn số 4."

        elif pid == "MED-ADM":
            if idx == 6:
                bp["created_by"] = "MED-U18"
                bp["assignee_id"] = "MED-U18"
                bp["updated_date"] = "2026-08-19"
            elif idx == 9:
                bp["assignee_id"] = "MED-U09"
                bp["disruption_id"] = "DIS-MED-OFFBOARD-01"
                bp["handover_from_user_id"] = "MED-U18"
                bp["handover_date"] = "2026-08-21"
                bp["updated_date"] = "2026-08-28"
                bp["handover_reason"] = "Kỹ sư Frontend MED-U18 nghỉ việc cuối ngày 2026-08-21; bàn giao toàn bộ giao diện hàng đợi tiếp đón sang MED-U09 từ đầu Sprint 2."
            elif idx == 17:
                bp["parent_seq"] = 16
                bp["assignee_id"] = "MED-U14"
            elif idx == 30:
                bp["transition_reason"] = "Bị hủy theo quyết định bác bỏ CFB-2026-02 tại DOC-MEDADM-EXPORT-006 nhằm giữ cứng include_phone_in_excel_export = false."
            elif idx == 31:
                bp["assignee_id"] = "MED-U13"
                bp["transition_reason"] = "Chờ đại diện vận hành phòng khám An Khang chốt quy ước nhãn ưu tiên hỗ trợ người cao tuổi tại quầy lễ tân."

        elif pid == "MED-PIL":
            if idx == 21:
                # Scheduled Saturday Pilot Cutover & Kiosk Rehearsal under OC-MED-PILOT-SAT-1010
                bp["created_by"] = "MED-U06"
                bp["assignee_id"] = "MED-U06"
                bp["oncall_ts"] = {
                    "created_at": "2026-10-10T08:30:00+07:00",
                    "actor_type": "human",
                    "work_mode": "weekend_incident_ot",
                    "is_overtime": True,
                    "in_progress_at": "2026-10-10T09:15:00+07:00",
                    "updated_at": "2026-10-10T15:30:00+07:00",
                    "updated_work_mode": "weekend_incident_ot",
                    "updated_is_overtime": True,
                }
                bp["task_note"] = {
                    "author_id": "MED-U06",
                    "created_at": "2026-10-10T15:30:00+07:00",
                    "work_mode": "weekend_incident_ot",
                    "is_overtime": True,
                    "title": "Biên bản ca trực diễn tập hạ tầng Pilot Thứ Bảy 10/10/2026 (OC-MED-PILOT-SAT-1010)",
                    "accomplishments": "Đặng Bảo Châu (MED-U06) và Mai Tuấn Anh (MED-U16) hoàn tất diễn tập ngắt đường truyền chính và chuyển mạch sang 4G trong 18 giây tại quầy lễ tân An Khang.",
                    "approach": "Thực hiện vào Thứ Bảy theo lịch trực được duyệt trước để không ảnh hưởng khung giờ đón khách ngày thường.",
                    "reason": "Đảm bảo an toàn vận hành trước khi chính thức mở cổng Pilot Milestone M3 sáng Thứ Hai 12/10/2026.",
                }
            elif idx == 22:
                bp["parent_seq"] = 21
                bp["assignee_id"] = "MED-U16"
                bp["updated_date"] = "2026-10-12"
            elif idx == 25:
                bp["assignee_id"] = "MED-U16"
                bp["bot_comment"] = {
                    "bot_id": "MED-BOT-NOTIFY-PROBE",
                    "created_at": "2026-10-14T07:15:00+07:00",
                    "body": "[MED-BOT-NOTIFY-PROBE] Tổng hợp tự động 96 chu kỳ kiểm tra callback mTLS trong 24h qua: độ khả dụng đạt 99.9%, độ trễ trung bình 92ms.",
                }
            elif idx == 30:
                bp["transition_reason"] = "Không cần đầu tư máy chủ vật lý tại chỗ sau khi kết nối đám mây mTLS đạt đầy đủ yêu cầu bảo mật và độ trễ."
            elif idx == 31:
                bp["assignee_id"] = "MED-U16"
                bp["transition_reason"] = "Đang chờ bộ phận thẩm định của đối tác VietNotify phê duyệt mã template tin nhắn thông báo dời lịch ngoài môi trường sandbox."

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
    sprints = _build_hybrid_sprints(projects)

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
        bps = _make_mediflow_blueprints(pid, proj["code"], proj["methodology"])
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

    doc_specs = build_mediflow_doc_specs(task_id_by_key)
    project_docs, doc_versions = render_project_documents_and_versions(
        pkg_root=PKG_ROOT,
        namespace=NAMESPACE,
        org_id=PRIMARY_ORG_ID,
        org_banner="MEDIFLOW HEALTHTECH  •  HYBRID CLINIC SCHEDULING & ADMIN PILOT",
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

    eval_cases = build_mediflow_eval_cases(make_eval_case, AS_OF_DATE, task_id_by_key, note_id_by_key)

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
            "overtime_hours": "17:00-22:00 (plus scheduled Saturday Pilot Cutover Duty OC-MED-PILOT-SAT-1010)",
        },
        "organizations": orgs,
        "users": users,
        "organization_memberships": org_mems,
        "role_assignments": role_assigns,
        "projects": projects,
        "project_memberships": proj_mems,
        "sprints": sprints,
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
        "oncall_schedules": ONCALL_SCHEDULES,
        "evaluation_cases": eval_cases,
    }

    neg_fixtures = build_standard_negative_fixtures(NAMESPACE, bundle)

    readme_md = f"""# Organization 4 — MediFlow: Nền Tảng Quản Lý Lịch Hẹn & Tiếp Đón Hành Chính Phòng Khám (Hybrid)

**Trạng thái:** Hoàn thành bộ dataset synthetic kiểm chứng được (`v1.0.0`, `as_of_date = {AS_OF_DATE}`); tái tạo 100% bằng `python -X utf8 -B Dataset/Organization4-MediFlow/tools/generate_org.py`. Chưa seed MongoDB runtime của Continuum.

## 1. Bối cảnh nghiệp vụ, Ranh giới phi lâm sàng & Phương pháp Hybrid
- **Tổ chức chính (`ORG-MED`)**: Công ty sản phẩm giả lập **MediFlow** triển khai thử nghiệm (Pilot) nền tảng quản lý lịch làm việc bác sĩ, đặt lịch hẹn và hàng đợi tiếp đón hành chính cho **Phòng khám Đa khoa An Khang (`ORG-ANKHANG`)**, tích hợp cổng tin nhắn giả lập **VietNotify (`ORG-VIETNOTIFY`)**.
- **Ranh giới dữ liệu nghiêm ngặt**: **100% dữ liệu hành chính synthetic** (mã `AK-PAT-XXXXXX`, đuôi email `.invalid`, che mặt nạ SĐT `***-***-482`). **Tuyệt đối không chứa** bệnh án lâm sàng, chẩn đoán, xét nghiệm, đơn thuốc hay PII người thật.
- **Phương pháp quản lý cấp project (Hybrid)**:
  - Ba dự án sản phẩm (`MED-REG`, `MED-APT`, `MED-ADM`) vận hành theo **Hybrid**: hội tụ theo 4 cổng Milestone (`MS-MED-01..04`) và phát triển qua **5 Sprint 2 tuần/dự án** (`15` sprints tổng cộng: `S1..S4` `COMPLETED` sạch 100% không còn task dở dang, `S5` là Sprint `ACTIVE` duy nhất mỗi dự án).
  - Dự án triển khai thực địa (`MED-PIL`) quản trị theo cổng Milestone không chia Sprint (`methodology = "WATERFALL"`, `sprint_id = null`), chứng minh mô hình quản lý thuộc về từng project.
- **Tình huống thực tế nổi bật**:
  1. **Phân loại phản hồi từ Demo M2 (`structured/clinic_feedback_log.jsonl`)**: Chấp thuận `CFB-2026-01` (cho phép `RECEPTION_SHIFT_LEAD` dời lịch hàng loạt có kiểm toán tại `MEDAPT-18`, `DOC-MEDAPT-REQ-001` v2); **Từ chối** `CFB-2026-02` (xuất Excel kèm SĐT đầy đủ tại `DOC-MEDADM-EXPORT-006` `REJECTED`, `MEDADM-30` `CANCELLED`, giữ `include_phone_in_excel_export = false`); giữ `CFB-2026-03` (khóa đặt lịch 30 ngày) ở trạng thái **phản hồi chưa duyệt** (`DOC-MEDAPT-DES-005` v2 `PENDING_REVIEW`).
  2. **Mưa bão làm Spillover Sprint & Lùi cổng Milestone M3**: Sự cố đứt cáp mưa bão cuối Sprint 4 (`DIS-MED-STORM-01` với `MED-U15`) khiến `MEDAPT-25` phải rollover sang `MEDAPT-S5` (`spillover_count = 1`) và lùi mốc sẵn sàng Pilot `MS-MED-03` từ `08/10` sang `12/10` sau buổi diễn tập ca trực Thứ Bảy `10/10/2026` (`OC-MED-PILOT-SAT-1010`).
  3. **Bàn giao nhân sự**: `MED-U18` nghỉ việc cuối Sprint 1 (`2026-08-21`, giao cho `MED-U09`); `MED-U10` nghỉ phép ốm hành chính giữa Sprint 3 (`10–11/09/2026`, giao `MEDAPT-15` cho `MED-U11`).

## 2. Nguồn tham chiếu GitHub & Giới hạn bản quyền
- Tham khảo khái niệm hành chính từ `openmrs/openmrs-core` (`2.8.10` / commit `0755f785f7d237a7a2e9d9f4e76aff43b7613ad3`, giấy phép `MPL-2.0` kèm *Healthcare Disclaimer*) và tài liệu cấu hình `openmrs/openmrs-contrib-o3-docs` (`main` commit `3a0da981e31e224a467a4432df2a65cb8dfdfe7b`, `MPL-2.0`, file `configure-patient-management.mdx`).
- **Không sao chép** bất kỳ mã nguồn, tài liệu hay mô hình lâm sàng nào của OpenMRS; không khẳng định OpenMRS dùng Hybrid. Xem chi tiết tại [../GITHUB_SOURCES_AND_LICENSES.md](../GITHUB_SOURCES_AND_LICENSES.md).

## 3. Phạm vi Continuum đã chốt & Quy mô gói dữ liệu
- **Không có Team / Không có lịch sử AI Chat / Không có entity Notebook thứ tư**.
- **Đủ 3 dạng Group Note**: `{len(all_notes)}` `TASK_NOTE` (`knowledge_eligible=false`), `{len(project_docs)}` `PROJECT_DOCUMENT` (`{len(doc_versions)}` versions, kèm 6 file DOCX), `{len(work_reports)}` `WORK_REPORT` (`DAILY` & `WEEKLY`, `MEMBER` & `LEADER`).
- **Evaluation**: `{len(eval_cases)}` benchmark cases trong `evaluation/benchmark_cases.jsonl` (`review_status = "unreviewed"` / `"chưa duyệt"`).
"""

    ic_md = f"""# Ingestion Contract — Organization 4: MediFlow (Hybrid v1.0.0)

1. **Tenant & Partner Isolation**: Chỉ nạp `ORG-MED` làm tenant chính; `ORG-ANKHANG` (phòng khám đối tác) và `ORG-VIETNOTIFY` (cổng nhắn tin đối tác) dùng để kiểm chứng cách ly đa tenant (`DENY`) và nguồn gốc phản hồi thực địa.
2. **Hybrid Sprint & Milestone Rules**:
   - `structured/sprints.jsonl` chứa 15 Sprint của 3 dự án `HYBRID` (`MED-REG`, `MED-APT`, `MED-ADM`): mỗi dự án có 4 Sprint `COMPLETED` (không chứa bất kỳ task mở nào) và đúng 1 Sprint `ACTIVE` (`S5`). Dự án `MED-PIL` có `sprint_id = null` trên toàn bộ 32 task.
   - Cổng Milestone và nhật ký phản hồi phòng khám lưu tại `structured/milestones.jsonl` và `structured/clinic_feedback_log.jsonl`. Phản hồi có `decision_status = "PENDING_EVALUATION"` tuyệt đối không được coi là quy tắc đã có hiệu lực.
3. **Ranh giới Phi Lâm Sàng & Quyền Riêng Tư**: 100% dữ liệu hành chính giả lập; cấm nạp dữ liệu bệnh án thật hoặc mở cờ `include_phone_in_excel_export`.
4. **Ba dạng Group Note & Tách biệt Evaluation**: `TASK_NOTE` luôn có `knowledge_eligible = false`; chỉ nạp phiên bản `APPROVED` mới nhất của `PROJECT_DOCUMENT` không bị `ARCHIVED` và các `WORK_REPORT` `APPROVED`. Không nạp `evaluation/benchmark_cases.jsonl` và `fixtures/negative_cases.json` vào database ứng dụng.
"""

    manifest = materialize_organization_package(
        pkg_root=PKG_ROOT,
        namespace=NAMESPACE,
        dataset_id="continuum-org4-mediflow-hybrid-v1",
        version="1.0.0",
        org_display_name="MediFlow (Clinic Appointment Scheduling & Admin Registration)",
        methodology_label="HYBRID",
        bundle=bundle,
        extra_structured_files={
            "structured/clinic_feedback_log.jsonl": CLINIC_FEEDBACK_LOG,
            "structured/milestones.jsonl": MILESTONE_RECORDS,
            "structured/oncall_schedules.jsonl": ONCALL_SCHEDULES,
            "structured/system_bots.jsonl": SYSTEM_BOTS,
        },
        negative_fixtures=neg_fixtures,
        source_attribution=SOURCE_ATTRIBUTION,
        assumptions=IMPLEMENTATION_ASSUMPTIONS,
        readme_markdown=readme_md,
        ingestion_contract_markdown=ic_md,
    )
    print(
        f"[ORG-4 MEDIFLOW] Generated successfully: {manifest['canonical_counts']['physical_files_total']} files, "
        f"{len(sprints)} sprints, {len(all_tasks)} tasks, {len(all_notes)} task notes, {len(project_docs)} docs, "
        f"{len(work_reports)} reports, {len(eval_cases)} eval cases."
    )


if __name__ == "__main__":
    main()
