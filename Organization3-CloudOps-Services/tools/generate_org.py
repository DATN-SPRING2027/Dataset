"""Deterministic generator for Organization 3 — CloudOps Services (Kanban 24/7 SaaS Operations & Incident Management)."""

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

from cloudops_docs import REPORT_NARRATIVES, build_cloudops_doc_specs  # noqa: E402
from cloudops_eval import build_cloudops_eval_cases  # noqa: E402
from cloudops_specs import (  # noqa: E402
    AS_OF_DATE,
    DISRUPTION_EVENTS,
    IMPLEMENTATION_ASSUMPTIONS,
    INCIDENT_RECORDS,
    KANBAN_WIP_POLICIES,
    NAMESPACE,
    ONCALL_SCHEDULES,
    ORG_ADMIN_IDS,
    ORG_SPECS,
    PRIMARY_ORG_ID,
    PROJECT_SPECS,
    SIM_START,
    SOURCE_ATTRIBUTION,
    SYSTEM_BOTS,
    USER_SPECS,
)
from continuum_synth import VN_HOLIDAYS_2026, build_working_days  # noqa: E402
from org_package_builder import (  # noqa: E402
    build_org_identity_graph,
    build_standard_negative_fixtures,
    build_work_reports_for_org,
    expand_project_tasks,
    make_eval_case,
    materialize_organization_package,
    render_project_documents_and_versions,
)


def _make_kanban_project_blueprints(pid: str) -> list[dict[str, Any]]:
    """Create 32 continuous-flow Kanban task blueprints (sprint_id=None) with WIP Classes of Service."""
    topics = {
        "CLD-INC": [
            ("Thiết lập ma trận phân loại sự cố SEV-0..SEV-3 và ngưỡng ACK 5 phút", "STORY", "DONE", "2026-04-20", "FIXED_DATE_SLA"),
            ("Cấu hình luồng tự động leo thang (Escalation) từ Primary sang Secondary sau 5 phút", "TASK", "DONE", "2026-04-27", "STANDARD_FLOW"),
            ("Áp đặt giới hạn shelve cảnh báo trùng tối đa 120 phút kèm tự động mở lại", "STORY", "DONE", "2026-05-04", "STANDARD_FLOW"),
            ("Xây dựng bộ băm SHA-256 fingerprint gom 500 cảnh báo lặp vào 01 AlertGroup", "STORY", "DONE", "2026-05-11", "STANDARD_FLOW"),
            ("Tích hợp worker CLD-BOT-ALERTGROUP quét các nhóm cảnh báo hết hạn shelve mỗi 60s", "TASK", "DONE", "2026-05-18", "STANDARD_FLOW"),
            ("Xây dựng API POST /api/v1/oncall/overrides kiểm tra trạng thái ACTIVE của người nhận ca", "TASK", "DONE", "2026-05-25", "STANDARD_FLOW"),
            ("Kiểm thử chịu tải chống bão 5.000 webhook cảnh báo/phút không rơi sự kiện", "TASK", "DONE", "2026-06-08", "INTANGIBLE_TECH_DEBT"),
            ("Bàn giao lịch trực lễ 02/09 và thu hồi khóa tích hợp khi CLD-U18 nghỉ việc (DIS-CLD-OFFBOARD-01)", "TASK", "DONE", "2026-08-26", "FIXED_DATE_SLA"),
            ("[EXPEDITE SEV-0] Xử lý khẩn cấp bão kết nối lễ Quốc khánh 02/09 (INC-2026-0902 — Workaround tạm thời)", "BUG", "DONE", "2026-09-02", "EXPEDITE_P0"),
            ("Subtask biên soạn & hiệu đính báo cáo hậu kiểm DOC-CLDINC-RCA-002 (bác bỏ giả thuyết DNS v1)", "TASK", "DONE", "2026-09-03", "FIXED_DATE_SLA"),
            ("Cập nhật bộ lọc chống gom nhầm hai sự cố độc lập cùng cụm Kubernetes", "BUG", "DONE", "2026-06-22", "STANDARD_FLOW"),
            ("Chuẩn hóa Sổ tay Chỉ huy Sự cố (DOC-CLDINC-RUN-006) và quy trình giao ca tuần", "STORY", "DONE", "2026-08-24", "STANDARD_FLOW"),
            ("Tự động đính kèm liên kết runbook tương ứng vào thông báo Pager ca trực", "TASK", "DONE", "2026-07-06", "STANDARD_FLOW"),
            ("Kiểm tra xác thực chữ ký HMAC cho toàn bộ webhook cảnh báo đầu vào", "TASK", "DONE", "2026-07-14", "STANDARD_FLOW"),
            ("Diễn tập mất liên lạc Primary On-Call giả lập và đo thời gian chuyển Secondary (< 310s)", "TASK", "DONE", "2026-07-28", "INTANGIBLE_TECH_DEBT"),
            ("Thiết kế giao diện bảng Kanban hiển thị làn EXPEDITE_P0 và cảnh báo chạm trần WIP=5", "STORY", "DONE", "2026-06-15", "STANDARD_FLOW"),
            ("Rà soát log phản hồi ACK tháng 08 đạt 100% trong khung cam kết SLA", "TASK", "DONE", "2026-09-04", "STANDARD_FLOW"),
            ("Tối ưu truy vấn lịch sử dòng thời gian sự cố phục vụ biên soạn Postmortem", "TASK", "DONE", "2026-09-14", "INTANGIBLE_TECH_DEBT"),
            ("Bổ sung cảnh báo sớm khi một AlertGroup bị shelve lặp lại lần thứ 2 liên tiếp", "TASK", "DONE", "2026-09-21", "STANDARD_FLOW"),
            ("Đồng bộ mã định danh incident_id sang bảng theo dõi hậu kiểm của CLD-SUP", "TASK", "DONE", "2026-09-28", "STANDARD_FLOW"),
            ("Kiểm tra dự phòng kênh gọi thoại thứ cấp khi nhà mạng di động nghẽn cục bộ", "TASK", "DONE", "2026-10-02", "STANDARD_FLOW"),
            ("Cập nhật phân công lịch trực tháng 10/2026 đảm bảo đủ cặp Primary + Secondary", "TASK", "DONE", "2026-10-06", "FIXED_DATE_SLA"),
            ("Thống kê chỉ số MTTA / MTTR quý 3 cho buổi họp rà soát độ tin cậy", "TASK", "DONE", "2026-10-08", "STANDARD_FLOW"),
            ("Kiểm chứng cơ chế khóa không cho phép xóa lịch sử sự kiện chuyển trạng thái sự cố", "TASK", "DONE", "2026-10-09", "STANDARD_FLOW"),
            ("Đánh giá rủi ro bản nháp v2 tự động đóng sự cố SEV-1 (DOC-CLDINC-DES-005 v2)", "STORY", "IN_REVIEW", "2026-10-13", "STANDARD_FLOW"),
            ("Tinh chỉnh mẫu ghi chú giao ca tối Thứ Sáu giữa nhóm Incident và Infrastructure", "TASK", "IN_PROGRESS", "2026-10-13", "STANDARD_FLOW"),
            ("Viết kịch bản diễn tập GameDay quý 4 cho tình huống suy giảm đa vùng", "TASK", "IN_PROGRESS", "2026-10-14", "INTANGIBLE_TECH_DEBT"),
            ("Rà soát danh sách đầu mối liên hệ khẩn cấp của các đối tác hạ tầng thượng nguồn", "TASK", "IN_REVIEW", "2026-10-15", "STANDARD_FLOW"),
            ("Chuẩn bị lịch trực dự phòng giai đoạn cao điểm quyết toán cuối năm của FinLedger", "TASK", "TODO", "2026-10-15", "FIXED_DATE_SLA"),
            ("Hủy tích hợp cổng SMS cố định đời cũ do đã chuyển hoàn toàn sang kênh đa phương thức", "TASK", "CANCELLED", "2026-07-16", "INTANGIBLE_TECH_DEBT"),
            ("Chờ đối tác VinaCloud gửi biên bản xác nhận định tuyến dự phòng BGP liên vùng", "TASK", "BLOCKED", "2026-10-12", "FIXED_DATE_SLA"),
            ("Cập nhật tài liệu hướng dẫn đọc chỉ số SLE chu kỳ 85% cho thành viên mới", "TASK", "TODO", "2026-10-16", "STANDARD_FLOW"),
        ],
        "CLD-OBS": [
            ("Xác lập khung SLI/SLO khả dụng 99.95% và độ trễ P99 <= 450ms đa tenant", "STORY", "DONE", "2026-04-22", "FIXED_DATE_SLA"),
            ("Triển khai công thức cảnh báo tốc độ đốt ngân sách lỗi đa cửa sổ (14.4x burn-rate)", "STORY", "DONE", "2026-05-05", "STANDARD_FLOW"),
            ("Triển khai cụm OpenTelemetry Collector với Tail-Based Sampling giữ 100% lỗi 5xx", "STORY", "DONE", "2026-05-28", "STANDARD_FLOW"),
            ("Cài đặt processor tự động khử Authorization header, cookie và email trên span", "TASK", "DONE", "2026-06-02", "FIXED_DATE_SLA"),
            ("Xây dựng bảng theo dõi tiêu thụ Error Budget theo thời gian thực cho từng phân hệ", "TASK", "DONE", "2026-06-11", "STANDARD_FLOW"),
            ("Chuẩn hóa bộ nhãn telemetry tổng hợp (tenant_tier, service_name) không chứa PII", "TASK", "DONE", "2026-06-18", "STANDARD_FLOW"),
            ("Áp đặt giới hạn 50.000 chuỗi thời gian hoạt động/job chống bùng nổ cardinality", "TASK", "DONE", "2026-06-23", "INTANGIBLE_TECH_DEBT"),
            ("Xây dựng dịch vụ Dead-Man-Switch Heartbeat ping 60 giây giám sát worker nền", "STORY", "DONE", "2026-07-06", "STANDARD_FLOW"),
            ("Cấu hình nén dữ liệu chuỗi thời gian lưu nóng 30 ngày và lưu ấm 90 ngày", "TASK", "DONE", "2026-07-15", "STANDARD_FLOW"),
            ("Tích hợp dò synthetic kiểm tra luồng cấp phát JWT mỗi 30 giây từ 2 vùng mạng", "TASK", "DONE", "2026-07-23", "STANDARD_FLOW"),
            ("Sửa lỗi rò rỉ bộ nhớ đệm trên collector khi đích nhận trace chập chờn", "BUG", "DONE", "2026-08-03", "STANDARD_FLOW"),
            ("Thiết lập quy trình kiểm toán cảnh báo nhiễu 2 tuần/lần (mục tiêu false-positive < 15%)", "STORY", "DONE", "2026-08-11", "STANDARD_FLOW"),
            ("Gỡ bỏ 9 cảnh báo dung lượng đĩa tĩnh trùng lặp gây nhiễu ca trực tối", "TASK", "DONE", "2026-08-17", "INTANGIBLE_TECH_DEBT"),
            ("Kiểm tra hiệu năng truy vấn biểu đồ độ trễ 30 ngày dưới 600ms", "TASK", "DONE", "2026-08-25", "STANDARD_FLOW"),
            ("Bổ sung metric cl_waiting và sv_active riêng cho từng pool PgBouncer sau lễ 02/09", "STORY", "DONE", "2026-09-08", "EXPEDITE_P0"),
            ("Xây dựng cảnh báo sớm khi hàng đợi chờ kết nối CSDL tăng liên tục quá 90 giây", "TASK", "DONE", "2026-09-11", "STANDARD_FLOW"),
            ("Kiểm chứng bộ lọc khử dữ liệu nhạy cảm trên 1 triệu bản ghi log mẫu", "TASK", "DONE", "2026-09-18", "FIXED_DATE_SLA"),
            ("Tinh chỉnh ngưỡng cảnh báo độ trễ cổng webhook sau đợt tăng lưu lượng tháng 09", "TASK", "DONE", "2026-09-24", "STANDARD_FLOW"),
            ("Subtask kiểm thử kích hoạt CLD-BOT-HEARTBEAT chính xác sau 180 giây mất ping", "TASK", "DONE", "2026-07-10", "STANDARD_FLOW"),
            ("Bổ sung biểu đồ theo dõi tỷ lệ HTTP 403 bất thường tại lớp WAF theo từng đối tác", "TASK", "DONE", "2026-09-30", "STANDARD_FLOW"),
            ("Tối ưu chi phí lưu trữ span bằng cách loại bỏ healthcheck nội bộ không lỗi", "TASK", "DONE", "2026-10-05", "INTANGIBLE_TECH_DEBT"),
            ("Đối chiếu độ chính xác đồng hồ đo SLO tháng 09 với bảng đối soát của CLD-SUP", "TASK", "DONE", "2026-10-07", "FIXED_DATE_SLA"),
            ("Hoàn thành đợt rà soát Alert Fatigue đầu tháng 10: tỷ lệ nhiễu giảm còn 6.4%", "TASK", "DONE", "2026-10-09", "STANDARD_FLOW"),
            ("Kiểm tra cảnh báo hết hạn chứng chỉ TLS trước 21 ngày trên toàn bộ ingress", "TASK", "DONE", "2026-10-12", "STANDARD_FLOW"),
            ("Cập nhật dashboard phân tách tải giữa auth_pool và reporting_pool", "STORY", "IN_REVIEW", "2026-10-13", "STANDARD_FLOW"),
            ("Soát xét các metric cũ không còn biểu đồ tham chiếu để lên lịch thu hồi", "TASK", "IN_PROGRESS", "2026-10-14", "INTANGIBLE_TECH_DEBT"),
            ("Viết kiểm thử tự động chặn khai báo nhãn metric chứa chuỗi email hoặc UUID", "TASK", "IN_PROGRESS", "2026-10-15", "STANDARD_FLOW"),
            ("Đánh giá độ trễ đẩy dữ liệu từ cụm Read-Replica sang bảng tổng hợp SLI", "TASK", "IN_REVIEW", "2026-10-15", "STANDARD_FLOW"),
            ("Chuẩn bị gói cấu hình giám sát cho đợt nâng cấp phiên bản Collector tháng 11", "TASK", "TODO", "2026-10-15", "STANDARD_FLOW"),
            ("Hủy triển khai cảnh báo Pager khi CPU pod > 65% trong 30s (DOC-CLDOBS-SLI-006 REJECTED)", "STORY", "CANCELLED", "2026-08-21", "STANDARD_FLOW"),
            ("Chờ nhóm CLD-INF chốt danh mục mã quy tắc WAF chuẩn trước khi bật exporter mới", "TASK", "BLOCKED", "2026-10-13", "STANDARD_FLOW"),
            ("Tài liệu hóa hướng dẫn tra cứu trace lỗi xuyên dịch vụ bằng trace_id", "TASK", "TODO", "2026-10-16", "STANDARD_FLOW"),
        ],
        "CLD-INF": [
            ("Thiết lập kiến trúc cụm Kubernetes phân tách pool node giao dịch và xử lý nền", "STORY", "DONE", "2026-04-21", "STANDARD_FLOW"),
            ("Triển khai quản lý trạng thái Terraform tập trung kèm khóa chống chạy đồng thời", "TASK", "DONE", "2026-04-29", "STANDARD_FLOW"),
            ("Áp dụng NetworkPolicy mặc định cô lập lưu lượng ngang giữa các namespace dịch vụ", "STORY", "DONE", "2026-05-19", "FIXED_DATE_SLA"),
            ("Soạn thảo sổ tay migration một bước ban đầu (cựu SRE CLD-U18 — sau này đã ARCHIVED)", "TASK", "DONE", "2026-06-04", "STANDARD_FLOW"),
            ("Thiết lập sao lưu WAL liên tục đảm bảo RPO <= 5 phút và RTO <= 20 phút", "STORY", "DONE", "2026-06-11", "FIXED_DATE_SLA"),
            ("Triển khai worker CLD-BOT-TF-DRIFT quét lệch cấu hình hạ tầng mỗi 60 phút", "STORY", "DONE", "2026-06-17", "STANDARD_FLOW"),
            ("Tối ưu cấu hình HPA giãn pod sớm theo hàng đợi kết nối thực tế", "TASK", "DONE", "2026-07-02", "STANDARD_FLOW"),
            ("Cấu hình tự động xoay vòng mật khẩu kết nối CSDL không làm gián đoạn phiên", "TASK", "DONE", "2026-07-20", "STANDARD_FLOW"),
            ("[EXPEDITE SEV-1] Quay lui khẩn cấp lỗi tương thích cột tối 18/08 (INC-2026-0818)", "BUG", "DONE", "2026-08-18", "EXPEDITE_P0"),
            ("Ban hành chuẩn migration Expand/Contract 3 bước và lưu trữ runbook cũ (DOC-CLDINF-DB-002)", "STORY", "DONE", "2026-08-20", "FIXED_DATE_SLA"),
            ("Thu hồi chứng chỉ SSH/Kubeconfig và quyền IAM của CLD-U18 đúng ngày 28/08", "TASK", "DONE", "2026-08-28", "FIXED_DATE_SLA"),
            ("Diễn tập khôi phục PITR PostgreSQL định kỳ tháng 08 đạt 14 phút", "TASK", "DONE", "2026-08-25", "STANDARD_FLOW"),
            ("Tích hợp linter CI chặn câu lệnh DROP COLUMN / ALTER COLUMN TYPE trực tiếp", "TASK", "DONE", "2026-08-31", "INTANGIBLE_TECH_DEBT"),
            ("Tách cụm Read-Replica chuyên trách cho các truy vấn báo cáo phân tích dài", "STORY", "DONE", "2026-09-04", "EXPEDITE_P0"),
            ("Cấu hình giới hạn bộ nhớ và CPU tường minh cho 100% deployment sản xuất", "TASK", "DONE", "2026-07-29", "STANDARD_FLOW"),
            ("Kiểm tra định kỳ tính toàn vẹn bản sao lưu ngoại vi khác vùng khả dụng", "TASK", "DONE", "2026-08-10", "STANDARD_FLOW"),
            ("Nâng cấp bản vá bảo mật nhân node worker theo hình thức cuốn chiếu an toàn", "TASK", "DONE", "2026-09-14", "STANDARD_FLOW"),
            ("Tinh chỉnh tham số tcp_keepalives_idle giữa PgBouncer và PostgreSQL Primary", "TASK", "DONE", "2026-09-15", "STANDARD_FLOW"),
            ("Khắc phục gốc INC-2026-0902: Tách riêng auth_pool (60 kết nối, timeout 3s) & reporting_pool", "STORY", "DONE", "2026-09-08", "EXPEDITE_P0"),
            ("Subtask bàn giao nghỉ ốm (DIS-CLD-SICK-01): kiểm thử tải chứng minh cô lập auth_pool 38ms", "TASK", "DONE", "2026-09-16", "FIXED_DATE_SLA"),
            ("Áp dụng cấu hình PgBouncer đa pool lên toàn bộ vùng sản xuất không gián đoạn", "TASK", "DONE", "2026-09-22", "STANDARD_FLOW"),
            ("Kiểm chứng tự động ngắt truy vấn báo cáo vượt ngưỡng 15.000ms trên Read-Replica", "TASK", "DONE", "2026-09-24", "STANDARD_FLOW"),
            ("[EXPEDITE SEV-1] Ca trực Thứ Bảy 26/09 gỡ rule WAF sửa tay chặn nhầm FinLedger (INC-2026-0926)", "BUG", "DONE", "2026-09-26", "EXPEDITE_P0"),
            ("Đồng bộ toàn bộ rule WAF vào Terraform & khóa quyền sửa tay trên console (DOC-CLDINF-ARC-001 v2)", "STORY", "IN_REVIEW", "2026-09-28", "FIXED_DATE_SLA"),
            ("Subtask viết bài kiểm thử tự động danh sách allowlist IP webhook FinLedger trong CI", "TASK", "DONE", "2026-10-02", "STANDARD_FLOW"),
            ("Diễn tập khôi phục PITR PostgreSQL tháng 10 đạt 13 phút (vượt mục tiêu RTO 20 phút)", "TASK", "DONE", "2026-10-07", "STANDARD_FLOW"),
            ("Kiểm tra pha Expand thêm cột nullable không gây chờ khóa (lock_timeout=2000ms)", "TASK", "DONE", "2026-10-12", "STANDARD_FLOW"),
            ("Rà soát phân quyền RBAC chỉ đọc trên bảng điều khiển đám mây cho nhóm vận hành", "TASK", "IN_PROGRESS", "2026-10-13", "STANDARD_FLOW"),
            ("Tối ưu thời gian lập kế hoạch (terraform plan) cho module mạng biên xuống dưới 45s", "TASK", "IN_PROGRESS", "2026-10-14", "INTANGIBLE_TECH_DEBT"),
            ("Hủy đề xuất dùng chung một database user cho cả ứng dụng web và worker báo cáo", "TASK", "CANCELLED", "2026-09-09", "STANDARD_FLOW"),
            ("Chuẩn bị lịch bảo trì pha Contract dọn cột cũ sau 14 ngày chạy ổn định", "TASK", "TODO", "2026-10-15", "STANDARD_FLOW"),
            ("Cập nhật sơ đồ luồng kết nối CSDL đa pool cho buổi đào tạo nội bộ SRE", "TASK", "TODO", "2026-10-16", "STANDARD_FLOW"),
        ],
        "CLD-SUP": [
            ("Thiết lập quy trình tiếp nhận hỗ trợ Tier-3 với cam kết phản hồi P0 <= 15 phút", "STORY", "DONE", "2026-04-23", "FIXED_DATE_SLA"),
            ("Xây dựng mẫu bản tin cập nhật trạng thái sự cố định kỳ mỗi 30 phút cho khách hàng", "TASK", "DONE", "2026-05-04", "STANDARD_FLOW"),
            ("Áp dụng quy tắc cấm đóng ticket sự cố P0/P1 khi mới chỉ có workaround tạm thời", "STORY", "DONE", "2026-05-12", "FIXED_DATE_SLA"),
            ("Thiết kế liên kết hai chiều giữa ticket CLD-SUP và mã sự cố gốc ở CLD-INC/CLD-INF", "STORY", "DONE", "2026-06-09", "STANDARD_FLOW"),
            ("Cấu hình phân quyền chặn tài khoản khách hàng đọc trực tiếp Task Note nội bộ", "TASK", "DONE", "2026-06-16", "FIXED_DATE_SLA"),
            ("Xây dựng quy trình phê duyệt 4 mắt (author != publisher) trước khi đăng Status Page", "TASK", "DONE", "2026-06-25", "STANDARD_FLOW"),
            ("Phát triển bộ lọc regex chặn rò rỉ IP nội bộ và tên tenant khác trên POST /api/v1/status-updates", "STORY", "DONE", "2026-07-01", "FIXED_DATE_SLA"),
            ("Thiết kế bảng sla_breach_ledgers và postmortem_action_items theo dõi cam kết sau sự cố", "TASK", "DONE", "2026-07-20", "STANDARD_FLOW"),
            ("Xây dựng công cụ tính tự động thời gian gián đoạn hợp lệ so với ngưỡng 99.95%", "TASK", "DONE", "2026-07-28", "STANDARD_FLOW"),
            ("Soạn thảo bản tin minh bạch và gửi tóm tắt khắc phục sự cố tối 18/08 cho khách hàng", "TASK", "DONE", "2026-08-21", "FIXED_DATE_SLA"),
            ("Rà soát chất lượng phản hồi Tier-3 tháng 08 đạt 100% đúng chuẩn khử nhạy cảm", "TASK", "DONE", "2026-08-27", "STANDARD_FLOW"),
            ("Phối hợp truyền thông trạng thái và gửi bản RCA v2 đã duyệt của sự cố lễ 02/09", "STORY", "DONE", "2026-09-08", "FIXED_DATE_SLA"),
            ("Kiểm tra đối chiếu toàn bộ hành động phòng ngừa của INC-2026-0902 đã gắn đủ bằng chứng", "TASK", "DONE", "2026-09-22", "STANDARD_FLOW"),
            ("Cập nhật danh bạ đầu mối kỹ thuật phía FinLedger để xác minh sự cố tích hợp", "TASK", "DONE", "2026-08-12", "STANDARD_FLOW"),
            ("Sửa lỗi định dạng múi giờ hiển thị trên biên bản đối soát SLA xuất PDF", "BUG", "DONE", "2026-09-10", "STANDARD_FLOW"),
            ("Kiểm thử chặn xuất bản bản tin thử nghiệm có chứa chuỗi tên bảng nội bộ (HTTP 422)", "TASK", "DONE", "2026-07-07", "STANDARD_FLOW"),
            ("Tổng hợp báo cáo tuân thủ SLA tháng 08 cho toàn bộ các gói dịch vụ doanh nghiệp", "TASK", "DONE", "2026-09-04", "FIXED_DATE_SLA"),
            ("Xác minh khóa ngoại không cho phép đóng postmortem_action_items thiếu link kiểm thử", "TASK", "DONE", "2026-09-15", "STANDARD_FLOW"),
            ("Đóng ticket tổng hợp hậu kiểm lễ 02/09 sau khi CLDINF-19 và CLDINF-20 hoàn tất", "TASK", "DONE", "2026-09-23", "FIXED_DATE_SLA"),
            ("Tiếp nhận thông báo lỗi HTTP 403 từ FinLedger và chuyển làn khẩn cấp sang CLD-INF", "STORY", "DONE", "2026-09-28", "EXPEDITE_P0"),
            ("Hướng dẫn đội vận hành FinLedger replay an toàn 148 sự kiện webhook bị chặn ngày 26/09", "STORY", "DONE", "2026-09-29", "FIXED_DATE_SLA"),
            ("Subtask đối soát khóa idempotency_key xác nhận 148/148 webhook khớp sổ cái không trùng", "TASK", "DONE", "2026-09-30", "FIXED_DATE_SLA"),
            ("Ban hành quy trình chuẩn xử lý chặn nhầm webhook đối tác (DOC-CLDSUP-RUN-005)", "TASK", "DONE", "2026-10-01", "STANDARD_FLOW"),
            ("Kiểm tra định kỳ thời gian phản hồi đầu tiên trên hàng đợi Tier-3 tuần đầu tháng 10", "TASK", "DONE", "2026-10-08", "STANDARD_FLOW"),
            ("Đối chiếu danh mục các hành động hậu kiểm đang mở của INC-2026-0926 (chờ CLDINF-24)", "TASK", "IN_REVIEW", "2026-10-13", "STANDARD_FLOW"),
            ("Chuẩn bị số liệu thống kê độ khả dụng nửa đầu tháng 10 cho cuộc họp dịch vụ", "TASK", "IN_PROGRESS", "2026-10-14", "STANDARD_FLOW"),
            ("Rà soát mẫu thông báo bảo trì định kỳ pha Contract gửi trước 7 ngày làm việc", "TASK", "IN_REVIEW", "2026-10-15", "STANDARD_FLOW"),
            ("Soạn thảo bản nháp khung báo cáo tổng kết độ tin cậy Quý 4 (DOC-CLDSUP-COM-006)", "STORY", "IN_PROGRESS", "2026-10-15", "STANDARD_FLOW"),
            ("Lập lịch họp định kỳ rà soát chất lượng dịch vụ tháng 10 với các tenant lớn", "TASK", "TODO", "2026-10-15", "FIXED_DATE_SLA"),
            ("Hủy kênh tiếp nhận hỗ trợ qua hòm thư chia sẻ không xác thực chữ ký miền", "TASK", "CANCELLED", "2026-06-29", "STANDARD_FLOW"),
            ("Chờ đại diện vận hành FinLedger ký xác nhận biên bản đối soát tín dụng SLA quý 3", "TASK", "BLOCKED", "2026-10-12", "FIXED_DATE_SLA"),
            ("Bổ sung hướng dẫn phân biệt bản tin giảm nhẹ tạm thời và bản tin đóng sự cố gốc", "TASK", "TODO", "2026-10-16", "STANDARD_FLOW"),
        ],
    }[pid]

    blueprints: list[dict[str, Any]] = []
    for idx, (title, ttype, st, s_date, cos) in enumerate(topics, start=1):
        bp: dict[str, Any] = {
            "title": title,
            "description": f"[{pid} / Kanban {cos}] {title}. Vận hành trên luồng Kanban liên tục không dùng Sprint (sprint_id=null), kiểm soát nghiêm ngặt giới hạn WIP và bằng chứng hậu kiểm.",
            "type": ttype,
            "status": st,
            "priority": "HIGH" if (cos in ("EXPEDITE_P0", "FIXED_DATE_SLA") or st == "BLOCKED") else ("LOW" if st == "CANCELLED" else "MEDIUM"),
            "start_date": s_date,
            "duration_days": 4 if st == "DONE" else 2,
            "sprint_id": None,  # Pure Kanban: sprint_id is always None
            "kanban_class_of_service": cos,
            "labels": ["kanban", pid.lower(), cos.lower()],
        }

        if pid == "CLD-INC":
            if idx == 8:
                bp["assignee_id"] = "CLD-U08"
                bp["handover_from_user_id"] = "CLD-U18"
                bp["handover_date"] = "2026-08-27"
                bp["updated_date"] = "2026-08-28"
                bp["disruption_id"] = "DIS-CLD-OFFBOARD-01"
                bp["handover_reason"] = "Kỹ sư SRE CLD-U18 nghỉ việc cuối ngày 2026-08-28; chuyển lịch trực lễ Quốc khánh sang cặp CLD-U07 / CLD-U08."
            elif idx == 9:
                # National Day 2026-09-02 SEV-0 Incident: detected by 24/7 bot, handled by Secondary On-Call CLD-U08
                bp["created_by"] = "CLD-U03"
                bp["assignee_id"] = "CLD-U08"
                bp["incident_id"] = "INC-2026-0902"
                bp["disruption_id"] = "DIS-CLD-STORM-01"
                bp["oncall_ts"] = {
                    "created_at": "2026-09-02T09:12:00+07:00",
                    "actor_type": "system_bot",
                    "work_mode": "automated_bot",
                    "is_overtime": False,
                    "in_progress_at": "2026-09-02T09:17:00+07:00",
                    "updated_at": "2026-09-02T09:46:00+07:00",
                    "updated_work_mode": "oncall_incident_response",
                    "updated_is_overtime": True,
                }
                bp["bot_comment"] = {
                    "bot_id": "CLD-BOT-HEARTBEAT",
                    "created_at": "2026-09-02T09:12:15+07:00",
                    "body": "[CLD-BOT-HEARTBEAT] Mất nhịp ping dịch vụ auth-token-verifier quá 180 giây; tự động mở cảnh báo SEV-0 INC-2026-0902 và kích hoạt lịch trực OC-2026-0902-HOLIDAY.",
                }
                bp["task_note"] = {
                    "author_id": "CLD-U08",
                    "created_at": "2026-09-02T09:46:00+07:00",
                    "work_mode": "oncall_incident_response",
                    "is_overtime": True,
                    "is_temporary_workaround": True,
                    "title": "[WORKAROUND TẠM THỜI] Giảm nhẹ bão kết nối lễ 02/09 (INC-2026-0902) trong ca trực Secondary",
                    "accomplishments": "Do Primary CLD-U07 mất kết nối vì mưa bão đứt cáp quang (DIS-CLD-STORM-01), Secondary CLD-U08 nhận leo thang lúc 09:17, ngắt các phiên báo cáo treo, điều hướng tạm sang read-replica và shelve cảnh báo lặp 120 phút.",
                    "approach": "Khôi phục nhanh luồng đăng nhập lúc 09:46+07:00 mà không thay đổi cấu trúc bảng trong ngày lễ.",
                    "reason": "CHỈ LÀ GIẢM NHẸ TẠM THỜI (temporary workaround, knowledge_eligible=false); khắc phục gốc bắt buộc thực hiện bằng tách pool PgBouncer tại CLDINF-19.",
                }
            elif idx == 10:
                bp["parent_seq"] = 9
                bp["assignee_id"] = "CLD-U08"
                bp["incident_id"] = "INC-2026-0902"
                bp["rework"] = True
                bp["updated_date"] = "2026-09-08"
                bp["rework_reason"] = "Bác bỏ giả thuyết lỗi CoreDNS ở dự thảo v1; cập nhật bằng chứng nghẽn pool PgBouncer theo review của VP CLD-U01."
            elif idx == 30:
                bp["transition_reason"] = "Ngừng sử dụng cổng SMS tĩnh đời cũ sau khi hoàn tất kiểm thử kênh thông báo đa phương thức có xác thực."
            elif idx == 31:
                bp["assignee_id"] = "CLD-U13"
                bp["transition_reason"] = "Đang chờ đội NOC đối tác VinaCloud gửi biên bản xác nhận định tuyến dự phòng BGP liên vùng."

        elif pid == "CLD-OBS":
            if idx == 19:
                bp["parent_seq"] = 8
                bp["assignee_id"] = "CLD-U12"
                bp["bot_comment"] = {
                    "bot_id": "CLD-BOT-HEARTBEAT",
                    "created_at": "2026-07-14T10:05:00+07:00",
                    "body": "[CLD-BOT-HEARTBEAT] Xác nhận kiểm thử: phát hiện mất ping đúng mốc 180 giây và đẩy sự kiện sang hàng đợi cảnh báo thành công.",
                }
            elif idx == 30:
                bp["transition_reason"] = "Tài liệu đề xuất DOC-CLDOBS-SLI-006 bị REJECTED do ngưỡng CPU > 65% trong 30 giây sinh 42% cảnh báo giả."
            elif idx == 31:
                bp["assignee_id"] = "CLD-U09"
                bp["transition_reason"] = "Chờ nhóm CLD-INF chốt danh mục nhãn mã rule WAF chuẩn sau khi hợp nhất module Terraform mới."

        elif pid == "CLD-INF":
            if idx == 4:
                bp["created_by"] = "CLD-U18"
                bp["assignee_id"] = "CLD-U18"
                bp["updated_date"] = "2026-06-09"
            elif idx == 9:
                # Evening On-Call Incident 2026-08-18 under OC-2026-0818-EVENING
                bp["created_by"] = "CLD-U05"
                bp["assignee_id"] = "CLD-U11"
                bp["incident_id"] = "INC-2026-0818"
                bp["oncall_ts"] = {
                    "created_at": "2026-08-18T19:10:00+07:00",
                    "actor_type": "system_bot",
                    "work_mode": "automated_bot",
                    "is_overtime": False,
                    "in_progress_at": "2026-08-18T19:14:00+07:00",
                    "updated_at": "2026-08-18T19:52:00+07:00",
                    "updated_work_mode": "oncall_incident_response",
                    "updated_is_overtime": True,
                }
                bp["bot_comment"] = {
                    "bot_id": "CLD-BOT-ALERTGROUP",
                    "created_at": "2026-08-18T19:10:20+07:00",
                    "body": "[CLD-BOT-ALERTGROUP] Gom 312 lỗi SQLSTATE 42804 trên pod phiên bản cũ thành nhóm sự cố INC-2026-0818 (SEV-1).",
                }
            elif idx == 19:
                bp["assignee_id"] = "CLD-U11"
                bp["incident_id"] = "INC-2026-0902"
                bp["is_overtime"] = True
                bp["updated_date"] = "2026-09-14"
                bp["task_note"] = {
                    "title": "[KHẮC PHỤC GỐC INC-2026-0902] Tách biệt hoàn toàn auth_pool và reporting_pool trên PgBouncer",
                    "accomplishments": "Đã tách cấu hình PgBouncer thành auth_pool (60 kết nối, statement_timeout=3000ms) trên Primary và reporting_pool (25 kết nối) trỏ sang Read-Replica theo DOC-CLDINF-DB-002 v2.",
                    "approach": "Thay thế triệt để workaround tạm thời hôm lễ 02/09 (CLDINC-9) bằng cô lập tài nguyên ở tầng connection pooler.",
                    "reason": "Ngăn chặn vĩnh viễn việc truy vấn báo cáo nặng làm cạn kiệt kết nối của luồng xác thực đa tenant.",
                }
            elif idx == 20:
                bp["parent_seq"] = 19
                bp["assignee_id"] = "CLD-U16"
                bp["incident_id"] = "INC-2026-0902"
                bp["disruption_id"] = "DIS-CLD-SICK-01"
                bp["handover_from_user_id"] = "CLD-U11"
                bp["handover_date"] = "2026-09-16"
                bp["updated_date"] = "2026-09-18"
                bp["handover_reason"] = "CLD-U11 nghỉ ốm viêm phế quản 16–17/09/2026 (DIS-CLD-SICK-01); bàn giao kiểm thử tải sang CLD-U16 để tránh nghẽn WIP."
                bp["task_note"] = {
                    "title": "Bàn giao nghỉ ốm DIS-CLD-SICK-01: Kết quả kiểm thử bão hòa reporting_pool",
                    "accomplishments": "Mai Xuân Trường (CLD-U16) chạy mô phỏng 200 truy vấn báo cáo nặng; auth_pool vẫn đạt 100% thành công với P99 = 38ms.",
                    "approach": "Thực thi kịch bản k6 chuẩn và ghi nhận báo cáo chính thức tại DOC-CLDINF-TST-005.",
                    "reason": "Đảm bảo đóng đúng hạn hành động phòng ngừa cốt lõi của sự cố INC-2026-0902 khi kỹ sư CSDL chính nghỉ ốm.",
                }
            elif idx == 23:
                # Saturday Weekend Incident 2026-09-26 under OC-2026-0926-SATURDAY
                bp["created_by"] = "CLD-U05"
                bp["assignee_id"] = "CLD-U10"
                bp["incident_id"] = "INC-2026-0926"
                bp["oncall_ts"] = {
                    "created_at": "2026-09-26T14:05:00+07:00",
                    "actor_type": "system_bot",
                    "work_mode": "automated_bot",
                    "is_overtime": False,
                    "in_progress_at": "2026-09-26T14:12:00+07:00",
                    "updated_at": "2026-09-26T14:55:00+07:00",
                    "updated_work_mode": "weekend_incident_ot",
                    "updated_is_overtime": True,
                }
                bp["bot_comment"] = {
                    "bot_id": "CLD-BOT-TF-DRIFT",
                    "created_at": "2026-09-26T14:05:30+07:00",
                    "body": "[CLD-BOT-TF-DRIFT] Phát hiện rule WAF thủ công ngoài Terraform state gây tăng đột biến HTTP 403 trên đường dẫn webhook đối tác.",
                }
                bp["task_note"] = {
                    "author_id": "CLD-U10",
                    "created_at": "2026-09-26T14:55:00+07:00",
                    "work_mode": "weekend_incident_ot",
                    "is_overtime": True,
                    "is_temporary_workaround": True,
                    "title": "[GIẢM NHẸ CA TRỰC THỨ BẢY] Gỡ rule WAF sửa tay chặn nhầm webhook FinLedger (INC-2026-0926)",
                    "accomplishments": "Đặng Anh Quân (CLD-U10, trực chính OC-2026-0926-SATURDAY) xác minh chữ ký HMAC hợp lệ và gỡ rule chặn tay lúc 14:55+07:00.",
                    "approach": "Khôi phục lưu lượng tức thời cho khách hàng; mở tiếp task CLDINF-24 để khóa quyền sửa tay bằng Terraform.",
                    "reason": "Xử lý khẩn cấp trong ca trực cuối tuần; bản sửa quản trị vĩnh viễn theo dõi tại CLDINF-24.",
                }
            elif idx == 24:
                bp["assignee_id"] = "CLD-U16"
                bp["incident_id"] = "INC-2026-0926"
                bp["updated_date"] = "2026-10-14"
            elif idx == 25:
                bp["parent_seq"] = 24
                bp["assignee_id"] = "CLD-U10"
            elif idx == 30:
                bp["transition_reason"] = "Bị hủy vì vi phạm nguyên tắc đặc quyền tối thiểu và cô lập pool kết nối tại DOC-CLDINF-DB-002."

        elif pid == "CLD-SUP":
            if idx == 22:
                bp["parent_seq"] = 21
                bp["assignee_id"] = "CLD-U15"
            elif idx == 30:
                bp["transition_reason"] = "Đóng kênh email chia sẻ không xác thực để bắt buộc gửi yêu cầu qua cổng hỗ trợ có kiểm tra quyền tenant."
            elif idx == 31:
                bp["assignee_id"] = "CLD-U15"
                bp["transition_reason"] = "Đang chờ Quản lý vận hành phía khách hàng FinLedger ký xác nhận biên bản đối soát tín dụng SLA quý 3."

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
        bps = _make_kanban_project_blueprints(pid)
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

    doc_specs = build_cloudops_doc_specs(task_id_by_key)
    project_docs, doc_versions = render_project_documents_and_versions(
        pkg_root=PKG_ROOT,
        namespace=NAMESPACE,
        org_id=PRIMARY_ORG_ID,
        org_banner="CLOUDOPS SERVICES  •  KANBAN 24/7 SRE & INCIDENT RELAY",
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

    eval_cases = build_cloudops_eval_cases(make_eval_case, AS_OF_DATE, task_id_by_key, note_id_by_key)

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
            "overtime_hours": "17:00-22:00 (plus scheduled 24/7 On-Call & System Bots)",
        },
        "organizations": orgs,
        "users": users,
        "organization_memberships": org_mems,
        "role_assignments": role_assigns,
        "projects": projects,
        "project_memberships": proj_mems,
        "sprints": [],  # Pure Kanban: zero sprints
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

    readme_md = f"""# Organization 3 — CloudOps Services: Vận Hành SaaS 24/7, Hỗ Trợ Tier-3 & Điều Phối Sự Cố (Kanban)

**Trạng thái:** Hoàn thành bộ dataset synthetic kiểm chứng được (`v1.0.0`, `as_of_date = {AS_OF_DATE}`); tái tạo 100% bằng `python -X utf8 -B Dataset/Organization3-CloudOps-Services/tools/generate_org.py`. Chưa seed MongoDB runtime của Continuum.

## 1. Bối cảnh nghiệp vụ & Phương pháp quản lý Kanban
- **Tổ chức chính (`ORG-CLD`)**: Đơn vị vận hành SRE, giám sát SLO và hỗ trợ kỹ thuật Tier-3 đa tenant (kèm tenant khách hàng doanh nghiệp `ORG-FINLEDGER` và đối tác hạ tầng thượng nguồn `ORG-VINACLOUD` phục vụ kiểm thử cách ly đa tenant).
- **Phương pháp chủ đạo**: **Kanban liên tục** (`methodology = "KANBAN"`, `sprints = []`, `sprint_id = null` trên toàn bộ `{len(all_tasks)}` task), điều tiết bằng giới hạn WIP, SLE và các làn ưu tiên `EXPEDITE_P0` / `FIXED_DATE_SLA` / `STANDARD_FLOW` (`structured/kanban_wip_policies.jsonl`).
- **Tình huống thực tế nổi bật**:
  1. **Sự cố SEV-0 ngày lễ Quốc khánh `02/09/2026` (`INC-2026-0902`)**: Bot 24/7 `CLD-BOT-HEARTBEAT` phát hiện mất nhịp lúc `09:12+07:00`; Primary On-Call `CLD-U07` bị đứt cáp quang mưa bão (`DIS-CLD-STORM-01`) nên tự động leo thang sang Secondary `CLD-U08` lúc `09:17+07:00`. Tách bạch rõ **workaround tạm thời** (`CLDINC-9`, `is_temporary_workaround=true`) với **bản sửa nguyên nhân gốc** tách pool `PgBouncer` (`CLDINF-19`, `DOC-CLDINC-RCA-002` v2 bác bỏ giả thuyết DNS sai ở v1).
  2. **Sự cố lệch cấu hình WAF chiều Thứ Bảy `26/09/2026` (`INC-2026-0926`)**: Bot `CLD-BOT-TF-DRIFT` phát hiện rule sửa tay chặn nhầm webhook `FinLedger`; ca trực cuối tuần `CLD-U10` gỡ chặn khẩn cấp (`CLDINF-23`), Tier-3 hướng dẫn replay 148 sự kiện idempotent (`CLDSUP-21`) và khóa sửa tay bằng Terraform (`CLDINF-24`, `DOC-CLDINF-ARC-001` v2).
  3. **Lưu trữ Runbook lỗi & Bàn giao nhân sự**: Lưu trữ `DOC-CLDINF-RUN-006-LEGACY` (`ARCHIVED`) sau sự cố `INC-2026-0818` để thay bằng chuẩn Expand/Contract (`DOC-CLDINF-DB-002` v2); `CLD-U18` nghỉ việc ngày `2026-08-28`; `CLD-U16` nhận bàn giao kiểm thử tải khi `CLD-U11` nghỉ ốm (`DIS-CLD-SICK-01`).

## 2. Nguồn tham chiếu GitHub & Giới hạn bản quyền
- Tham khảo khái niệm nghiệp vụ từ `roxy-wi/IncidentRelay` (tag `v2.4.0`, commit `21ea27d92927242ed499b7584a276f47cb1c68cd`, giấy phép **`Elastic-2.0` — source-available, không phải OSI open-source**, issues `#127`, `#128`, `#130`) và danh mục cấu trúc phân tích sự cố `danluu/post-mortems` (`master` commit `630562e55281ff28961704e8042a7dc9569a96e7`, không có file LICENSE chung).
- **Tuyệt đối không sao chép** mã nguồn, tài liệu hay nội dung chịu điều khoản `Elastic-2.0` hoặc bài postmortem bên thứ ba; không khẳng định IncidentRelay dùng Kanban. Chi tiết tại [../GITHUB_SOURCES_AND_LICENSES.md](../GITHUB_SOURCES_AND_LICENSES.md).

## 3. Phạm vi Continuum đã chốt & Quy mô gói dữ liệu
- **Không có Team / Không có lịch sử AI Chat / Không có entity Notebook thứ tư**.
- **Đủ 3 dạng Group Note**: `{len(all_notes)}` `TASK_NOTE` (`knowledge_eligible=false`), `{len(project_docs)}` `PROJECT_DOCUMENT` (`{len(doc_versions)}` versions, kèm 6 file DOCX), `{len(work_reports)}` `WORK_REPORT` (`DAILY` & `WEEKLY`, `MEMBER` & `LEADER`).
- **Evaluation**: `{len(eval_cases)}` benchmark cases trong `evaluation/benchmark_cases.jsonl` (`review_status = "unreviewed"` / `"chưa duyệt"`).
"""

    ic_md = f"""# Ingestion Contract — Organization 3: CloudOps Services (Kanban v1.0.0)

1. **Tenant & Multi-Tenant Isolation**: Chỉ nạp `ORG-CLD` làm tenant vận hành chính; `ORG-FINLEDGER` và `ORG-VINACLOUD` là tổ chức bên ngoài dùng để kiểm chứng rào cản phân quyền đa tenant (`DENY`).
2. **Kanban Constraint**: `structured/sprints.jsonl` rỗng (`[]`) và toàn bộ `{len(all_tasks)}` task có `sprint_id = null`. Chính sách giới hạn WIP, lịch trực ca và danh mục bot 24/7 lưu tại `structured/kanban_wip_policies.jsonl`, `structured/oncall_schedules.jsonl`, `structured/incidents.jsonl` và `structured/system_bots.jsonl`.
3. **24/7 Bot vs Lịch làm việc con người**:
   - Con người trong ngày thường chỉ hoạt động `08:00–12:00`, `13:00–17:00` và OT tối `17:00–22:00+07:00` (cấm `12:00–13:00`).
   - Hoạt động của con người vào tối muộn, cuối tuần hoặc ngày lễ Quốc khánh `02/09` bắt buộc có `work_mode` thuộc `oncall_incident_response` / `weekend_incident_ot` và nằm trong khung lịch trực hợp lệ tại `structured/oncall_schedules.jsonl`.
   - Sự kiện tự động của bot dùng `actor_type = "system_bot"` và `work_mode = "automated_bot"`.
4. **Ba dạng Group Note & Chống nhầm Workaround**: Task Note luôn có `knowledge_eligible = false` (đặc biệt các Task Note gắn `is_temporary_workaround = true` không bao giờ được coi là bản sửa gốc). Chỉ phiên bản `APPROVED` mới nhất của Project Document không bị `ARCHIVED` và các Work Report `APPROVED` mới có `knowledge_eligible = true`.
5. **Tách biệt Evaluation & Fixtures**: Không nạp `evaluation/benchmark_cases.jsonl` và `fixtures/negative_cases.json` vào database ứng dụng.
"""

    manifest = materialize_organization_package(
        pkg_root=PKG_ROOT,
        namespace=NAMESPACE,
        dataset_id="continuum-org3-cloudops-kanban-v1",
        version="1.0.0",
        org_display_name="CloudOps Services (24/7 SaaS Operations & Incident Relay)",
        methodology_label="KANBAN",
        bundle=bundle,
        extra_structured_files={
            "structured/incidents.jsonl": INCIDENT_RECORDS,
            "structured/kanban_wip_policies.jsonl": KANBAN_WIP_POLICIES,
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
        f"[ORG-3 CLOUDOPS] Generated successfully: {manifest['canonical_counts']['physical_files_total']} files, "
        f"{len(all_tasks)} tasks, {len(all_notes)} task notes, {len(project_docs)} docs, "
        f"{len(work_reports)} reports, {len(eval_cases)} eval cases."
    )


if __name__ == "__main__":
    main()
