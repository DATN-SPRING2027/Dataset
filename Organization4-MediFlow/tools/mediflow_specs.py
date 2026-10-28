"""Bespoke Hybrid (Milestone + Sprint) administrative clinic specifications for Organization 4 — MediFlow."""

from __future__ import annotations

NAMESPACE = "mediflow"
PRIMARY_ORG_ID = "ORG-MED"
SIM_START = "2026-04-20"
AS_OF_DATE = "2026-10-16"

ORG_SPECS = [
    ("ORG-MED", "MediFlow HealthTech Co., Ltd.", "product_healthtech_vendor", "mediflow.invalid", "ENTERPRISE"),
    ("ORG-ANKHANG", "An Khang Outpatient Clinic (Synthetic Pilot Partner)", "pilot_clinic_partner", "ankhangclinic.invalid", "FREE"),
    ("ORG-VIETNOTIFY", "VietNotify Messaging Gateway (Synthetic Partner)", "messaging_gateway_vendor", "vietnotify.invalid", "FREE"),
]

ORG_ADMIN_IDS = {"MED-U01", "MED-U02"}

USER_SPECS = [
    ("MED-U01", "Nguyễn Hoàng Nam", "ORG-MED", "Product & Delivery", "Head of Engineering & Clinic Delivery (Org Manager)", "2025-03-10", None),
    ("MED-U02", "Lê Minh Thư", "ORG-MED", "Product Management", "Principal Product & Privacy Governance Manager (Org Manager)", "2025-04-01", None),
    ("MED-U03", "Trần Quốc Khánh", "ORG-MED", "Patient Registration", "Tech Lead — Administrative Registration & Identity", "2025-05-05", None),
    ("MED-U04", "Phạm Thu Thủy", "ORG-MED", "Appointment Engine", "Tech Lead — Doctor Schedules & Appointment Booking", "2025-05-19", None),
    ("MED-U05", "Võ Tuấn Kiệt", "ORG-MED", "Reception & Admin Ops", "Tech Lead — Reception Queue & Admin Reporting", "2025-06-02", None),
    ("MED-U06", "Đặng Bảo Châu", "ORG-MED", "Pilot & Implementation", "Lead Pilot Integration & Clinic Training", "2025-06-16", None),
    ("MED-U07", "Hoàng Minh Quân", "ORG-MED", "Product Analysis", "Senior Healthcare Admin BA", "2025-07-01", None),
    ("MED-U08", "Bùi Phương Linh", "ORG-MED", "Patient Registration", "Senior Backend Engineer (Registration & Dedup)", "2025-07-15", None),
    ("MED-U09", "Ngô Gia Hân", "ORG-MED", "Patient Registration", "Frontend Engineer (Reception Desk UI)", "2025-08-04", None),
    ("MED-U10", "Đỗ Anh Tuấn", "ORG-MED", "Appointment Engine", "Backend Engineer (Slot Locking & Shifts)", "2025-08-18", None),
    ("MED-U11", "Trịnh Thanh Tùng", "ORG-MED", "Appointment Engine", "Backend Engineer (Reschedule & Notification Hooks)", "2025-09-03", None),
    ("MED-U12", "Lý Khánh Vy", "ORG-MED", "Appointment Engine", "Frontend Engineer (Calendar & Walk-In Board)", "2025-09-15", None),
    ("MED-U13", "Phan Quốc Huy", "ORG-MED", "Reception & Admin Ops", "Backend Engineer (Queue & RBAC Audit)", "2025-10-01", None),
    ("MED-U14", "Vương Thảo Nhi", "ORG-MED", "Reception & Admin Ops", "Data Protection & Admin Export Engineer", "2025-10-20", None),
    ("MED-U15", "Hồ Minh Triết", "ORG-MED", "Quality Assurance", "Senior QA Automation Engineer", "2025-11-10", None),
    ("MED-U16", "Mai Tuấn Anh", "ORG-MED", "Pilot & Implementation", "DevOps & Pilot Cutover Engineer", "2025-12-01", None),
    ("MED-U17", "Đinh Ngọc Ánh", "ORG-MED", "Quality Assurance", "Pilot UAT & Privacy Compliance Tester", "2026-01-12", None),
    ("MED-U18", "Tạ Quang Minh", "ORG-MED", "Reception & Admin Ops", "Former Frontend Engineer (Offboarded)", "2025-06-15", "2026-08-21"),
    ("AK-U01", "Nguyễn Thị Mai", "ORG-ANKHANG", "Clinic Operations", "An Khang Clinic Operations Manager (Synthetic)", "2026-04-20", None),
    ("AK-U02", "Trần Văn Hòa", "ORG-ANKHANG", "Reception Desk", "Lead Clinic Receptionist (Synthetic)", "2026-04-20", None),
    ("AK-U03", "Phạm Minh Đức", "ORG-ANKHANG", "Clinic IT", "An Khang Local Network Coordinator (Synthetic)", "2026-04-20", None),
    ("VN-U01", "Lương Quốc Việt", "ORG-VIETNOTIFY", "Partner Integration", "VietNotify Webhook Support Engineer (Synthetic)", "2026-04-20", None),
]

SYSTEM_BOTS = [
    {"bot_id": "MED-BOT-NOTIFY-PROBE", "name": "Appointment Reminder Callback Synthetic Probe", "schedule": "24x7_every_15m", "organization_id": "ORG-MED"},
]

PROJECT_SPECS = [
    {
        "project_id": "MED-REG",
        "code": "MEDREG",
        "name": "Hồ Sơ Hành Chính Người Khám Giả Lập & Chống Trùng Lặp Đăng Ký",
        "description": "Dự án Hybrid (Milestone + Sprint 2 tuần) xây dựng đăng ký hành chính, định danh giả lập AK-PAT-XXXXXX và che mặt nạ thông tin liên lạc (không lưu bệnh án lâm sàng).",
        "methodology": "HYBRID",
        "created_by": "MED-U01",
        "leader_id": "MED-U03",
        "member_ids": ["MED-U07", "MED-U08", "MED-U09", "MED-U15"],
        "former_member_ids": ["MED-U18"],
        "start_date": "2026-04-20",
        "target_date": "2026-10-30",
    },
    {
        "project_id": "MED-APT",
        "code": "MEDAPT",
        "name": "Quản Lý Lịch Làm Việc Bác Sĩ, Đặt Lịch Hẹn & Dời Lịch Theo Quyền Lễ Tân",
        "description": "Dự án Hybrid quản lý ca trực phòng khám, khóa slot chống đặt trùng và xử lý dời lịch hàng loạt có kiểm toán.",
        "methodology": "HYBRID",
        "created_by": "MED-U01",
        "leader_id": "MED-U04",
        "member_ids": ["MED-U07", "MED-U10", "MED-U11", "MED-U12", "MED-U15"],
        "former_member_ids": [],
        "start_date": "2026-04-20",
        "target_date": "2026-10-30",
    },
    {
        "project_id": "MED-ADM",
        "code": "MEDADM",
        "name": "Hàng Đợi Tiếp Đón Quầy Lễ Tân, Phân Quyền Vai Trò & Báo Cáo Hành Chính",
        "description": "Dự án Hybrid quản lý trạng thái tiếp đón (Scheduled/WalkIn -> CheckedIn -> Completed/Missed) và kiểm soát xuất dữ liệu không lộ SĐT.",
        "methodology": "HYBRID",
        "created_by": "MED-U02",
        "leader_id": "MED-U05",
        "member_ids": ["MED-U09", "MED-U13", "MED-U14", "MED-U17"],
        "former_member_ids": ["MED-U18"],
        "start_date": "2026-04-20",
        "target_date": "2026-10-30",
    },
    {
        "project_id": "MED-PIL",
        "code": "MEDPIL",
        "name": "Triển Khai Pilot Phòng Khám Đa Khoa An Khang, Đào Tạo & Nghiệm Thu Vận Hành",
        "description": "Dự án điều phối triển khai Pilot theo cổng Milestone (không chia Sprint nội bộ, sprint_id=null), tích hợp cổng nhắc lịch giả lập VietNotify và nghiệm thu thực địa.",
        "methodology": "WATERFALL",
        "created_by": "MED-U02",
        "leader_id": "MED-U06",
        "member_ids": ["MED-U07", "MED-U14", "MED-U16", "MED-U17"],
        "former_member_ids": [],
        "start_date": "2026-05-04",
        "target_date": "2026-10-30",
    },
]

MILESTONE_RECORDS = [
    {"milestone_id": "MS-MED-01", "organization_id": "ORG-MED", "name": "M1 — Chốt Phạm Vi Hành Chính & Ranh Giới Phi Lâm Sàng", "target_date": "2026-06-12", "actual_date": "2026-06-12", "status": "COMPLETED", "approved_by": "MED-U02", "linked_sprints": [], "summary": "Chốt phạm vi 100% hành chính lịch hẹn và tiếp đón; loại trừ hoàn toàn hồ sơ bệnh án lâm sàng, đơn thuốc và xét nghiệm."},
    {"milestone_id": "MS-MED-02", "organization_id": "ORG-MED", "name": "M2 — Demo Phòng Khám An Khang Đợt 1 & Phân Loại Phản Hồi", "target_date": "2026-08-28", "actual_date": "2026-08-28", "status": "COMPLETED", "approved_by": "MED-U01", "linked_sprints": ["S1", "S2"], "summary": "Hoàn thành Demo Sprint 1–2; tiếp nhận phản hồi CFB-2026-01 (duyệt lễ tân dời lịch hộ có kiểm toán) và bác bỏ CFB-2026-02 (từ chối xuất Excel lộ SĐT)."},
    {"milestone_id": "MS-MED-03", "organization_id": "ORG-MED", "name": "M3 — Vận Hành Thử Nghiệm (Pilot Readiness) Tại Quầy Tiếp Đón", "target_date": "2026-10-08", "actual_date": "2026-10-12", "status": "COMPLETED_WITH_DELAY", "approved_by": "MED-U01", "linked_sprints": ["S3", "S4"], "summary": "Lùi 2 ngày làm việc từ 08/10 sang 12/10 do mưa bão mất mạng cuối Sprint 4 (DIS-MED-STORM-01) và chờ cổng nhắc lịch đối tác VietNotify xác nhận mẫu tin."},
    {"milestone_id": "MS-MED-04", "organization_id": "ORG-MED", "name": "M4 — Đánh Giá Sau Pilot & Nghiệm Thu Giai Đoạn 1", "target_date": "2026-10-30", "actual_date": None, "status": "IN_PROGRESS", "approved_by": None, "linked_sprints": ["S5"], "summary": "Đang hoàn tất các hạng mục spillover tại Sprint 5 (2026-10-05..2026-10-16) và đối soát điều kiện nghiệm thu Pilot."},
]

SPRINT_WINDOWS = [
    ("S1", "Sprint 1 — Nền Tảng Định Danh Hành Chính & Khung Ca Trực", "COMPLETED", "2026-08-10", "2026-08-21", "MS-MED-02"),
    ("S2", "Sprint 2 — Đặt Lịch Hẹn, Hàng Đợi Tiếp Đón & Chuẩn Bị Demo M2", "COMPLETED", "2026-08-24", "2026-09-04", "MS-MED-02"),
    ("S3", "Sprint 3 — Khóa Chống Đặt Trùng Slot & Quyền Lễ Tân Dời Lịch Hộ", "COMPLETED", "2026-09-07", "2026-09-18", "MS-MED-03"),
    ("S4", "Sprint 4 — Tích Hợp Nhắc Lịch Hành Chính & Kiểm Thử Trước Pilot", "COMPLETED", "2026-09-21", "2026-10-02", "MS-MED-03"),
    ("S5", "Sprint 5 — Xử Lý Spillover Sau Mưa Bão & Tinh Chỉnh Pilot M4", "ACTIVE", "2026-10-05", "2026-10-16", "MS-MED-04"),
]

CLINIC_FEEDBACK_LOG = [
    {
        "feedback_id": "CFB-2026-01",
        "milestone_id": "MS-MED-02",
        "submitted_by_partner": "AK-U02",
        "submitted_at": "2026-08-28T10:30:00+07:00",
        "topic": "Đề nghị cho phép Lễ tân trưởng dời lịch hẹn hàng loạt thay người khám khi lịch trực bác sĩ thay đổi đột xuất.",
        "decision_status": "APPROVED_INTO_BACKLOG",
        "decided_by": "MED-U02",
        "decided_at": "2026-08-31T14:30:00+07:00",
        "impact_summary": "Chấp thuận bổ sung quyền RECEPTION_SHIFT_LEAD dời lịch hộ kèm bắt buộc nhập reschedule_reason, lưu vết audit_log và gửi thông báo qua VietNotify (triển khai tại MEDAPT-18, MEDAPT-19 trong Sprint 3–4; cập nhật DOC-MEDAPT-REQ-001 v2 & DOC-MEDAPT-API-003 v2).",
    },
    {
        "feedback_id": "CFB-2026-02",
        "milestone_id": "MS-MED-02",
        "submitted_by_partner": "AK-U01",
        "submitted_at": "2026-08-28T11:00:00+07:00",
        "topic": "Đề nghị cho phép xuất file Excel danh sách lịch hẹn tuần kèm đầy đủ số điện thoại không che mặt nạ để gọi điện thủ công.",
        "decision_status": "REJECTED_PRIVACY_RISK",
        "decided_by": "MED-U02",
        "decided_at": "2026-09-03T15:00:00+07:00",
        "impact_summary": "Từ chối tại DOC-MEDADM-EXPORT-006 (REJECTED) và hủy task MEDADM-30 (CANCELLED); giữ cứng cờ include_phone_in_excel_export = false để chống rò rỉ dữ liệu liên lạc hành chính.",
    },
    {
        "feedback_id": "CFB-2026-03",
        "milestone_id": "MS-MED-04",
        "submitted_by_partner": "AK-U01",
        "submitted_at": "2026-10-13T09:45:00+07:00",
        "topic": "Phản hồi thử nghiệm Pilot: đề xuất tự động khóa quyền đặt lịch trực tuyến 30 ngày nếu vắng mặt (Missed) 2 lần liên tiếp.",
        "decision_status": "PENDING_EVALUATION",
        "decided_by": None,
        "decided_at": None,
        "impact_summary": "Mới là phản hồi chưa phê duyệt (đang ghi nhận tại bản nháp DOC-MEDAPT-DES-005 v2 PENDING_REVIEW); tuyệt đối chưa có hiệu lực áp dụng trên môi trường Pilot.",
    },
]

ONCALL_SCHEDULES = [
    {
        "schedule_id": "OC-MED-PILOT-SAT-1010",
        "organization_id": "ORG-MED",
        "rotation_name": "Saturday Pilot Cutover & Reception Kiosk Rehearsal Duty",
        "primary_user_id": "MED-U06",
        "secondary_user_id": "MED-U16",
        "start_at": "2026-10-10T08:00:00+07:00",
        "end_at": "2026-10-10T18:00:00+07:00",
        "override_note": "Ca trực triển khai hạ tầng Pilot Thứ Bảy 10/10/2026 ngoài giờ cao điểm đón khách của phòng khám An Khang.",
    }
]

DISRUPTION_EVENTS = [
    {
        "disruption_id": "DIS-MED-OFFBOARD-01",
        "organization_id": "ORG-MED",
        "project_id": "MED-ADM",
        "kind": "employee_offboarding",
        "affected_user_id": "MED-U18",
        "backup_user_id": "MED-U09",
        "unavailable_from": "2026-08-22T00:00:00+07:00",
        "unavailable_to": "2026-12-31T23:59:59+07:00",
        "cause": "Kỹ sư Frontend Tạ Quang Minh (MED-U18) hoàn tất bàn giao cuối Sprint 1 và nghỉ việc từ hết ngày 2026-08-21.",
        "impact": "Các màn hình bảng hàng đợi quầy tiếp đón trong Sprint 2 cần người phụ trách thay thế.",
        "resolution": "Bàn giao sang Ngô Gia Hân (MED-U09) và thu hồi toàn bộ quyền truy cập ORG-MED ngày 21/08/2026.",
    },
    {
        "disruption_id": "DIS-MED-SICK-01",
        "organization_id": "ORG-MED",
        "project_id": "MED-APT",
        "kind": "sick_leave",
        "affected_user_id": "MED-U10",
        "backup_user_id": "MED-U11",
        "unavailable_from": "2026-09-10T08:00:00+07:00",
        "unavailable_to": "2026-09-11T22:00:00+07:00",
        "cause": "Kỹ sư Backend Đỗ Anh Tuấn (MED-U10) nghỉ phép ốm có xác nhận hành chính trong 2 ngày 10–11/09/2026 giữa Sprint 3.",
        "impact": "Nguy cơ trễ kiểm thử tương tranh khóa slot đặt lịch hẹn (MEDAPT-14) trước khi đóng Sprint 3.",
        "resolution": "Tech Lead MED-U04 chuyển giao subtask kiểm thử khóa tương tranh MEDAPT-15 sang Trịnh Thanh Tùng (MED-U11).",
    },
    {
        "disruption_id": "DIS-MED-STORM-01",
        "organization_id": "ORG-MED",
        "project_id": "MED-APT",
        "kind": "storm_network_disruption",
        "affected_user_id": "MED-U15",
        "backup_user_id": "MED-U17",
        "unavailable_from": "2026-09-28T08:00:00+07:00",
        "unavailable_to": "2026-09-29T22:00:00+07:00",
        "cause": "Mưa lớn ngập tuyến đường và đứt cáp viễn thông khu vực cư trú của QA Hồ Minh Triết (MED-U15) ngày 28–29/09/2026 cuối Sprint 4.",
        "impact": "Không kịp chạy hết bộ kiểm thử tự động dời lịch hàng loạt trong Sprint 4, làm hạng mục MEDAPT-25 phải spillover sang Sprint 5 và lùi mốc sẵn sàng Pilot MS-MED-03 từ 08/10 sang 12/10.",
        "resolution": "Chuyển tiếp chính thức MEDAPT-25 từ MEDAPT-S4 sang MEDAPT-S5 (spillover_count=1) và huy động MED-U17 hỗ trợ kiểm thử bù.",
    },
]

SOURCE_ATTRIBUTION = [
    {
        "repo_url": "https://github.com/openmrs/openmrs-core",
        "repo_name": "openmrs/openmrs-core",
        "selected_release_or_tag": "2.8.10 (master reference)",
        "commit_sha": "0755f785f7d237a7a2e9d9f4e76aff43b7613ad3",
        "accessed_at": "2026-10-28T08:17:08+07:00",
        "license": "MPL-2.0 with OpenMRS Public License Exhibit B (Healthcare Disclaimer)",
        "inspected_artifacts": [
            "LICENSE & README.md (verified MPL-2.0 + Healthcare Disclaimer)",
            "api/src/main/java/org/openmrs/ (administrative domain boundaries: Person, PatientIdentifier, Provider, Location, Visit, Role, Privilege)",
            "Public PR/issue activity (#6758)",
        ],
        "usage_boundary": "Chỉ tham khảo cách tách biệt định danh hành chính, địa điểm phòng khám, ca làm việc và phân quyền vai trò; loại trừ hoàn toàn các thực thể lâm sàng và tuyệt đối không sao chép mã nguồn Java/XML hay dữ liệu của OpenMRS. Không khẳng định OpenMRS dùng mô hình Hybrid.",
    },
    {
        "repo_url": "https://github.com/openmrs/openmrs-contrib-o3-docs/blob/main/content/en-US/docs/configure-o3/configure-patient-management.mdx",
        "repo_name": "openmrs/openmrs-contrib-o3-docs",
        "selected_release_or_tag": "main",
        "commit_sha": "3a0da981e31e224a467a4432df2a65cb8dfdfe7b",
        "accessed_at": "2026-10-28T08:17:08+07:00",
        "license": "MPL-2.0",
        "inspected_artifacts": [
            "LICENSE",
            "content/en-US/docs/configure-o3/configure-patient-management.mdx (configurable registration sections, appointment lifecycle statuses Scheduled/CheckedIn/Completed/Cancelled/Missed, reception queues, and privacy option includePhoneNumberInExcelSpreadsheet: false)",
        ],
        "usage_boundary": "Tham khảo khái niệm vòng đời trạng thái lịch hẹn hành chính và ý tưởng cấu hình ẩn số điện thoại khi xuất bảng tính để tự thiết kế kịch bản synthetic CFB-2026-02 độc lập bằng tiếng Việt.",
    },
]

IMPLEMENTATION_ASSUMPTIONS = [
    "Giả định triển khai (Implementation Assumption): MediFlow gồm 3 dự án sản phẩm vận hành theo Hybrid (MED-REG, MED-APT, MED-ADM: kết hợp 4 cổng Milestone MS-MED-01..04 với 5 Sprint 2 tuần) và 1 dự án triển khai thực địa vận hành theo Milestone không dùng Sprint (MED-PIL, methodology=WATERFALL, sprint_id=null), thể hiện đúng nguyên tắc phương pháp quản lý thuộc về từng project.",
    "Giả định triển khai (Implementation Assumption): 100% dữ liệu trong MediFlow và phòng khám đối tác An Khang là dữ liệu hành chính giả lập (lịch hẹn, ca bác sĩ, hàng đợi tiếp đón); không chứa bất kỳ thông tin lâm sàng, chẩn đoán, xét nghiệm hay đơn thuốc nào.",
]
