"""Bespoke Kanban & 24/7 SRE domain specifications for Organization 3 — CloudOps Services."""

from __future__ import annotations

NAMESPACE = "cloudops"
PRIMARY_ORG_ID = "ORG-CLD"
SIM_START = "2026-04-16"
AS_OF_DATE = "2026-10-16"

ORG_SPECS = [
    ("ORG-CLD", "CloudOps Services Co., Ltd.", "managed_sre_saas_operator", "cloudops.invalid", "ENTERPRISE"),
    ("ORG-FINLEDGER", "FinLedger Enterprise SaaS Tenant", "enterprise_customer_tenant", "finledger.invalid", "FREE"),
    ("ORG-VINACLOUD", "VinaCloud Managed Infrastructure Partner", "upstream_cloud_provider", "vinacloud.invalid", "FREE"),
]

ORG_ADMIN_IDS = {"CLD-U01", "CLD-U02"}

USER_SPECS = [
    ("CLD-U01", "Nguyễn Minh Khôi", "ORG-CLD", "SRE Leadership", "VP of Reliability & Operations (Org Manager)", "2025-03-03", None),
    ("CLD-U02", "Trần Phương Thảo", "ORG-CLD", "Service Delivery", "Head of SaaS Support & Incident Governance (Org Manager)", "2025-04-01", None),
    ("CLD-U03", "Lê Hoàng Bách", "ORG-CLD", "Incident Command", "Lead SRE — Alerting & Incident Relay", "2025-05-05", None),
    ("CLD-U04", "Phạm Thanh Hằng", "ORG-CLD", "Observability", "Lead Observability & SLO Engineer", "2025-05-19", None),
    ("CLD-U05", "Vũ Quốc Tuấn", "ORG-CLD", "Cloud Infrastructure", "Lead Infrastructure & Database Reliability Engineer", "2025-06-02", None),
    ("CLD-U06", "Đỗ Lan Anh", "ORG-CLD", "Customer Reliability", "Lead Tier-3 Support & Escalations Engineer", "2025-06-16", None),
    ("CLD-U07", "Hoàng Gia Bảo", "ORG-CLD", "Incident Command", "Senior On-Call SRE (Primary Rotation A)", "2025-07-01", None),
    ("CLD-U08", "Bùi Minh Nhật", "ORG-CLD", "Incident Command", "Senior On-Call SRE (Secondary Rotation A)", "2025-07-15", None),
    ("CLD-U09", "Ngô Thu Trang", "ORG-CLD", "Observability", "Telemetry & OpenTelemetry Pipeline Engineer", "2025-08-01", None),
    ("CLD-U10", "Đặng Anh Quân", "ORG-CLD", "Cloud Infrastructure", "Kubernetes & WAF Security SRE", "2025-08-18", None),
    ("CLD-U11", "Trịnh Khánh Toàn", "ORG-CLD", "Cloud Infrastructure", "PostgreSQL & PgBouncer Reliability Engineer", "2025-09-03", None),
    ("CLD-U12", "Lý Ngọc Diệp", "ORG-CLD", "Observability", "Synthetic Probing & Heartbeat Engineer", "2025-09-15", None),
    ("CLD-U13", "Phan Tuấn Dũng", "ORG-CLD", "Incident Command", "Alert Routing & Runbook Automation Engineer", "2025-10-01", None),
    ("CLD-U14", "Vương Mỹ Linh", "ORG-CLD", "Customer Reliability", "Tier-3 Application Support Specialist", "2025-10-20", None),
    ("CLD-U15", "Hồ Trọng Nghĩa", "ORG-CLD", "Customer Reliability", "SLA & Tenant Communications Analyst", "2025-11-10", None),
    ("CLD-U16", "Mai Xuân Trường", "ORG-CLD", "Cloud Infrastructure", "Terraform IaC & Drift Remediation Engineer", "2025-12-01", None),
    ("CLD-U17", "Đinh Hà My", "ORG-CLD", "Customer Reliability", "Incident Scribe & Postmortem QA Analyst", "2026-01-12", None),
    ("CLD-U18", "Tô Hải Nam", "ORG-CLD", "Incident Command", "Former On-Call SRE (Offboarded)", "2025-06-01", "2026-08-28"),
    ("FL-U01", "Đoàn Thanh Tùng", "ORG-FINLEDGER", "Tenant Engineering", "FinLedger Platform Integration Lead", "2026-04-16", None),
    ("FL-U02", "Lương Bích Phương", "ORG-FINLEDGER", "Tenant Ops", "FinLedger Operations Duty Manager", "2026-04-16", None),
    ("FL-U03", "Cao Minh Đức", "ORG-FINLEDGER", "Tenant Security", "FinLedger Security Auditor", "2026-04-16", None),
    ("VC-U01", "Trần Đình Phong", "ORG-VINACLOUD", "NOC", "VinaCloud Upstream Network Engineer", "2026-04-16", None),
    ("VC-U02", "Nguyễn Hải Yến", "ORG-VINACLOUD", "TAM", "VinaCloud Technical Account Manager", "2026-04-16", None),
]

SYSTEM_BOTS = [
    {"bot_id": "CLD-BOT-HEARTBEAT", "name": "Dead-Man-Switch Heartbeat Watchdog", "schedule": "24x7_every_60s", "organization_id": "ORG-CLD"},
    {"bot_id": "CLD-BOT-ALERTGROUP", "name": "AlertGroup Deduplication & Auto-Unshelve Worker", "schedule": "24x7_continuous", "organization_id": "ORG-CLD"},
    {"bot_id": "CLD-BOT-TF-DRIFT", "name": "Hourly Terraform & WAF Drift Detector", "schedule": "24x7_hourly", "organization_id": "ORG-CLD"},
]

PROJECT_SPECS = [
    {
        "project_id": "CLD-INC",
        "code": "CLDINC",
        "name": "Điều Phối Cảnh Báo, Lịch Trực Escalation & Xử Lý Sự Cố (Incident Relay)",
        "description": "Luồng vận hành Kanban tiếp nhận cảnh báo, gom nhóm chống bão alert (AlertGroup), tạm ẩn có thời hạn (shelve), leo thang ca trực và điều phối sự cố P0/P1.",
        "methodology": "KANBAN",
        "created_by": "CLD-U01",
        "leader_id": "CLD-U03",
        "member_ids": ["CLD-U07", "CLD-U08", "CLD-U13", "CLD-U17"],
        "former_member_ids": ["CLD-U18"],
        "start_date": "2026-04-16",
        "target_date": "2026-12-31",
    },
    {
        "project_id": "CLD-OBS",
        "code": "CLDOBS",
        "name": "Giám Sát Telemetry, Heartbeat Watchdog & Cảnh Báo SLO Burn-Rate",
        "description": "Luồng vận hành Kanban duy trì pipeline OpenTelemetry, bộ dò nhịp tim dịch vụ nền và tinh chỉnh ngưỡng cảnh báo độ trễ đa tenant.",
        "methodology": "KANBAN",
        "created_by": "CLD-U01",
        "leader_id": "CLD-U04",
        "member_ids": ["CLD-U08", "CLD-U09", "CLD-U12", "CLD-U13"],
        "former_member_ids": [],
        "start_date": "2026-04-16",
        "target_date": "2026-12-31",
    },
    {
        "project_id": "CLD-INF",
        "code": "CLDINF",
        "name": "Hạ Tầng Kubernetes Đa Tenant, Terraform IaC & Vận Hành PostgreSQL Không Gián Đoạn",
        "description": "Luồng Kanban xử lý gốc hạ tầng, kiểm soát trôi cấu hình WAF/Terraform, tối ưu PgBouncer và bảo trì cơ sở dữ liệu expand/contract.",
        "methodology": "KANBAN",
        "created_by": "CLD-U01",
        "leader_id": "CLD-U05",
        "member_ids": ["CLD-U07", "CLD-U10", "CLD-U11", "CLD-U16"],
        "former_member_ids": ["CLD-U18"],
        "start_date": "2026-04-16",
        "target_date": "2026-12-31",
    },
    {
        "project_id": "CLD-SUP",
        "code": "CLDSUP",
        "name": "Hỗ Trợ Kỹ Thuật Tier-3, Quản Trị SLA Khách Hàng & Hậu Kiểm Postmortem",
        "description": "Luồng Kanban tiếp nhận yêu cầu hỗ trợ doanh nghiệp, truyền thông trạng thái sự cố minh bạch, theo dõi cam kết SLA và đóng hành động phòng ngừa tái diễn.",
        "methodology": "KANBAN",
        "created_by": "CLD-U02",
        "leader_id": "CLD-U06",
        "member_ids": ["CLD-U14", "CLD-U15", "CLD-U16", "CLD-U17"],
        "former_member_ids": [],
        "start_date": "2026-04-16",
        "target_date": "2026-12-31",
    },
]

KANBAN_WIP_POLICIES = [
    {"policy_id": "KBP-CLDINC", "project_id": "CLD-INC", "in_progress_wip_limit": 5, "in_review_wip_limit": 3, "expedite_lane_max": 1, "classes_of_service": ["EXPEDITE_P0", "FIXED_DATE_SLA", "STANDARD_FLOW", "INTANGIBLE_TECH_DEBT"], "sle_p85_business_days": 3, "pull_rule": "Hàng đợi EXPEDITE_P0 được phép vượt trần WIP tối đa 1 mục nhưng phải tạm dừng kéo việc STANDARD_FLOW mới cho đến khi đóng điểm nghẽn."},
    {"policy_id": "KBP-CLDOBS", "project_id": "CLD-OBS", "in_progress_wip_limit": 4, "in_review_wip_limit": 3, "expedite_lane_max": 1, "classes_of_service": ["EXPEDITE_P0", "STANDARD_FLOW", "INTANGIBLE_TECH_DEBT"], "sle_p85_business_days": 5, "pull_rule": "Ưu tiên xử lý cảnh báo nhiễu (alert fatigue) có tỷ lệ false-positive > 15% trước khi thêm dashboard mới."},
    {"policy_id": "KBP-CLDINF", "project_id": "CLD-INF", "in_progress_wip_limit": 4, "in_review_wip_limit": 2, "expedite_lane_max": 1, "classes_of_service": ["EXPEDITE_P0", "FIXED_DATE_SLA", "STANDARD_FLOW", "INTANGIBLE_TECH_DEBT"], "sle_p85_business_days": 6, "pull_rule": "Mọi thay đổi schema CSDL hoặc rule WAF bắt buộc qua Terraform PR trừ thao tác cô lập P0 có hiệu lực tạm <= 4 giờ."},
    {"policy_id": "KBP-CLDSUP", "project_id": "CLD-SUP", "in_progress_wip_limit": 6, "in_review_wip_limit": 3, "expedite_lane_max": 1, "classes_of_service": ["EXPEDITE_P0", "FIXED_DATE_SLA", "STANDARD_FLOW"], "sle_p85_business_days": 4, "pull_rule": "Ticket khách hàng gắn hậu kiểm sự cố P0 không được đóng khi mới có workaround tạm thời mà chưa gắn mã task xử lý gốc."},
]

ONCALL_SCHEDULES = [
    {
        "schedule_id": "OC-2026-0818-EVENING",
        "organization_id": "ORG-CLD",
        "rotation_name": "Infra & DB Primary On-Call",
        "primary_user_id": "CLD-U11",
        "secondary_user_id": "CLD-U05",
        "start_at": "2026-08-18T17:00:00+07:00",
        "end_at": "2026-08-19T08:00:00+07:00",
        "override_note": "Ca trực giám sát bảo trì mở rộng cột PostgreSQL tối 18/08/2026.",
    },
    {
        "schedule_id": "OC-2026-0902-HOLIDAY",
        "organization_id": "ORG-CLD",
        "rotation_name": "National Day Holiday 24h SRE Rotation",
        "primary_user_id": "CLD-U07",
        "secondary_user_id": "CLD-U08",
        "start_at": "2026-09-02T00:00:00+07:00",
        "end_at": "2026-09-02T23:59:59+07:00",
        "override_note": "Trực lễ Quốc khánh 02/09: Primary CLD-U07 bị đứt cáp quang gia đình do mưa bão lúc 08:30 nên hệ thống tự động leo thang (escalate) sang Secondary CLD-U08 lúc 09:17+07:00.",
    },
    {
        "schedule_id": "OC-2026-0926-SATURDAY",
        "organization_id": "ORG-CLD",
        "rotation_name": "Weekend Edge & WAF Duty Rotation",
        "primary_user_id": "CLD-U10",
        "secondary_user_id": "CLD-U05",
        "start_at": "2026-09-26T08:00:00+07:00",
        "end_at": "2026-09-26T22:00:00+07:00",
        "override_note": "Ca trực Thứ Bảy xử lý sự cố chặn nhầm webhook đối tác FinLedger do cấu hình WAF lệch ngoài Terraform.",
    },
]

INCIDENT_RECORDS = [
    {
        "incident_id": "INC-2026-0818",
        "severity": "SEV-1",
        "title": "Lỗi tương thích ngược khi đổi kiểu cột audit_event_seq gây lỗi ghi trên pod cũ trong lúc rolling deploy",
        "detected_at": "2026-08-18T19:10:00+07:00",
        "detected_by": "CLD-BOT-ALERTGROUP",
        "commander_id": "CLD-U05",
        "temporary_mitigation": "Quay lui ngay deployment ứng dụng về bản build trước và hủy phiên DDL đang giữ khóa (task CLDINF-9).",
        "permanent_root_cause_fix": "Ban hành chuẩn migration Expand/Contract 3 bước tại DOC-CLDINF-DB-002 v2 và lưu trữ runbook cũ DOC-CLDINF-RUN-006-LEGACY (task CLDINF-10).",
        "status": "RESOLVED_PERMANENTLY",
    },
    {
        "incident_id": "INC-2026-0902",
        "severity": "SEV-0",
        "title": "Bão kết nối PgBouncer ngày lễ Quốc khánh 02/09 làm nghẽn API xác thực đa tenant & mất nhịp Heartbeat",
        "detected_at": "2026-09-02T09:12:00+07:00",
        "detected_by": "CLD-BOT-HEARTBEAT",
        "commander_id": "CLD-U08",
        "temporary_mitigation": "Secondary On-Call CLD-U08 rút lưu lượng báo cáo nặng sang read-replica và shelve tạm cảnh báo trùng trong 120 phút (CLDINC-9 — chỉ là xử lý tạm thời!).",
        "permanent_root_cause_fix": "Tách pool PgBouncer riêng cho luồng auth-critical kèm áp ngưỡng statement_timeout=3000ms (CLDINF-19, DOC-CLDINC-RCA-002 v2).",
        "status": "RESOLVED_PERMANENTLY",
    },
    {
        "incident_id": "INC-2026-0926",
        "severity": "SEV-1",
        "title": "Rule WAF sửa tay ngoài luồng Terraform chặn nhầm HTTP 403 đối với webhook của khách hàng FinLedger",
        "detected_at": "2026-09-26T14:05:00+07:00",
        "detected_by": "CLD-BOT-TF-DRIFT",
        "commander_id": "CLD-U10",
        "temporary_mitigation": "Gỡ rule tay khẩn cấp cho dải IP ký số của FinLedger trong ca trực Thứ Bảy 26/09 (CLDINF-23).",
        "permanent_root_cause_fix": "Đồng bộ toàn bộ chính sách WAF vào module Terraform và bật khóa cảnh báo sửa tay ngoài IaC (CLDINF-24, DOC-CLDINF-ARC-001 v2).",
        "status": "MITIGATED_FOLLOWUP_IN_REVIEW",
    },
]

DISRUPTION_EVENTS = [
    {
        "disruption_id": "DIS-CLD-OFFBOARD-01",
        "organization_id": "ORG-CLD",
        "project_id": "CLD-INC",
        "kind": "employee_offboarding",
        "affected_user_id": "CLD-U18",
        "backup_user_id": "CLD-U08",
        "unavailable_from": "2026-08-29T00:00:00+07:00",
        "unavailable_to": "2026-12-31T23:59:59+07:00",
        "cause": "Kỹ sư SRE Tô Hải Nam (CLD-U18) hoàn tất bàn giao và nghỉ việc từ cuối ngày 2026-08-28.",
        "impact": "Trống lịch trực chính kỳ nghỉ lễ Quốc khánh đầu tháng 09 và các thẻ Kanban tự động hóa cảnh báo.",
        "resolution": "Cập nhật lịch trực sang CLD-U07 / CLD-U08, thu hồi toàn bộ API key và quyền ORG-CLD ngày 28/08/2026.",
    },
    {
        "disruption_id": "DIS-CLD-STORM-01",
        "organization_id": "ORG-CLD",
        "project_id": "CLD-INC",
        "kind": "storm_isp_fiber_cut",
        "affected_user_id": "CLD-U07",
        "backup_user_id": "CLD-U08",
        "unavailable_from": "2026-09-02T08:00:00+07:00",
        "unavailable_to": "2026-09-02T23:00:00+07:00",
        "cause": "Mưa bão lớn ngày Quốc khánh 02/09 làm đứt cáp quang khu dân cư và mất sóng 4G cục bộ nơi Primary On-Call Hoàng Gia Bảo (CLD-U07) cư trú.",
        "impact": "CLD-U07 không thể nhận ACK cảnh báo SEV-0 INC-2026-0902 lúc 09:12+07:00 trong vòng 5 phút đầu.",
        "resolution": "Chính sách Escalation tự động chuyển quyền chỉ huy sự cố sang Secondary On-Call Bùi Minh Nhật (CLD-U08) lúc 09:17+07:00.",
    },
    {
        "disruption_id": "DIS-CLD-SICK-01",
        "organization_id": "ORG-CLD",
        "project_id": "CLD-INF",
        "kind": "sick_leave",
        "affected_user_id": "CLD-U11",
        "backup_user_id": "CLD-U16",
        "unavailable_from": "2026-09-16T08:00:00+07:00",
        "unavailable_to": "2026-09-17T22:00:00+07:00",
        "cause": "Kỹ sư CSDL Trịnh Khánh Toàn (CLD-U11) nghỉ ốm viêm phế quản cấp 2 ngày 16–17/09/2026.",
        "impact": "Thẻ Kanban tinh chỉnh cấu hình PgBouncer sau sự cố lễ 02/09 có nguy cơ chạm trần WIP.",
        "resolution": "Lead CLD-U05 điều phối Mai Xuân Trường (CLD-U16) tiếp nhận kiểm thử tải subtask CLDINF-20.",
    },
]

SOURCE_ATTRIBUTION = [
    {
        "repo_url": "https://github.com/roxy-wi/IncidentRelay",
        "repo_name": "roxy-wi/IncidentRelay",
        "selected_release_or_tag": "v2.4.0",
        "commit_sha": "21ea27d92927242ed499b7584a276f47cb1c68cd",
        "accessed_at": "2026-10-28T08:17:08+07:00",
        "license": "Elastic-2.0 (Elastic License 2.0 — source-available, NOT OSI open-source)",
        "inspected_artifacts": [
            "LICENSE & LICENSING.md (verified Elastic License 2.0 terms)",
            "README.md",
            "app/modules/, app/services/, app/scheduler_worker.py",
            "docs/incidents/ & docs/scheduling/ (AlertGroup deduplication, temporary shelving with auto-expiry, escalation steps, on-call overrides, heartbeat monitors)",
            "Public GitHub issues #127, #128, #130",
        ],
        "usage_boundary": "Chỉ khảo sát mô hình nghiệp vụ điều phối cảnh báo, gom nhóm AlertGroup, shelve có thời hạn, lịch trực và heartbeat để tự thiết kế kịch bản synthetic độc lập cho CloudOps Services. Tuyệt đối không sao chép mã nguồn, tài liệu hay thành phần nào chịu điều khoản Elastic-2.0; không khẳng định IncidentRelay dùng Kanban.",
    },
    {
        "repo_url": "https://github.com/danluu/post-mortems",
        "repo_name": "danluu/post-mortems",
        "selected_release_or_tag": "master",
        "commit_sha": "630562e55281ff28961704e8042a7dc9569a96e7",
        "accessed_at": "2026-10-28T08:17:08+07:00",
        "license": "No repository LICENSE file (license: null; curated directory of external third-party postmortem links, each governed by its own publisher terms)",
        "inspected_artifacts": [
            "README.md index structure and failure mode categories (deployment schema incompatibility, configuration/WAF drift, cascading connection pool saturation)",
        ],
        "usage_boundary": "Chỉ tham khảo cấu trúc phân tích sự cố (phát hiện → giảm nhẹ tạm thời → nguyên nhân gốc → hành động phòng ngừa); 100% văn bản RCA, số liệu và nhân vật trong CloudOps là giả lập độc lập, không chép bất kỳ bài postmortem bên thứ ba nào.",
    },
]

IMPLEMENTATION_ASSUMPTIONS = [
    "Giả định triển khai (Implementation Assumption): Quy mô 4 luồng vận hành Kanban (CLD-INC, CLD-OBS, CLD-INF, CLD-SUP), 23 nhân sự người dùng + 3 bot tự động 24/7 và cửa sổ 2026-04-16 .. 2026-10-16 được thiết lập để kiểm chứng rõ sự khác biệt giữa ca hành chính, OT buổi tối, ca trực lễ/cuối tuần có lịch trực và bot chạy 24/7.",
    "Giả định triển khai (Implementation Assumption): Toàn bộ 4 project vận hành theo Kanban liên tục không chia Sprint (sprints = [], sprint_id = null), kiểm soát bằng giới hạn WIP và Class of Service trong structured/kanban_wip_policies.jsonl.",
]
