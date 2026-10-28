"""56 unreviewed benchmark evaluation cases for Organization 3 — CloudOps Services (Kanban SRE)."""

from __future__ import annotations

from typing import Any, Callable


def build_cloudops_eval_cases(
    make_eval_case_fn: Callable[..., dict[str, Any]],
    as_of: str,
    task_id_by_key: dict[str, str],
    note_id_by_key: dict[str, str],
) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    def add(
        suite: str,
        channel: str,
        cat: str,
        pid: str | None,
        principal: str,
        q: str,
        ans: str,
        targets: list[str],
        sources: list[str],
        forbid: list[str] | None = None,
        mandatory: list[str] | None = None,
        forbidden_claims: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> None:
        idx = len(cases) + 1
        cases.append(
            make_eval_case_fn(
                case_id=f"CLD-EVAL-{idx:03d}",
                org_id="ORG-CLD",
                project_id=pid,
                as_of=as_of,
                idx=idx,
                suite=suite,
                answer_channel=channel,
                case_category=cat,
                principal_id=principal,
                question=q,
                expected_answer=ans,
                target_resource_ids=targets,
                source_ids=sources,
                must_not_cite=forbid or [],
                mandatory_points=mandatory or [],
                forbidden_claims=forbidden_claims or [],
                tags=tags or [],
            )
        )

    # 1-10: Temporary Workaround vs Root-Cause Fix, RCA v1 vs v2, Holiday On-Call Escalation, Legacy Runbook, Rejected/Draft Docs
    add(
        "WORKAROUND_VS_ROOTCAUSE", "knowledge", "workaround_vs_fix", "CLD-INC", "CLD-U03",
        "Trong sự cố SEV-0 ngày Quốc khánh 02/09/2026 (INC-2026-0902), việc chuyển lưu lượng sang read-replica và shelve cảnh báo 120 phút tại CLDINC-9 đã khắc phục triệt để nguyên nhân gốc chưa?",
        "Chưa. Thao tác tại CLDINC-9 (và Task Note đính kèm) chỉ là giải pháp giảm nhẹ tạm thời (temporary workaround) trong ca trực lễ; giải pháp khắc phục triệt để nguyên nhân gốc là tách riêng auth_pool và reporting_pool kèm áp ngưỡng statement_timeout=3000ms tại task CLDINF-19 theo DOC-CLDINC-RCA-002 v2 và DOC-CLDINF-DB-002 v2.",
        [task_id_by_key["CLDINC-9"], note_id_by_key["CLDINC-9"], task_id_by_key["CLDINF-19"], "DOC-CLDINC-RCA-002"],
        ["DOC-CLDINC-RCA-002", "DOC-CLDINF-DB-002", task_id_by_key["CLDINC-9"], task_id_by_key["CLDINF-19"]],
        ["DOC-CLDINC-RCA-002@v1", note_id_by_key["CLDINC-9"]],
        ["giảm nhẹ tạm thời", "CLDINC-9", "CLDINF-19", "auth_pool", "statement_timeout=3000ms"],
        ["Khẳng định shelve 120 phút ở CLDINC-9 là bản sửa lỗi vĩnh viễn"],
        ["workaround_vs_permanent", "holiday_incident"],
    )
    add(
        "RAG_LINEAGE", "knowledge", "version_conflict", "CLD-INC", "CLD-U01",
        "Nguyên nhân gốc được phê duyệt chính thức của sự cố mất kết nối xác thực ngày 02/09/2026 là lỗi phân giải CoreDNS hay bão kết nối PgBouncer?",
        "Nguyên nhân gốc chính thức theo DOC-CLDINC-RCA-002 v2 (APPROVED) là cạn kiệt pool PgBouncer dùng chung do job xuất báo cáo đầu tháng không đặt statement_timeout; giả thuyết lỗi CoreDNS ở phiên bản v1 đã bị bác bỏ (CHANGES_REQUESTED) vì độ trễ DNS thực tế dưới 2ms.",
        ["DOC-CLDINC-RCA-002@v2", "DOC-CLDINC-RCA-002@v1"],
        ["DOC-CLDINC-RCA-002"],
        ["DOC-CLDINC-RCA-002@v1"],
        ["PgBouncer", "DOC-CLDINC-RCA-002", "bác bỏ"],
        ["Kết luận nguyên nhân sự cố 02/09 là do CoreDNS"],
        ["rca_lineage", "rejected_hypothesis"],
    )
    add(
        "END_TO_END_CHAIN", "workspace", "provenance_chain", "CLD-INF", "CLD-U05",
        "Truy vết toàn bộ chuỗi xử lý từ phát hiện tự động sự cố lễ 02/09, leo thang ca trực do bão, xử lý tạm thời CLDINC-9, chuẩn hóa DB v2, kiểm thử tải bàn giao nghỉ ốm đến báo cáo tuần Leader.",
        f"Bot CLD-BOT-HEARTBEAT phát hiện mất nhịp lúc 09:12 ngày 02/09; do Primary CLD-U07 bị đứt cáp quang mưa bão (DIS-CLD-STORM-01), ca trực leo thang sang Secondary CLD-U08 lúc 09:17 để giảm nhẹ tạm thời tại {task_id_by_key['CLDINC-9']} (CLDINC-9, Task Note {note_id_by_key['CLDINC-9']}), sau đó tách pool PgBouncer tại {task_id_by_key['CLDINF-19']} (DOC-CLDINF-DB-002 v2), kiểm thử tải tại {task_id_by_key['CLDINF-20']} do CLD-U16 nhận bàn giao khi CLD-U11 nghỉ ốm (DOC-CLDINF-TST-005) và tổng hợp trong báo cáo tuần Leader CLD-INF-WR-W40-L1.",
        [task_id_by_key["CLDINC-9"], task_id_by_key["CLDINF-19"], task_id_by_key["CLDINF-20"], "DOC-CLDINF-DB-002", "CLD-INF-WR-W40-L1"],
        [task_id_by_key["CLDINC-9"], note_id_by_key["CLDINC-9"], task_id_by_key["CLDINF-19"], task_id_by_key["CLDINF-20"], "DOC-CLDINC-RCA-002", "DOC-CLDINF-DB-002", "DOC-CLDINF-TST-005", "CLD-INF-WR-W40-L1"],
        ["DOC-CLDINF-RUN-006-LEGACY", "DOC-CLDINC-RCA-002@v1"],
        ["CLD-BOT-HEARTBEAT", "CLD-U08", "CLDINC-9", "CLDINF-19", "CLDINF-20", "CLD-INF-WR-W40-L1"],
        [],
        ["end_to_end_chain", "sre_traceability"],
    )
    add(
        "SUPERSEDED_RUNBOOK", "knowledge", "version_conflict", "CLD-INF", "CLD-U05",
        "Kỹ sư CloudOps có được phép chạy lệnh ALTER COLUMN TYPE trực tiếp cùng lúc rolling deploy theo sổ tay DOC-CLDINF-RUN-006-LEGACY không?",
        "Tuyệt đối không. Sổ tay DOC-CLDINF-RUN-006-LEGACY đã bị ARCHIVED sau khi gây sự cố INC-2026-0818; quy chuẩn hiện hành là DOC-CLDINF-DB-002 v2 bắt buộc thực hiện migration 3 bước Expand -> Dual-Write/Backfill -> Contract với lock_timeout=2000ms.",
        ["DOC-CLDINF-DB-002", "DOC-CLDINF-RUN-006-LEGACY"],
        ["DOC-CLDINF-DB-002"],
        ["DOC-CLDINF-RUN-006-LEGACY"],
        ["ARCHIVED", "DOC-CLDINF-DB-002", "Expand", "Contract", "lock_timeout=2000ms"],
        ["Hướng dẫn chạy ALTER COLUMN trực tiếp theo runbook cũ"],
        ["superseded_runbook", "zero_downtime_db"],
    )
    add(
        "REJECTED_EXCLUSION", "knowledge", "rejected_proposal", "CLD-OBS", "CLD-U04",
        "Hệ thống giám sát của CloudOps có bắn cảnh báo Pager đánh thức ca trực khi CPU của một pod vượt 65% trong 30 giây không?",
        "Không. Đề xuất tại DOC-CLDOBS-SLI-006 đã bị REJECTED (task CLDOBS-30 chuyển CANCELLED) vì gây 42% cảnh báo giả khi HPA giãn pod; hệ thống chỉ đánh thức ca trực theo tốc độ đốt ngân sách lỗi SLO đa cửa sổ tại DOC-CLDOBS-REQ-001.",
        ["DOC-CLDOBS-SLI-006", "DOC-CLDOBS-REQ-001"],
        ["DOC-CLDOBS-REQ-001"],
        ["DOC-CLDOBS-SLI-006@v1"],
        ["REJECTED", "DOC-CLDOBS-REQ-001", "burn-rate"],
        ["Khẳng định ca trực được gọi dậy khi CPU pod > 65% trong 30s"],
        ["alert_fatigue", "rejected_doc"],
    )
    add(
        "DRAFT_EXCLUSION", "knowledge", "draft_vs_approved", "CLD-INC", "CLD-U03",
        "Bot điều phối của CloudOps hiện có được phép tự động đóng sự cố SEV-1 sau 15 phút metric xanh theo thiết kế DOC-CLDINC-DES-005 v2 không?",
        "Không. Tính năng tự động đóng sự cố SEV-1 mới nằm ở bản v2 đang PENDING_REVIEW của DOC-CLDINC-DES-005 và chưa được áp dụng trên môi trường vận hành.",
        ["DOC-CLDINC-DES-005@v2", "DOC-CLDINC-DES-005@v1"],
        ["DOC-CLDINC-DES-005@v1", "DOC-CLDINC-REQ-001"],
        ["DOC-CLDINC-DES-005@v2"],
        ["PENDING_REVIEW", "chưa được áp dụng"],
        ["Nói bot đã tự động đóng sự cố SEV-1 sau 15 phút"],
        ["draft_vs_approved", "incident_closure"],
    )
    add(
        "DRAFT_TEMPLATE", "knowledge", "draft_vs_approved", "CLD-SUP", "CLD-U06",
        "Mẫu báo cáo tổng kết độ tin cậy Quý 4/2026 gửi khách hàng Enterprise tại DOC-CLDSUP-COM-006 đã được ban hành chính thức chưa?",
        "Chưa. DOC-CLDSUP-COM-006 đang ở trạng thái DRAFT (knowledge_eligible=false), chưa trình duyệt và chưa có hiệu lực phát hành.",
        ["DOC-CLDSUP-COM-006"],
        ["DOC-CLDSUP-REQ-001"],
        ["DOC-CLDSUP-COM-006", "DOC-CLDSUP-COM-006@v1"],
        ["DRAFT", "chưa trình duyệt"],
        ["Khẳng định mẫu báo cáo Q4 đã được phê duyệt"],
        ["draft_exclusion", "customer_comms"],
    )
    add(
        "WAF_SATURDAY_INCIDENT", "workspace", "weekend_oncall", "CLD-INF", "CLD-U05",
        "Sự cố chặn nhầm HTTP 403 đối với webhook FinLedger chiều Thứ Bảy 26/09/2026 (INC-2026-0926) do ai phát hiện, ai xử lý trong ca trực và thay đổi kiến trúc nào được ban hành sau đó?",
        f"Bot CLD-BOT-TF-DRIFT phát hiện lệch cấu hình lúc 14:05 Thứ Bảy 26/09; kỹ sư trực chính Đặng Anh Quân (CLD-U10, lịch trực OC-2026-0926-SATURDAY) gỡ rule sửa tay khẩn cấp tại {task_id_by_key['CLDINF-23']} (CLDINF-23), đồng thời kiến trúc DOC-CLDINF-ARC-001 v2 chuyển console WAF sang Read-Only và bắt buộc quản lý qua Terraform ({task_id_by_key['CLDINF-24']}).",
        [task_id_by_key["CLDINF-23"], task_id_by_key["CLDINF-24"], "DOC-CLDINF-ARC-001"],
        [task_id_by_key["CLDINF-23"], task_id_by_key["CLDINF-24"], "DOC-CLDINF-ARC-001", "DOC-CLDSUP-RUN-005"],
        [],
        ["CLD-BOT-TF-DRIFT", "CLD-U10", "CLDINF-23", "DOC-CLDINF-ARC-001"],
        [],
        ["weekend_oncall", "waf_drift"],
    )
    add(
        "DISRUPTION_HANDOVER", "workspace", "disruption_handover", "CLD-INF", "CLD-U05",
        "Khi kỹ sư CSDL Trịnh Khánh Toàn (CLD-U11) nghỉ ốm ngày 16–17/09/2026, ai đã nhận bàn giao kiểm thử chịu tải PgBouncer để không chạm trần WIP Kanban?",
        f"Mai Xuân Trường (CLD-U16) đã tiếp nhận và hoàn thành subtask kiểm thử tải {task_id_by_key['CLDINF-20']} (CLDINF-20) cùng báo cáo DOC-CLDINF-TST-005 theo sự kiện DIS-CLD-SICK-01.",
        [task_id_by_key["CLDINF-20"], "DOC-CLDINF-TST-005", "DIS-CLD-SICK-01"],
        [task_id_by_key["CLDINF-20"], "DOC-CLDINF-TST-005", "DIS-CLD-SICK-01"],
        [],
        ["CLD-U11", "CLD-U16", "CLDINF-20"],
        [],
        ["sick_leave", "kanban_handover"],
    )
    add(
        "OFFBOARDING_PROVENANCE", "workspace", "offboarding", "CLD-INC", "CLD-U02",
        "Kỹ sư SRE Tô Hải Nam (CLD-U18) nghỉ việc từ thời điểm nào, lịch trực lễ Quốc khánh được bàn giao cho ai và quyền truy cập hiện tại của CLD-U18 ra sao?",
        "CLD-U18 hoàn tất bàn giao và nghỉ việc cuối ngày 2026-08-28 (DIS-CLD-OFFBOARD-01); lịch trực lễ được chuyển sang cặp CLD-U07 / CLD-U08, và toàn bộ quyền ORG-CLD của CLD-U18 đã bị thu hồi (SUSPENDED/REMOVED).",
        ["DIS-CLD-OFFBOARD-01", "DOC-CLDINC-RUN-006"],
        ["DIS-CLD-OFFBOARD-01", "DOC-CLDINC-RUN-006"],
        [],
        ["2026-08-28", "CLD-U08", "thu hồi"],
        ["Cho rằng CLD-U18 vẫn còn quyền trực ca trong tháng 09/2026"],
        ["offboarding", "oncall_rotation"],
    )

    # 11-16: ACL / Multi-Tenant Isolation / Offboarded / Cross-project DENY
    add(
        "ACL_SECURITY", "access", "access_denied", "CLD-INC", "FL-U01",
        "Trưởng nhóm tích hợp của khách hàng FinLedger (FL-U01) yêu cầu đọc trực tiếp Task Note ca trực nội bộ của CLDINC-9.",
        "DENY: FL-U01 thuộc tenant khách hàng bên ngoài ORG-FINLEDGER, bị chặn hoàn toàn khỏi không gian làm việc nội bộ ORG-CLD.",
        [note_id_by_key["CLDINC-9"]], [], [note_id_by_key["CLDINC-9"]],
        ["DENY", "ORG-FINLEDGER"], ["Tiết lộ nội dung Task Note nội bộ ca trực"], ["cross_tenant_deny"],
    )
    add(
        "ACL_SECURITY", "access", "access_denied", "CLD-INF", "VC-U01",
        "Kỹ sư mạng đối tác hạ tầng VinaCloud (VC-U01) truy cập tài liệu thiết kế PgBouncer nội bộ DOC-CLDINF-DB-002.",
        "DENY: Tài khoản đối tác VC-U01 thuộc ORG-VINACLOUD, không có tư cách thành viên trong ORG-CLD.",
        ["DOC-CLDINF-DB-002"], [], ["DOC-CLDINF-DB-002"],
        ["DENY", "ORG-VINACLOUD"], ["Trích dẫn thông số nội bộ của DOC-CLDINF-DB-002"], ["cross_tenant_deny"],
    )
    add(
        "ACL_SECURITY", "access", "access_denied", "CLD-INC", "CLD-U18",
        "Cựu nhân viên Tô Hải Nam (CLD-U18) truy cập báo cáo hậu kiểm sự cố lễ 02/09 DOC-CLDINC-RCA-002.",
        "DENY: Tài khoản CLD-U18 đã offboard ngày 2026-08-28 (status=SUSPENDED, membership=REMOVED), không còn quyền truy cập tài liệu phát sinh sau ngày nghỉ.",
        ["DOC-CLDINC-RCA-002"], [], ["DOC-CLDINC-RCA-002"],
        ["DENY", "2026-08-28"], ["Cung cấp nội dung DOC-CLDINC-RCA-002 cho CLD-U18"], ["offboarded_deny"],
    )
    add(
        "ACL_SECURITY", "access", "access_denied", "CLD-INF", "CLD-U14",
        "Chuyên viên hỗ trợ Tier-3 Vương Mỹ Linh (CLD-U14, chỉ thuộc dự án CLD-SUP) yêu cầu mở báo cáo nội bộ CLD-INF-WR-W40-M1 của nhóm Hạ tầng.",
        "DENY: CLD-U14 không có Project Membership trong dự án CLD-INF và không phải Organization ADMIN của ORG-CLD.",
        ["CLD-INF-WR-W40-M1"], [], ["CLD-INF-WR-W40-M1"],
        ["DENY", "CLD-INF"], ["Tiết lộ báo cáo thành viên CLD-INF"], ["internal_cross_project_deny"],
    )
    add(
        "ACL_SECURITY", "access", "access_denied", "CLD-OBS", "FL-U03",
        "Kiểm toán viên bảo mật FinLedger (FL-U03) yêu cầu truy vấn danh sách cảnh báo của các tenant khác trên dự án CLD-OBS.",
        "DENY: Cách ly đa tenant nghiêm ngặt không cho phép người dùng ORG-FINLEDGER đọc dữ liệu nội bộ ORG-CLD hoặc thông tin của tenant khác.",
        ["DOC-CLDOBS-ARC-002"], [], ["DOC-CLDOBS-ARC-002"],
        ["DENY"], ["Tiết lộ tên hoặc lưu lượng của tenant khác"], ["multi_tenant_isolation"],
    )
    add(
        "ACL_SECURITY", "access", "access_denied", "CLD-SUP", "CLD-U09",
        "Kỹ sư Telemetry Ngô Thu Trang (CLD-U09, chỉ thuộc CLD-OBS) yêu cầu đọc Task Note đối soát tín dụng SLA nội bộ tại CLDSUP-8.",
        "DENY: CLD-U09 không thuộc danh sách thành viên dự án CLD-SUP.",
        [note_id_by_key["CLDSUP-8"]], [], [note_id_by_key["CLDSUP-8"]],
        ["DENY"], [], ["internal_cross_project_deny"],
    )

    # 17-20: Calibrated Abstention & Scope Boundaries
    add(
        "ABSTENTION", "workspace", "missing_evidence", None, "CLD-U01",
        "Cho biết danh sách các Sprint 2 tuần và điểm vận tốc (velocity story points) của các dự án CloudOps Services.",
        "Không tồn tại dữ liệu Sprint: toàn bộ 4 luồng dự án của CloudOps Services vận hành thuần túy theo phương pháp Kanban liên tục (sprints = [], sprint_id = null), kiểm soát bằng giới hạn WIP và SLE thay vì Sprint.",
        ["DOC-CLDINC-DES-005"], ["DOC-CLDINC-DES-005@v1"], [],
        ["Kanban", "sprint_id = null", "không chia Sprint"], ["Bịa danh sách Sprint 1, Sprint 2 cho CloudOps"], ["calibrated_abstention", "kanban_no_sprint"],
    )
    add(
        "ABSTENTION", "workspace", "missing_evidence", None, "CLD-U02",
        "Truy xuất lịch sử trò chuyện AI Chat của kỹ sư trực ca Bùi Minh Nhật (CLD-U08) trong sáng ngày 02/09/2026.",
        "Không tồn tại trong dataset: theo phạm vi sản phẩm đã chốt, hệ thống không tạo sẵn hay seed lịch sử AI Chat.",
        ["DOC-CLDINC-REQ-001"], ["DOC-CLDINC-REQ-001"], [],
        ["không tạo lịch sử AI Chat"], ["Tự bịa log hội thoại AI Chat"], ["calibrated_abstention", "no_ai_chat"],
    )
    add(
        "ABSTENTION", "workspace", "missing_evidence", None, "CLD-U01",
        "Cho biết mã định danh entity Team của đội On-Call Rotation A trong cơ sở dữ liệu Continuum.",
        "Không có entity Team hoặc Team Membership trong phạm vi dự án; quyền hạn được xác lập trực tiếp qua Organization Membership, Project Membership và Role Assignment.",
        ["DOC-CLDSUP-ARC-002"], ["DOC-CLDSUP-ARC-002"], [],
        ["không có entity Team"], ["Bịa mã TEAM-ONCALL-A"], ["calibrated_abstention", "no_team_entity"],
    )
    add(
        "ABSTENTION", "knowledge", "missing_evidence", "CLD-INF", "CLD-U05",
        "CloudOps có sao chép mã nguồn Python từ kho roxy-wi/IncidentRelay (giấy phép Elastic License 2.0) vào hệ thống nội bộ không?",
        "Không. IncidentRelay (Elastic-2.0, source-available) chỉ được khảo sát để hiểu khái niệm nghiệp vụ lịch trực, gom nhóm cảnh báo và shelve; toàn bộ dữ liệu và tài liệu CloudOps được thiết kế synthetic độc lập.",
        ["DOC-CLDINC-ARC-003"], ["DOC-CLDINC-ARC-003"], [],
        ["Elastic-2.0", "không sao chép", "synthetic"], ["Khẳng định đang phân phối lại mã nguồn IncidentRelay"], ["calibrated_abstention", "license_compliance"],
    )

    # 21-36: Domain Rules across CLD-INC, CLD-OBS, CLD-INF, CLD-SUP
    domain_qa = [
        ("CLD-INC", "CLD-U03", "DOC-CLDINC-REQ-001", "CLDINC-1", "Thời gian ACK tối đa cho sự cố SEV-0 là bao nhiêu phút và thời hạn shelve cảnh báo trùng tối đa là bao lâu?", "SEV-0 yêu cầu ACK trong tối đa 5 phút (quá hạn tự động leo thang sang Secondary On-Call); thao tác shelve bị giới hạn tối đa 120 phút rồi tự động unshelve."),
        ("CLD-INC", "CLD-U03", "DOC-CLDINC-ARC-003", "CLDINC-4", "Bộ gom nhóm AlertGroup gom tối đa bao nhiêu sự kiện lặp và worker nào quét mở lại cảnh báo hết hạn shelve?", "Gom tối đa 500 sự kiện lặp cùng chữ ký lỗi về 01 AlertGroup và do worker CLD-BOT-ALERTGROUP quét mở lại mỗi 60 giây."),
        ("CLD-INC", "CLD-U13", "DOC-CLDINC-API-004", "CLDINC-6", "Điều kiện bắt buộc đối với người nhận ca thay khi gọi POST /api/v1/oncall/overrides là gì?", "Người nhận ca thay bắt buộc đang ở trạng thái ACTIVE trong tổ chức ORG-CLD."),
        ("CLD-INC", "CLD-U07", "DOC-CLDINC-RUN-006", "CLDINC-12", "Trước khi một kỹ sư SRE nghỉ việc hoặc nghỉ ốm dài ngày, sổ tay chỉ huy sự cố yêu cầu cập nhật gì?", "Phải cập nhật lại bảng lịch trực oncall_schedules trước giờ giao ca và thu hồi khóa webhook để không trống cặp Primary + Secondary."),
        ("CLD-OBS", "CLD-U04", "DOC-CLDOBS-REQ-001", "CLDOBS-1", "Mục tiêu SLO khả dụng tháng, độ trễ P99 và ngưỡng burn-rate đánh thức ca trực đêm được quy định ra sao?", "SLO khả dụng 99.95%/tháng, P99 <= 450ms; chỉ đánh thức ca trực đêm khi burn-rate cửa sổ 5 phút và 1 giờ đồng thời vượt 14.4x ngân sách lỗi."),
        ("CLD-OBS", "CLD-U09", "DOC-CLDOBS-ARC-002", "CLDOBS-3", "Pipeline OpenTelemetry lấy mẫu giữ lại bao nhiêu phần trăm trace lỗi 5xx và xử lý dữ liệu nhạy cảm thế nào?", "Giữ lại 100% trace lỗi 5xx hoặc trễ > 1.000ms (10% lưu lượng thường) và tự động xóa Authorization header, cookie, email trước khi lưu."),
        ("CLD-OBS", "CLD-U09", "DOC-CLDOBS-DB-003", "CLDOBS-7", "Vì sao hệ thống cấm đưa user_id và request_id vào nhãn metric chuỗi thời gian?", "Để chống bùng nổ cardinality (giới hạn 50.000 chuỗi hoạt động/job); chỉ cho phép nhãn tổng hợp như tenant_tier và service_name."),
        ("CLD-OBS", "CLD-U12", "DOC-CLDOBS-API-004", "CLDOBS-8", "Sau bao lâu không nhận được tín hiệu ping thì CLD-BOT-HEARTBEAT tự động kích hoạt cảnh báo?", "Sau khi quá ngưỡng interval_sec + grace_sec (180 giây, tương đương 3 chu kỳ 60 giây bị trễ)."),
        ("CLD-INF", "CLD-U05", "DOC-CLDINF-DB-002", "CLDINF-19", "Cấu hình kích thước và giới hạn thời gian câu lệnh giữa auth_pool và reporting_pool trên PgBouncer khác nhau như thế nào?", "auth_pool trên Primary có pool_size=60 và statement_timeout=3000ms; reporting_pool trỏ sang Read-Replica với pool_size=25 và statement_timeout=15000ms."),
        ("CLD-INF", "CLD-U16", "DOC-CLDINF-API-003", "CLDINF-6", "Tần suất quét phát hiện trôi cấu hình ngoài GitOps của worker CLD-BOT-TF-DRIFT là bao lâu?", "Quét tự động định kỳ mỗi 60 phút (hàng giờ) trên toàn bộ module WAF, Security Group và PgBouncer ConfigMap."),
        ("CLD-INF", "CLD-U05", "DOC-CLDINF-REQ-004", "CLDINF-3", "Mục tiêu RPO và RTO tối đa cho cụm cơ sở dữ liệu PostgreSQL đa tenant của CloudOps là bao nhiêu?", "RPO <= 5 phút (nhờ sao lưu WAL liên tục) và RTO <= 20 phút."),
        ("CLD-INF", "CLD-U16", "DOC-CLDINF-TST-005", "CLDINF-20", "Trong bài kiểm thử bão hòa 200 truy vấn báo cáo nặng đồng thời, độ trễ P99 và tỷ lệ thành công của auth_pool đạt mức nào?", "Tỷ lệ đăng nhập thành công qua auth_pool đạt 100% với độ trễ P99 ổn định ở 38ms."),
        ("CLD-SUP", "CLD-U06", "DOC-CLDSUP-REQ-001", "CLDSUP-1", "Khi nào một ticket hỗ trợ khách hàng gắn với sự cố P0/P1 mới được phép chuyển sang trạng thái DONE?", "Chỉ sau khi đã gửi bản tóm tắt RCA được phê duyệt và liên kết rõ mã task khắc phục nguyên nhân gốc (không được đóng khi mới có workaround tạm thời)."),
        ("CLD-SUP", "CLD-U14", "DOC-CLDSUP-API-003", "CLDSUP-7", "Cơ chế bảo vệ nào ngăn việc đăng nhầm IP nội bộ hoặc tên tenant khác lên trang Status Page công khai?", "Endpoint POST /api/v1/status-updates áp dụng bộ lọc regex từ chối HTTP 422 và bắt buộc phê duyệt 4 mắt (author != publisher)."),
        ("CLD-SUP", "CLD-U15", "DOC-CLDSUP-DB-004", "CLDSUP-8", "Điều kiện để đóng một mục hành động phòng ngừa trong bảng postmortem_action_items là gì?", "Phải đính kèm đầy đủ bằng chứng kiểm thử chịu tải hoặc mã PR Terraform đã hợp nhất."),
        ("CLD-SUP", "CLD-U14", "DOC-CLDSUP-RUN-005", "CLDSUP-21", "Có bao nhiêu sự kiện webhook của FinLedger bị chặn hôm 26/09 đã được replay lại và cơ chế nào chống ghi trùng?", "Toàn bộ 148 sự kiện webhook đã được replay thành công 100% nhờ kiểm tra khóa idempotency_key trước khi gửi bù."),
    ]
    for pid, princ, doc_id, t_key, q_txt, a_txt in domain_qa:
        add(
            "DOMAIN_RAG", "knowledge", "normal", pid, princ, q_txt, a_txt,
            [doc_id, task_id_by_key[t_key]], [doc_id, task_id_by_key[t_key]], [],
            [doc_id], [], ["domain_rule", pid.lower()],
        )

    # 37-56: Group Note boundaries, Work Report governance, Kanban WIP, Bot vs Human calendar, Blockers
    extra = [
        ("TASK_NOTE_BOUNDARY", "knowledge", "task_note_not_knowledge", "CLD-INC", "CLD-U03",
         "Ghi chú thao tác khẩn cấp tại Task Note của CLDINC-9 có được coi là tài liệu quy chuẩn vận hành chính thức thay cho DOC-CLDINC-RCA-002 không?",
         "Không. Task Note của CLDINC-9 chỉ lưu vết thực thi tại tab công việc (knowledge_eligible=false, is_temporary_workaround=true), không phải tài liệu tri thức đã phê duyệt.",
         [note_id_by_key["CLDINC-9"], "DOC-CLDINC-RCA-002"], ["DOC-CLDINC-RCA-002"], [note_id_by_key["CLDINC-9"]],
         ["knowledge_eligible=false", "DOC-CLDINC-RCA-002"], ["Dùng Task Note làm quy chuẩn chính thức"], ["group_note_boundary"]),
        ("WORK_REPORT_FLOW", "workspace", "report_governance", "CLD-INC", "CLD-U01",
         "Báo cáo tuần cấp Leader CLD-INC-WR-W40-L1 của Lê Hoàng Bách (CLD-U03) do vai trò nào phê duyệt?",
         "Do Organization ADMIN Manager (CLD-U01 hoặc CLD-U02) phê duyệt theo đúng luồng Leader -> Manager của Continuum.",
         ["CLD-INC-WR-W40-L1"], ["CLD-INC-WR-W40-L1"], [], ["LEADER", "ADMIN"], [], ["leader_manager_flow"]),
        ("WORK_REPORT_REJECTED", "knowledge", "draft_vs_approved", "CLD-OBS", "CLD-U04",
         "Vì sao báo cáo tuần CLD-OBS-WR-W40-M2 bị từ chối (REJECTED) và nó có đủ điều kiện đưa vào kho tri thức không?",
         "Bị REJECTED do trích dẫn nhầm tài liệu DOC-CLDOBS-SLI-006 đã bị bác bỏ và thiếu bằng chứng staging; do đó knowledge_eligible=false.",
         ["CLD-OBS-WR-W40-M2"], ["CLD-OBS-WR-W40-M1"], ["CLD-OBS-WR-W40-M2"], ["REJECTED", "knowledge_eligible=false"], [], ["rejected_report"]),
        ("WORK_REPORT_CHANGES", "workspace", "report_governance", "CLD-INF", "CLD-U01",
         "Trạng thái hiện tại của báo cáo tuần Leader CLD-INF-WR-W41-L1 là gì?",
         "Đang ở trạng thái CHANGES_REQUESTED để bổ sung chi tiết tiến độ đóng thẻ hậu kiểm WAF CLDINF-24 theo yêu cầu của Manager.",
         ["CLD-INF-WR-W41-L1"], [], ["CLD-INF-WR-W41-L1"], ["CHANGES_REQUESTED"], [], ["report_changes_requested"]),
        ("WORK_REPORT_OVERDUE", "workspace", "report_governance", "CLD-INC", "CLD-U03",
         "Báo cáo ngày CLD-INC-WR-D1014-M2 đang mang trạng thái nộp bài nào trên danh sách kiểm tra kỳ báo cáo?",
         "Đang là bản nháp quá hạn (status=DRAFT, is_overdue=true, roster_submission_state=OVERDUE).",
         ["CLD-INC-WR-D1014-M2"], [], ["CLD-INC-WR-D1014-M2"], ["DRAFT", "OVERDUE"], [], ["overdue_report"]),
        ("WORK_REPORT_PENDING", "workspace", "report_governance", "CLD-SUP", "CLD-U06",
         "Báo cáo ngày 15/10/2026 mã CLD-SUP-WR-D1015-M1 đã được Lead CLD-U06 duyệt chưa?",
         "Chưa; báo cáo đang ở trạng thái PENDING_REVIEW chờ xét duyệt nên knowledge_eligible=false.",
         ["CLD-SUP-WR-D1015-M1"], [], ["CLD-SUP-WR-D1015-M1"], ["PENDING_REVIEW"], [], ["pending_report"]),
        ("DAILY_LEADER_REPORT", "knowledge", "normal", "CLD-OBS", "CLD-U01",
         "Báo cáo ngày Leader CLD-OBS-WR-D1014-L1 ngày 14/10/2026 đã xác nhận nội dung gì?",
         "Lead CLD-U04 đã kiểm tra ngân sách lỗi (Error Budget) tháng 10 của phân hệ xác thực và cổng webhook, được Manager phê duyệt (APPROVED).",
         ["CLD-OBS-WR-D1014-L1"], ["CLD-OBS-WR-D1014-L1"], [], ["Error Budget", "APPROVED"], [], ["daily_leader_report"]),
        ("DAILY_MEMBER_APPROVED", "knowledge", "normal", "CLD-INF", "CLD-U05",
         "Kết quả kiểm tra đối soát drift trong báo cáo ngày CLD-INF-WR-D1013-M1 ngày 13/10/2026 là bao nhiêu sai lệch?",
         "Ghi nhận 0 sai lệch ngoài GitOps từ báo cáo hàng giờ của CLD-BOT-TF-DRIFT và đã được Lead CLD-U05 phê duyệt.",
         ["CLD-INF-WR-D1013-M1"], ["CLD-INF-WR-D1013-M1"], [], ["0 sai lệch", "CLD-BOT-TF-DRIFT"], [], ["daily_member_report"]),
        ("KANBAN_WIP_POLICY", "knowledge", "normal", "CLD-INC", "CLD-U03",
         "Theo thiết kế Kanban tại DOC-CLDINC-DES-005 v1, giới hạn WIP cột IN_PROGRESS và làn EXPEDITE_P0 của bảng CLD-INC là bao nhiêu?",
         "Giới hạn tối đa 5 thẻ ở cột IN_PROGRESS và tối đa 1 thẻ trên làn khẩn cấp EXPEDITE_P0.",
         ["DOC-CLDINC-DES-005@v1"], ["DOC-CLDINC-DES-005@v1"], ["DOC-CLDINC-DES-005@v2"], ["5 thẻ", "EXPEDITE_P0"], [], ["kanban_wip"]),
        ("BOT_VS_HUMAN_TIME", "workspace", "temporal_audit", "CLD-INC", "CLD-U03",
         "Vì sao hệ thống ghi nhận sự kiện khởi tạo CLDINC-9 lúc 09:12 sáng ngày nghỉ lễ Quốc khánh 02/09/2026 là hợp lệ?",
         f"Vì sự kiện phát hiện lúc 09:12+07:00 do bot tự động 24/7 CLD-BOT-HEARTBEAT tạo (work_mode=automated_bot), và các thao tác xử lý tiếp theo do kỹ sư CLD-U08 thực hiện trong ca trực lễ hợp lệ OC-2026-0902-HOLIDAY (work_mode=oncall_incident_response).",
         [task_id_by_key["CLDINC-9"], "DOC-CLDINC-RCA-002"], [task_id_by_key["CLDINC-9"], "DOC-CLDINC-RCA-002"], [], ["CLD-BOT-HEARTBEAT", "OC-2026-0902-HOLIDAY"], [], ["temporal_audit", "bot_24x7"]),
        ("EVENING_INCIDENT_AUG18", "workspace", "temporal_audit", "CLD-INF", "CLD-U05",
         "Sự cố lỗi ghi trên pod cũ tối 18/08/2026 (INC-2026-0818) được xử lý giảm nhẹ ngay trong ca trực tối bằng task nào?",
         f"Được xử lý tại task {task_id_by_key['CLDINF-9']} (CLDINF-9) trong ca trực giám sát bảo trì tối OC-2026-0818-EVENING bằng cách quay lui bản triển khai và hủy phiên DDL đang giữ khóa.",
         [task_id_by_key["CLDINF-9"], "DOC-CLDINF-DB-002"], [task_id_by_key["CLDINF-9"], "DOC-CLDINF-DB-002"], ["DOC-CLDINF-RUN-006-LEGACY"], ["CLDINF-9", "18/08/2026"], [], ["evening_oncall"]),
        ("BLOCKED_TASK_TRACE", "workspace", "blocker_analysis", "CLD-INC", "CLD-U03",
         "Thẻ Kanban CLDINC-31 đang bị chặn (BLOCKED) vì nguyên nhân gì?",
         f"Task {task_id_by_key['CLDINC-31']} (CLDINC-31) đang BLOCKED do chờ đội mạng của đối tác hạ tầng VinaCloud gửi biên bản xác nhận định tuyến dự phòng BGP liên vùng.",
         [task_id_by_key["CLDINC-31"]], [task_id_by_key["CLDINC-31"], "CLD-INC-WR-D1014-L1"], [], ["BLOCKED", "VinaCloud", "CLDINC-31"], [], ["blocker_analysis"]),
        ("BLOCKED_SLA_SIGN", "workspace", "blocker_analysis", "CLD-SUP", "CLD-U06",
         "Điểm nghẽn nào đang làm thẻ CLDSUP-31 ở trạng thái BLOCKED trên bảng hỗ trợ khách hàng?",
         f"Task {task_id_by_key['CLDSUP-31']} (CLDSUP-31) đang chờ đại diện vận hành khách hàng FinLedger ký xác nhận biên bản đối soát tín dụng SLA quý 3.",
         [task_id_by_key["CLDSUP-31"]], [task_id_by_key["CLDSUP-31"]], [], ["BLOCKED", "FinLedger", "CLDSUP-31"], [], ["blocker_analysis"]),
        ("SUBTASK_HIERARCHY", "workspace", "subtask_hierarchy", "CLD-INF", "CLD-U05",
         "Subtask kiểm thử chịu tải PgBouncer CLDINF-20 là con trực tiếp 1 cấp của thẻ Kanban nào?",
         f"Subtask {task_id_by_key['CLDINF-20']} (CLDINF-20) là con trực tiếp 1 cấp của thẻ khắc phục gốc {task_id_by_key['CLDINF-19']} (CLDINF-19).",
         [task_id_by_key["CLDINF-19"], task_id_by_key["CLDINF-20"]], [task_id_by_key["CLDINF-19"], task_id_by_key["CLDINF-20"], "DOC-CLDINF-TST-005"], [], ["CLDINF-19", "CLDINF-20"], [], ["subtask_1_level"]),
        ("CANCELLED_TASK_REASON", "workspace", "cancelled_scope", "CLD-OBS", "CLD-U04",
         "Lý do thẻ Kanban CLDOBS-30 bị chuyển sang trạng thái CANCELLED là gì?",
         f"Task {task_id_by_key['CLDOBS-30']} (CLDOBS-30) bị hủy sau khi tài liệu đề xuất cảnh báo CPU > 65% trong 30 giây (DOC-CLDOBS-SLI-006) bị bác bỏ do sinh 42% cảnh báo giả.",
         [task_id_by_key["CLDOBS-30"], "DOC-CLDOBS-SLI-006"], [task_id_by_key["CLDOBS-30"], "DOC-CLDOBS-REQ-001"], ["DOC-CLDOBS-SLI-006@v1"], ["CANCELLED", "42%"], [], ["cancelled_task"]),
        ("ORG_ADMIN_VISIBILITY", "workspace", "org_admin_visibility", "CLD-INF", "CLD-U02",
         "Head of SaaS Support Trần Phương Thảo (CLD-U02, vai trò Organization ADMIN) có quyền đọc tài liệu kiến trúc hạ tầng DOC-CLDINF-ARC-001 không?",
         "Có. Với vai trò Organization ADMIN được gán tường minh của ORG-CLD, CLD-U02 có quyền rà soát cấp tổ chức trên tất cả dự án thuộc ORG-CLD.",
         ["DOC-CLDINF-ARC-001"], ["DOC-CLDINF-ARC-001"], [], ["ADMIN", "ORG-CLD"], [], ["org_admin_access"]),
        ("WAF_FOLLOWUP_STATUS", "workspace", "task_status", "CLD-INF", "CLD-U05",
         "Tính đến ngày chốt dataset 2026-10-16, thẻ đồng bộ hoàn toàn rule WAF vào Terraform (CLDINF-24) đã DONE hay đang ở cột nào?",
         f"Tính đến 2026-10-16, task {task_id_by_key['CLDINF-24']} (CLDINF-24) đang ở trạng thái IN_REVIEW chờ xác nhận dải IP dự phòng thứ hai từ đội bảo mật FinLedger.",
         [task_id_by_key["CLDINF-24"]], [task_id_by_key["CLDINF-24"], "CLD-INF-WR-W41-L1"], [], ["IN_REVIEW", "CLDINF-24"], ["Khẳng định CLDINF-24 đã đóng hoàn tất từ tháng 09"], ["as_of_state"]),
        ("STORM_PRIMARY_UNAVAILABLE", "workspace", "disruption_handover", "CLD-INC", "CLD-U03",
         "Vì sao kỹ sư trực chính Hoàng Gia Bảo (CLD-U07) không phải là người bấm ACK sự cố SEV-0 sáng 02/09/2026?",
         "Do mưa bão lớn làm đứt cáp quang gia đình và mất sóng cục bộ nơi CLD-U07 cư trú từ 08:00 đến 23:00 ngày 02/09 (DIS-CLD-STORM-01), nên sau 5 phút hệ thống tự động chuyển quyền sang Secondary On-Call CLD-U08.",
         ["DIS-CLD-STORM-01", "DOC-CLDINC-RCA-002"], ["DIS-CLD-STORM-01", "DOC-CLDINC-RCA-002"], [], ["DIS-CLD-STORM-01", "CLD-U07", "CLD-U08"], [], ["storm_escalation"]),
        ("TENANT_PRIVACY_COMMS", "knowledge", "normal", "CLD-SUP", "CLD-U02",
         "Khi gửi báo cáo sự cố cho khách hàng FinLedger, chuyên viên CloudOps có được đính kèm log lưu lượng của các tenant khác cùng cụm để chứng minh tải cao không?",
         "Tuyệt đối không. Theo DOC-CLDSUP-REQ-001 và DOC-CLDSUP-API-003, mọi bản tin và báo cáo gửi khách hàng phải cách ly hoàn toàn, cấm tiết lộ tên, IP hay lưu lượng của bất kỳ tenant nào khác.",
         ["DOC-CLDSUP-REQ-001", "DOC-CLDSUP-API-003"], ["DOC-CLDSUP-REQ-001", "DOC-CLDSUP-API-003"], [], ["cấm tiết lộ", "tenant"], [], ["tenant_privacy"]),
        ("DB_REVIEW_LINEAGE", "knowledge", "version_conflict", "CLD-INF", "CLD-U05",
         "Phiên bản v1 của tài liệu chuẩn vận hành CSDL DOC-CLDINF-DB-002 đã được yêu cầu bổ sung những gì trước khi v2 được phê duyệt?",
         "Lead CLD-U05 yêu cầu bổ sung cấu hình lock_timeout=2000ms cho các câu lệnh DDL và thiết kế tách riêng hạn ngạch pool PgBouncer cho luồng xác thực; các nội dung này đã được hoàn thiện và phê duyệt tại bản v2.",
         ["DOC-CLDINF-DB-002@v1", "DOC-CLDINF-DB-002@v2"], ["DOC-CLDINF-DB-002"], ["DOC-CLDINF-DB-002@v1"], ["lock_timeout=2000ms", "PgBouncer", "v2"], [], ["review_history"]),
    ]
    for row in extra:
        add(*row)

    assert len(cases) == 56, f"Expected 56 CloudOps evaluation cases, got {len(cases)}"
    return cases
