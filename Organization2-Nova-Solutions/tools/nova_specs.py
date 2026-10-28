"""Bespoke Waterfall domain specifications for Organization 2 — Nova Solutions (HR, Attendance & Leave)."""

from __future__ import annotations

NAMESPACE = "nova"
PRIMARY_ORG_ID = "ORG-NOVA"
SIM_START = "2026-04-16"
AS_OF_DATE = "2026-10-16"

ORG_SPECS = [
    ("ORG-NOVA", "Nova Solutions Co., Ltd.", "software_outsourcing_vendor", "novasolutions.invalid", "ENTERPRISE"),
    ("ORG-MINHPHAT", "Minh Phát Manufacturing & Distribution Corp", "client_enterprise_300_staff", "minhphatcorp.invalid", "FREE"),
]

# Explicit Continuum Organization ADMIN (Manager) roles in ORG-NOVA
ORG_ADMIN_IDS = {"NV-U01", "NV-U02"}

USER_SPECS = [
    ("NV-U01", "Trần Quốc Bảo", "ORG-NOVA", "Delivery Management", "Delivery Director (Org Manager)", "2025-06-02", None),
    ("NV-U02", "Lê Thu Hà", "ORG-NOVA", "PMO & Quality", "Senior Project Manager (Org Manager)", "2025-07-01", None),
    ("NV-U03", "Phạm Minh Tuấn", "ORG-NOVA", "HR Core Squad", "Tech Lead — Core HR", "2025-08-11", None),
    ("NV-U04", "Nguyễn Hoàng Nam", "ORG-NOVA", "Attendance Squad", "Tech Lead — Time & Attendance", "2025-08-11", None),
    ("NV-U05", "Võ Thị Thanh Tâm", "ORG-NOVA", "Leave Workflow Squad", "Tech Lead — Leave & Accrual", "2025-09-01", None),
    ("NV-U06", "Đặng Gia Huy", "ORG-NOVA", "Data Migration & UAT", "Tech Lead — Data Migration & Cutover", "2025-09-15", None),
    ("NV-U07", "Bùi Khánh Linh", "ORG-NOVA", "Business Analysis", "Lead Business Analyst", "2025-10-01", None),
    ("NV-U08", "Hoàng Đức Anh", "ORG-NOVA", "HR Core Squad", "Backend Engineer (PHP/PostgreSQL)", "2025-10-15", None),
    ("NV-U09", "Đỗ Thảo Vy", "ORG-NOVA", "HR Core Squad", "Frontend Engineer (TypeScript)", "2025-11-03", None),
    ("NV-U10", "Ngô Quang Vinh", "ORG-NOVA", "Attendance Squad", "Backend Engineer — Shift & Punch", "2025-11-03", None),
    ("NV-U11", "Trịnh Mai Phương", "ORG-NOVA", "Attendance Squad", "Integration Engineer — Biometric Sync", "2025-11-17", None),
    ("NV-U12", "Lý Thành Đạt", "ORG-NOVA", "Leave Workflow Squad", "Backend Engineer — Accrual Engine", "2025-12-01", None),
    ("NV-U13", "Phan Ngọc Ánh", "ORG-NOVA", "Leave Workflow Squad", "Frontend Engineer — Approval Portal", "2025-12-01", None),
    ("NV-U14", "Vũ Đình Khoa", "ORG-NOVA", "Data Migration & UAT", "ETL & Data Quality Engineer", "2026-01-05", None),
    ("NV-U15", "Hồ Thanh Trúc", "ORG-NOVA", "PMO & Quality", "QA Lead — SIT & UAT", "2026-01-05", None),
    ("NV-U16", "Đinh Tuấn Kiệt", "ORG-NOVA", "PMO & Quality", "QA Automation Engineer", "2026-01-19", None),
    ("NV-U17", "Mai Bảo Ngọc", "ORG-NOVA", "PMO & Quality", "QA Analyst — Leave & Attendance", "2026-02-02", None),
    ("NV-U18", "Trương Hải Đăng", "ORG-NOVA", "DevSecOps", "Release & DB Migration Engineer", "2026-02-09", None),
    ("NV-U19", "Kiều Minh Châu", "ORG-NOVA", "Business Analysis", "Former Business Analyst (Offboarded)", "2025-09-01", "2026-08-14"),
    ("MP-U01", "Nguyễn Thị Bích Ngọc", "ORG-MINHPHAT", "Client HR Dept", "HR Director — Minh Phát (~300 nhân sự)", "2026-04-16", None),
    ("MP-U02", "Lâm Văn Phúc", "ORG-MINHPHAT", "Client C&B", "C&B Supervisor — Timekeeping UAT", "2026-04-16", None),
    ("MP-U03", "Châu Mỹ Duyên", "ORG-MINHPHAT", "Client Factory Admin", "Factory Shift Coordinator", "2026-04-16", None),
    ("MP-U04", "Tạ Quốc Hưng", "ORG-MINHPHAT", "Client IT", "Client IT Infrastructure Contact", "2026-04-16", None),
]

PROJECT_SPECS = [
    {
        "project_id": "NOVA-HR",
        "code": "NVHR",
        "name": "Hồ Sơ Nhân Sự, Hợp Đồng & Cơ Cấu Báo Cáo (Core HR)",
        "description": "Phân hệ quản lý hồ sơ hành chính nhân viên (~300 nhân sự Minh Phát), hợp đồng lao động, địa điểm làm việc, dây chuyền quản lý trực tiếp/gián tiếp và quy trình thôi việc theo mô hình Waterfall.",
        "methodology": "WATERFALL",
        "created_by": "NV-U02",
        "leader_id": "NV-U03",
        "member_ids": ["NV-U07", "NV-U08", "NV-U09", "NV-U15", "NV-U18"],
        "former_member_ids": ["NV-U19"],
        "start_date": "2026-04-16",
        "target_date": "2026-10-30",
    },
    {
        "project_id": "NOVA-ATD",
        "code": "NVATD",
        "name": "Quản Lý Ca Làm Việc, Đồng Bộ Chấm Công & Tăng Ca (Attendance)",
        "description": "Phân hệ phân ca hành chính/ca nhà máy, đồng bộ log máy chấm công vân tay, khấu trừ giờ nghỉ trưa 12:00-13:00 và đối soát giờ tăng ca hợp lệ theo mô hình Waterfall.",
        "methodology": "WATERFALL",
        "created_by": "NV-U02",
        "leader_id": "NV-U04",
        "member_ids": ["NV-U07", "NV-U10", "NV-U11", "NV-U16", "NV-U18"],
        "former_member_ids": [],
        "start_date": "2026-04-16",
        "target_date": "2026-10-30",
    },
    {
        "project_id": "NOVA-LEV",
        "code": "NVLEV",
        "name": "Quản Lý Quỹ Phép Năm, Nghỉ Nửa Ngày & Phê Duyệt Đa Cấp (Leave)",
        "description": "Phân hệ tính quỹ phép năm theo thâm niên, đăng ký nghỉ nguyên ngày/nửa ngày (0.5 ngày), phê duyệt 2 cấp Manager-HR và hoàn trả số dư khi hủy đơn theo mô hình Waterfall.",
        "methodology": "WATERFALL",
        "created_by": "NV-U02",
        "leader_id": "NV-U05",
        "member_ids": ["NV-U07", "NV-U12", "NV-U13", "NV-U15", "NV-U17"],
        "former_member_ids": ["NV-U19"],
        "start_date": "2026-04-16",
        "target_date": "2026-10-30",
    },
    {
        "project_id": "NOVA-DMG",
        "code": "NVDMG",
        "name": "Chuyển Đổi Dữ Liệu Nhân Sự Cũ, Nghiệm Thu UAT & Bàn Giao (Cutover)",
        "description": "Phân hệ chuẩn hóa dữ liệu Excel lịch sử 300 nhân viên Minh Phát, kiểm soát yêu cầu thay đổi (Change Request), tổ chức SIT/UAT và nghiệm thu bàn giao hệ thống.",
        "methodology": "WATERFALL",
        "created_by": "NV-U01",
        "leader_id": "NV-U06",
        "member_ids": ["NV-U07", "NV-U14", "NV-U15", "NV-U16", "NV-U17", "NV-U18"],
        "former_member_ids": ["NV-U19"],
        "start_date": "2026-04-16",
        "target_date": "2026-10-30",
    },
]

WATERFALL_PHASE_GATES = [
    {"phase_gate_id": "WFG-NOVA-01", "phase_order": 1, "phase_code": "SURVEY_DISCOVERY", "name": "Khảo sát hiện trạng 300 nhân sự & quy chế chấm công Minh Phát", "planned_start": "2026-04-16", "planned_end": "2026-05-15", "status": "SIGNED_OFF", "signed_off_by": "NV-U01", "signed_off_at": "2026-05-15T16:00:00+07:00", "exit_artifact_id": "DOC-NVHR-REQ-001"},
    {"phase_gate_id": "WFG-NOVA-02", "phase_order": 2, "phase_code": "FRS_BASELINE", "name": "Đặc tả yêu cầu nghiệp vụ (FRS Baseline v1.0 → cập nhật v2.0 sau CR-2026-08)", "planned_start": "2026-05-18", "planned_end": "2026-06-12", "status": "SIGNED_OFF_WITH_CR_AMENDMENT", "signed_off_by": "NV-U02", "signed_off_at": "2026-06-12T15:30:00+07:00", "exit_artifact_id": "DOC-NVLEV-REQ-001"},
    {"phase_gate_id": "WFG-NOVA-03", "phase_order": 3, "phase_code": "SYSTEM_DB_API_DESIGN", "name": "Thiết kế kiến trúc, cơ sở dữ liệu & hợp đồng API (cập nhật DB v2.0 do lỗi hủy phép nửa ngày)", "planned_start": "2026-06-15", "planned_end": "2026-07-17", "status": "SIGNED_OFF_REVISED", "signed_off_by": "NV-U01", "signed_off_at": "2026-07-17T16:15:00+07:00", "exit_artifact_id": "DOC-NVLEV-DB-002"},
    {"phase_gate_id": "WFG-NOVA-04", "phase_order": 4, "phase_code": "IMPLEMENTATION_UNIT_TEST", "name": "Phát triển phân hệ Core HR, Attendance, Leave & ETL Migration", "planned_start": "2026-07-20", "planned_end": "2026-09-11", "status": "SIGNED_OFF", "signed_off_by": "NV-U02", "signed_off_at": "2026-09-11T16:30:00+07:00", "exit_artifact_id": "DOC-NVATD-API-003"},
    {"phase_gate_id": "WFG-NOVA-05", "phase_order": 5, "phase_code": "SIT_AND_UAT", "name": "Kiểm thử tích hợp SIT & Nghiệm thu người dùng UAT với Minh Phát", "planned_start": "2026-09-14", "planned_end": "2026-10-09", "status": "CONDITIONAL_SIGN_OFF", "signed_off_by": "NV-U02", "signed_off_at": "2026-10-09T16:40:00+07:00", "exit_artifact_id": "DOC-NVDMG-UAT-004"},
    {"phase_gate_id": "WFG-NOVA-06", "phase_order": 6, "phase_code": "CUTOVER_AND_HANDOVER", "name": "Di chuyển dữ liệu cutover cuối kỳ, đào tạo C&B và bàn giao vận hành", "planned_start": "2026-10-12", "planned_end": "2026-10-30", "status": "IN_PROGRESS", "signed_off_by": None, "signed_off_at": None, "exit_artifact_id": "DOC-NVDMG-HND-006"},
]

DISRUPTION_EVENTS = [
    {
        "disruption_id": "DIS-NOVA-OFFBOARD-01",
        "organization_id": "ORG-NOVA",
        "project_id": "NOVA-LEV",
        "kind": "employee_offboarding",
        "affected_user_id": "NV-U19",
        "backup_user_id": "NV-U07",
        "unavailable_from": "2026-08-15T00:00:00+07:00",
        "unavailable_to": "2026-12-31T23:59:59+07:00",
        "cause": "BA Kiều Minh Châu (NV-U19) nghỉ việc theo nguyện vọng cá nhân ngày 2026-08-14 giữa giai đoạn phát triển.",
        "impact": "Cần bàn giao toàn bộ tài liệu FRS v1.0 và kịch bản UAT nghỉ phép/hồ sơ nhân sự cho Lead BA Bùi Khánh Linh (NV-U07).",
        "resolution": "Thu hồi quyền truy cập ORG-NOVA/project_memberships cuối ngày 2026-08-14; NV-U07 tiếp nhận cập nhật FRS v2.0.",
    },
    {
        "disruption_id": "DIS-NOVA-SICK-01",
        "organization_id": "ORG-NOVA",
        "project_id": "NOVA-HR",
        "kind": "sick_leave",
        "affected_user_id": "NV-U09",
        "backup_user_id": "NV-U08",
        "unavailable_from": "2026-09-07T08:00:00+07:00",
        "unavailable_to": "2026-09-09T22:00:00+07:00",
        "cause": "Frontend Engineer Đỗ Thảo Vy (NV-U09) nghỉ ốm sốt xuất huyết nhẹ 3 ngày (07–09/09/2026) ngay tuần chốt code Phase 4.",
        "impact": "Nguy cơ trễ màn hình cây sơ đồ báo cáo trực tiếp/gián tiếp (Supervisor Report-To Tree) trước cổng SIT.",
        "resolution": "Tech Lead NV-U03 điều phối NV-U08 hỗ trợ hoàn thiện binding API cây nhân sự trong subtask bàn giao NVHR-22.",
    },
    {
        "disruption_id": "DIS-NOVA-STORM-01",
        "organization_id": "ORG-NOVA",
        "project_id": "NOVA-LEV",
        "kind": "storm_power_network_outage",
        "affected_user_id": "NV-U13",
        "backup_user_id": "NV-U12",
        "unavailable_from": "2026-09-24T08:00:00+07:00",
        "unavailable_to": "2026-09-25T22:00:00+07:00",
        "cause": "Mưa bão lớn gây ngập và sự cố trạm biến áp khu vực Quận 7 khiến Phan Ngọc Ánh (NV-U13) mất điện và internet diện rộng ngày 24–25/09/2026.",
        "impact": "Gián đoạn sửa lỗi hiển thị số dư phép nửa ngày (0.5 ngày) trên màn hình UAT Approval Portal.",
        "resolution": "Lý Thành Đạt (NV-U12) tiếp nhận bản vá khẩn cấp NVLEV-23 và xác nhận với QA Hồ Thanh Trúc (NV-U15).",
    },
]

CHANGE_REQUEST_RECORDS = [
    {
        "cr_id": "CR-2026-08",
        "organization_id": "ORG-NOVA",
        "requested_by_external": "MP-U01",
        "recorded_by": "NV-U07",
        "decided_by": "NV-U01",
        "submitted_at": "2026-09-21T09:30:00+07:00",
        "decided_at": "2026-09-23T15:00:00+07:00",
        "title": "Bổ sung quy đổi tự động giờ tăng ca thành quỹ nghỉ bù (Compensatory Leave Ledger)",
        "decision": "PARTIALLY_ACCEPTED_SPLIT_PHASE",
        "approved_phase1_scope": "Chấp thuận bổ sung báo cáo đối soát & xuất CSV giờ tăng ca đủ điều kiện nghỉ bù (NVATD-27, DOC-NVATD-API-003 v2).",
        "deferred_phase2_scope": "Hoãn bộ máy tự động cộng/trừ quỹ nghỉ bù có thời hạn hết hạn 90 ngày sang Hợp đồng Giai đoạn 2 (task NVLEV-29 chuyển CANCELLED ở Phase 1 để bảo vệ mốc Go-Live 30/10/2026).",
        "document_id": "DOC-NVDMG-CR-003",
    }
]

SOURCE_ATTRIBUTION = [
    {
        "repo_url": "https://github.com/orangehrm/orangehrm",
        "repo_name": "orangehrm/orangehrm",
        "selected_release_or_tag": "v5.9",
        "commit_sha": "56e23b3b09e7af29317a0943523b825843fff527",
        "accessed_at": "2026-10-28T08:17:08+07:00",
        "license": "GPL-3.0-or-later",
        "inspected_artifacts": [
            "LICENSE",
            "README.md",
            "src/composer.json",
            "src/plugins/orangehrmPimPlugin/entity/ (Employee, EmpContract, EmpLocations, EmployeeTerminationRecord, ReportTo)",
            "src/plugins/orangehrmLeavePlugin/entity/ (LeaveRequest, Leave, LeaveEntitlement, LeaveType, Holiday, WorkWeek)",
            "src/plugins/orangehrmAttendancePlugin/entity/ (AttendanceRecord)",
            "Public GitHub issues #1964 (Supervisor/Org Chart), #1965 & #1966 (partial/half-day leave cancellation balance edge cases)",
        ],
        "usage_boundary": "Chỉ tham khảo khái niệm nghiệp vụ HR/Chấm công/Nghỉ phép và tình huống lỗi biên nửa ngày để tự thiết kế dữ liệu giả lập độc lập cho Nova Solutions. Tuyệt đối không sao chép mã nguồn, schema Doctrine, tài liệu hay tài sản GPL-3.0 của OrangeHRM; không khẳng định OrangeHRM phát triển theo Waterfall.",
    }
]

IMPLEMENTATION_ASSUMPTIONS = [
    "Giả định triển khai (Implementation Assumption): Quy mô 4 project Waterfall (NOVA-HR, NOVA-ATD, NOVA-LEV, NOVA-DMG), 23 tài khoản người dùng (19 Nova + 4 khách hàng Minh Phát) và cửa sổ mô phỏng 2026-04-16 .. 2026-10-16 được chọn để bao phủ trọn 6 cổng giai đoạn Waterfall mà Thang chưa chốt cứng con số tuyệt đối.",
    "Giả định triển khai (Implementation Assumption): Toàn bộ 4 project của Nova đều dùng Waterfall thuần túy (sprints = [], sprint_id = null trên mọi task) để tạo đối trọng rõ rệt với Agile Sprint (Northstar), Kanban (CloudOps) và Hybrid (MediFlow).",
    "Giả định triển khai (Implementation Assumption): Phạm vi nghiệp vụ dừng ở Hồ sơ nhân sự, Ca chấm công và Nghỉ phép cho ~300 nhân viên; không bao gồm tính lương (Payroll), BHXH hay thuế TNCN.",
]
