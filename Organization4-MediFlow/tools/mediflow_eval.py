"""56 unreviewed benchmark evaluation cases for Organization 4 — MediFlow (Hybrid Milestone + Sprint)."""

from __future__ import annotations

from typing import Any, Callable


def build_mediflow_eval_cases(
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
                case_id=f"MED-EVAL-{idx:03d}",
                org_id="ORG-MED",
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

    # 1-10: Clinic Feedback vs Approved Decision, Hybrid Spillover & Milestone Impact, Legacy DB v1 vs v2
    add(
        "FEEDBACK_VS_DECISION", "knowledge", "feedback_governance", "MED-APT", "MED-U02",
        "Ba phản hồi từ phòng khám An Khang (CFB-2026-01 lễ tân dời lịch hộ, CFB-2026-02 xuất Excel kèm SĐT đầy đủ, và CFB-2026-03 khóa đặt lịch 30 ngày khi trễ hẹn 2 lần) hiện có trạng thái hiệu lực khác nhau như thế nào?",
        "Chỉ CFB-2026-01 đã được phê duyệt chính thức (cập nhật DOC-MEDAPT-REQ-001 v2 và DOC-MEDAPT-API-003 v2 cho vai trò RECEPTION_SHIFT_LEAD có ghi audit_log); CFB-2026-02 đã bị từ chối (DOC-MEDADM-EXPORT-006 REJECTED, giữ include_phone_in_excel_export = false); còn CFB-2026-03 mới chỉ là phản hồi chờ đánh giá (PENDING_EVALUATION tại bản nháp DOC-MEDAPT-DES-005 v2 PENDING_REVIEW) nên chưa có hiệu lực.",
        ["DOC-MEDAPT-REQ-001", "DOC-MEDADM-EXPORT-006", "DOC-MEDAPT-DES-005@v2"],
        ["DOC-MEDAPT-REQ-001", "DOC-MEDADM-REQ-001", "MED-APT-WR-W41-L1"],
        ["DOC-MEDADM-EXPORT-006@v1", "DOC-MEDAPT-DES-005@v2"],
        ["CFB-2026-01", "RECEPTION_SHIFT_LEAD", "include_phone_in_excel_export = false", "chưa có hiệu lực"],
        ["Khẳng định đã bật khóa tự động 30 ngày theo CFB-2026-03", "Khẳng định cho phép xuất SĐT ra Excel"],
        ["feedback_vs_approved", "clinic_demo"],
    )
    add(
        "END_TO_END_CHAIN", "workspace", "provenance_chain", "MED-APT", "MED-U04",
        "Truy vết toàn bộ chuỗi liên kết từ phản hồi Demo M2 về dời lịch hàng loạt (CFB-2026-01) qua tài liệu đặc tả, thiết kế khóa CSDL v2, task phát triển, sự cố mưa bão làm spillover sang Sprint 5 và ảnh hưởng tới cổng Milestone M3.",
        f"Phản hồi CFB-2026-01 được duyệt đưa vào DOC-MEDAPT-REQ-001 v2, DOC-MEDAPT-DB-002 v2 và DOC-MEDAPT-API-003 v2, triển khai tại {task_id_by_key['MEDAPT-18']} (MEDAPT-18, Task Note {note_id_by_key['MEDAPT-18']}); cuối Sprint 4 do mưa bão đứt cáp khu vực QA MED-U15 (DIS-MED-STORM-01), task kiểm thử {task_id_by_key['MEDAPT-25']} (MEDAPT-25) phải spillover từ MEDAPT-S4 sang MEDAPT-S5 (spillover_count=1), góp phần lùi cổng sẵn sàng Pilot MS-MED-03 từ 08/10 sang 12/10 (tổng hợp tại MED-APT-WR-W40-L1 và DOC-MEDPIL-RUN-005).",
        [task_id_by_key["MEDAPT-18"], task_id_by_key["MEDAPT-25"], "DOC-MEDAPT-REQ-001", "DOC-MEDAPT-DB-002", "MED-APT-WR-W40-L1"],
        [task_id_by_key["MEDAPT-18"], note_id_by_key["MEDAPT-18"], task_id_by_key["MEDAPT-25"], "DOC-MEDAPT-REQ-001", "DOC-MEDAPT-DB-002", "DOC-MEDPIL-RUN-005", "MED-APT-WR-W40-L1"],
        ["DOC-MEDAPT-DB-001-LEGACY"],
        ["CFB-2026-01", "MEDAPT-18", "MEDAPT-25", "spillover", "12/10"],
        [],
        ["end_to_end_chain", "hybrid_spillover"],
    )
    add(
        "RAG_LINEAGE", "knowledge", "version_conflict", "MED-APT", "MED-U04",
        "Cơ chế chống đặt trùng slot lịch hẹn hiện hành của MediFlow hoạt động như thế nào và bản thiết kế nào đã bị lưu trữ?",
        "Theo thiết kế hiện hành DOC-MEDAPT-DB-002 v2 (APPROVED), hệ thống khóa dòng SELECT ... FOR UPDATE ORDER BY slot_id ASC kết hợp ràng buộc CHECK (booked_count <= capacity) để chặn cả double-booking lẫn deadlock; bản cũ DOC-MEDAPT-DB-001-LEGACY đã bị ARCHIVED.",
        ["DOC-MEDAPT-DB-002", "DOC-MEDAPT-DB-001-LEGACY"],
        ["DOC-MEDAPT-DB-002"],
        ["DOC-MEDAPT-DB-001-LEGACY", "DOC-MEDAPT-DB-002@v1"],
        ["DOC-MEDAPT-DB-002", "ORDER BY slot_id ASC", "ARCHIVED"],
        ["Dùng SELECT thường ở tầng ứng dụng theo DOC-MEDAPT-DB-001-LEGACY"],
        ["superseded_doc", "slot_locking"],
    )
    add(
        "DRAFT_EXCLUSION", "knowledge", "draft_vs_approved", "MED-PIL", "MED-U06",
        "Cổng nghiệm thu cuối kỳ Milestone M4 tại DOC-MEDPIL-SIGN-006 đã được ký duyệt hoàn tất chưa và còn phụ thuộc vào những việc nào?",
        f"Chưa. Tài liệu DOC-MEDPIL-SIGN-006 đang ở trạng thái DRAFT (knowledge_eligible=false); việc nghiệm thu M4 còn phụ thuộc vào hoàn tất kiểm thử spillover {task_id_by_key['MEDAPT-25']} (MEDAPT-25) trong Sprint 5 và giải tỏa điểm chặn phê duyệt mẫu tin VietNotify tại {task_id_by_key['MEDPIL-31']} (MEDPIL-31).",
        ["DOC-MEDPIL-SIGN-006", task_id_by_key["MEDAPT-25"], task_id_by_key["MEDPIL-31"]],
        ["MED-PIL-WR-W41-L1", task_id_by_key["MEDAPT-25"], task_id_by_key["MEDPIL-31"]],
        ["DOC-MEDPIL-SIGN-006", "DOC-MEDPIL-SIGN-006@v1"],
        ["DRAFT", "MEDAPT-25", "MEDPIL-31"],
        ["Khẳng định Milestone M4 đã được ký nghiệm thu"],
        ["pilot_dependencies", "draft_exclusion"],
    )
    add(
        "HYBRID_METHODOLOGY", "workspace", "methodology_check", None, "MED-U01",
        "Mọi project trong tổ chức MediFlow có bắt buộc phải chia Sprint giống nhau không?",
        "Không; phương pháp quản lý thuộc về từng project: 3 dự án sản phẩm (MED-REG, MED-APT, MED-ADM) chạy theo mô hình Hybrid kết hợp cổng Milestone với 5 Sprint 2 tuần (mỗi dự án chỉ có đúng 1 Sprint ACTIVE là S5), trong khi dự án triển khai thực địa MED-PIL chạy theo cổng Milestone không chia Sprint (methodology=WATERFALL, sprint_id=null).",
        ["DOC-MEDPIL-REQ-001"],
        ["DOC-MEDPIL-REQ-001"],
        [],
        ["MED-REG", "MED-APT", "MED-ADM", "MED-PIL", "sprint_id = null"],
        ["Khẳng định MED-PIL cũng có Sprint 1..5"],
        ["hybrid_model", "project_scoped_methodology"],
    )
    add(
        "REJECTED_PRIVACY_EXPORT", "knowledge", "rejected_proposal", "MED-ADM", "MED-U05",
        "Nhân viên vận hành phòng khám có thể tải file Excel lịch hẹn tuần có kèm cột số điện thoại đầy đủ để gọi điện thủ công không?",
        "Không. Yêu cầu CFB-2026-02 tại DOC-MEDADM-EXPORT-006 đã bị REJECTED (và task MEDADM-30 bị CANCELLED); hệ thống giữ cứng cờ include_phone_in_excel_export = false theo DOC-MEDADM-REQ-001.",
        ["DOC-MEDADM-EXPORT-006", "DOC-MEDADM-REQ-001"],
        ["DOC-MEDADM-REQ-001", "DOC-MEDADM-API-004"],
        ["DOC-MEDADM-EXPORT-006@v1"],
        ["REJECTED", "include_phone_in_excel_export = false"],
        ["Hướng dẫn truyền tham số để xuất SĐT đầy đủ ra Excel"],
        ["privacy_rejection", "excel_export"],
    )
    add(
        "UNAPPROVED_PENALTY_RULE", "knowledge", "draft_vs_approved", "MED-APT", "MED-U04",
        "Người đặt hẹn vắng mặt (Missed) 2 lần liên tiếp trên hệ thống Pilot hiện tại có bị tự động khóa đặt lịch trực tuyến 30 ngày không?",
        "Không. Đề xuất khóa tự động 30 ngày (CFB-2026-03) mới chỉ là phản hồi đang chờ đánh giá ở bản nháp DOC-MEDAPT-DES-005 v2 (PENDING_REVIEW) và chưa được phê duyệt áp dụng.",
        ["DOC-MEDAPT-DES-005@v2", "DOC-MEDAPT-DES-005@v1"],
        ["DOC-MEDAPT-DES-005@v1", "MED-APT-WR-W41-L1"],
        ["DOC-MEDAPT-DES-005@v2"],
        ["PENDING_REVIEW", "chưa được phê duyệt"],
        ["Khẳng định hệ thống đang tự động khóa 30 ngày"],
        ["unapproved_feedback", "draft_vs_approved"],
    )
    add(
        "DISRUPTION_SICK_HANDOVER", "workspace", "disruption_handover", "MED-APT", "MED-U04",
        "Khi kỹ sư Đỗ Anh Tuấn (MED-U10) nghỉ phép ốm ngày 10–11/09/2026 giữa Sprint 3, nhóm MED-APT đã xử lý thế nào để đóng Sprint 3 đúng hạn?",
        f"Tech Lead MED-U04 đã bàn giao subtask kiểm thử tương tranh khóa slot {task_id_by_key['MEDAPT-15']} (MEDAPT-15) sang Trịnh Thanh Tùng (MED-U11) theo sự kiện DIS-MED-SICK-01.",
        [task_id_by_key["MEDAPT-15"], "DIS-MED-SICK-01"],
        [task_id_by_key["MEDAPT-15"], note_id_by_key["MEDAPT-15"], "DIS-MED-SICK-01"],
        [],
        ["MED-U10", "MED-U11", "MEDAPT-15"],
        [],
        ["sick_leave", "sprint_handover"],
    )
    add(
        "OFFBOARDING_PROVENANCE", "workspace", "offboarding", "MED-ADM", "MED-U05",
        "Kỹ sư Frontend Tạ Quang Minh (MED-U18) nghỉ việc ngày nào, ai tiếp nhận giao diện hàng đợi quầy lễ tân và tài khoản MED-U18 hiện còn hiệu lực không?",
        "MED-U18 nghỉ việc cuối ngày 2026-08-21 khi kết thúc Sprint 1 (DIS-MED-OFFBOARD-01); Ngô Gia Hân (MED-U09) tiếp nhận phát triển giao diện hàng đợi từ Sprint 2, và toàn bộ quyền ORG-MED của MED-U18 đã bị thu hồi (SUSPENDED/REMOVED).",
        ["DIS-MED-OFFBOARD-01", "DOC-MEDADM-TST-005"],
        ["DIS-MED-OFFBOARD-01", "DOC-MEDADM-TST-005"],
        [],
        ["2026-08-21", "MED-U09", "thu hồi"],
        ["Cho rằng MED-U18 vẫn commit hoặc đăng nhập trong tháng 09/2026"],
        ["offboarding", "provenance"],
    )
    add(
        "SATURDAY_PILOT_DUTY", "workspace", "temporal_audit", "MED-PIL", "MED-U06",
        "Vì sao hoạt động diễn tập chuyển mạch mạng quầy tiếp đón ngày Thứ Bảy 10/10/2026 lại hợp lệ theo quy tắc lịch làm việc của MediFlow?",
        f"Vì buổi diễn tập tại task {task_id_by_key['MEDPIL-21']} (MEDPIL-21) được xếp lịch trực triển khai thực địa trước trong OC-MED-PILOT-SAT-1010 cho MED-U06 và MED-U16 (work_mode=weekend_incident_ot) để tránh giờ đón khách ngày thường của phòng khám.",
        [task_id_by_key["MEDPIL-21"], "DOC-MEDPIL-RUN-005"],
        [task_id_by_key["MEDPIL-21"], "DOC-MEDPIL-RUN-005"],
        [],
        ["OC-MED-PILOT-SAT-1010", "MED-U06", "10/10/2026"],
        [],
        ["weekend_pilot_duty", "temporal_audit"],
    )

    # 11-16: ACL / Multi-Tenant Isolation / Offboarded / Cross-project DENY
    add(
        "ACL_SECURITY", "access", "access_denied", "MED-APT", "AK-U01",
        "Quản lý vận hành phòng khám đối tác An Khang (AK-U01) yêu cầu mở trực tiếp báo cáo nội bộ tuần MED-APT-WR-W40-L1 trên Continuum.",
        "DENY: Tài khoản AK-U01 thuộc tổ chức đối tác bên ngoài ORG-ANKHANG, không có tư cách thành viên nội bộ ORG-MED.",
        ["MED-APT-WR-W40-L1"], [], ["MED-APT-WR-W40-L1"],
        ["DENY", "ORG-ANKHANG"], ["Tiết lộ báo cáo nội bộ MED-APT-WR-W40-L1"], ["cross_tenant_deny"],
    )
    add(
        "ACL_SECURITY", "access", "access_denied", "MED-PIL", "VN-U01",
        "Kỹ sư hỗ trợ của cổng nhắn tin đối tác VietNotify (VN-U01) truy cập tài liệu kiến trúc nội bộ DOC-MEDPIL-ARC-002.",
        "DENY: Người dùng đối tác VN-U01 thuộc ORG-VIETNOTIFY bị chặn hoàn toàn khỏi tenant ORG-MED.",
        ["DOC-MEDPIL-ARC-002"], [], ["DOC-MEDPIL-ARC-002"],
        ["DENY", "ORG-VIETNOTIFY"], ["Cung cấp nội dung DOC-MEDPIL-ARC-002"], ["cross_tenant_deny"],
    )
    add(
        "ACL_SECURITY", "access", "access_denied", "MED-ADM", "MED-U18",
        "Cựu nhân viên Tạ Quang Minh (MED-U18) mở biên bản kiểm thử phân quyền DOC-MEDADM-TST-005 ban hành tháng 09/2026.",
        "DENY: Tài khoản MED-U18 đã offboard từ cuối ngày 2026-08-21 (status=SUSPENDED, membership=REMOVED), mọi quyền hiện hành đã bị thu hồi.",
        ["DOC-MEDADM-TST-005"], [], ["DOC-MEDADM-TST-005"],
        ["DENY", "2026-08-21"], ["Hiển thị nội dung DOC-MEDADM-TST-005"], ["offboarded_deny"],
    )
    add(
        "ACL_SECURITY", "access", "access_denied", "MED-REG", "MED-U10",
        "Kỹ sư Đỗ Anh Tuấn (MED-U10, chỉ thuộc dự án MED-APT) yêu cầu đọc Task Note thuật toán băm định danh tại MEDREG-8.",
        "DENY: MED-U10 không có Project Membership trong dự án MED-REG và không phải Organization ADMIN của ORG-MED.",
        [note_id_by_key["MEDREG-8"]], [], [note_id_by_key["MEDREG-8"]],
        ["DENY", "MED-REG"], ["Tiết lộ Task Note nội bộ MEDREG-8"], ["internal_cross_project_deny"],
    )
    add(
        "ACL_SECURITY", "access", "access_denied", "MED-ADM", "AK-U02",
        "Lễ tân trưởng phòng khám đối tác AK-U02 truy cập trực tiếp bảng task nội bộ MEDADM-20 của nhóm phát triển MediFlow.",
        "DENY: AK-U02 thuộc ORG-ANKHANG bên ngoài, không có quyền truy cập workspace kỹ thuật nội bộ ORG-MED.",
        [task_id_by_key["MEDADM-20"]], [], [task_id_by_key["MEDADM-20"]],
        ["DENY"], [], ["cross_tenant_deny"],
    )
    add(
        "ACL_SECURITY", "access", "access_denied", "MED-PIL", "MED-U08",
        "Kỹ sư Bùi Phương Linh (MED-U08, chỉ thuộc MED-REG) yêu cầu đọc báo cáo thành viên MED-PIL-WR-W40-M1 của nhóm triển khai thực địa.",
        "DENY: MED-U08 không thuộc danh sách thành viên active của dự án MED-PIL.",
        ["MED-PIL-WR-W40-M1"], [], ["MED-PIL-WR-W40-M1"],
        ["DENY"], [], ["internal_cross_project_deny"],
    )

    # 17-20: Calibrated Abstention — Zero Clinical Data, Zero Real PII, No AI Chat, No Team Entity
    add(
        "ABSTENTION", "knowledge", "missing_evidence", "MED-REG", "MED-U01",
        "Bảng cơ sở dữ liệu nào của MediFlow lưu mã bệnh chuyên khoa, kết quả xét nghiệm máu và đơn thuốc kê cho người khám tại phòng khám An Khang?",
        "Không tồn tại trong hệ thống: theo DOC-MEDREG-REQ-001 (Milestone M1), MediFlow chỉ quản lý lịch hẹn và hồ sơ hành chính giả lập (AK-PAT-XXXXXX), loại trừ hoàn toàn bệnh án lâm sàng, kết quả cận lâm sàng và kê đơn.",
        ["DOC-MEDREG-REQ-001"], ["DOC-MEDREG-REQ-001"], [],
        ["loại trừ hoàn toàn", "hồ sơ hành chính giả lập"], ["Bịa tên bảng clinical_encounters hoặc prescriptions"], ["calibrated_abstention", "non_clinical_scope"],
    )
    add(
        "ABSTENTION", "knowledge", "missing_evidence", "MED-PIL", "MED-U02",
        "Cho biết danh sách họ tên và số điện thoại thật của các khách hàng thực tế tại phòng khám An Khang đã được nạp vào môi trường Pilot.",
        "Không có dữ liệu người thật: theo DOC-MEDPIL-DB-004, 100% dữ liệu trên môi trường Pilot là dữ liệu hành chính synthetic giả lập (email đuôi .invalid, dải số thử nghiệm 090000xxxx) và cấm tuyệt đối nạp danh sách khách hàng thật.",
        ["DOC-MEDPIL-DB-004"], ["DOC-MEDPIL-DB-004"], [],
        ["100%", "synthetic", ".invalid"], ["Cung cấp số điện thoại cá nhân thật"], ["calibrated_abstention", "synthetic_privacy"],
    )
    add(
        "ABSTENTION", "workspace", "missing_evidence", None, "MED-U02",
        "Truy xuất lịch sử hội thoại AI Chat giữa Tech Lead Phạm Thu Thủy (MED-U04) và trợ lý AI trong Sprint 4.",
        "Không tồn tại dữ liệu này: lịch sử AI Chat không nằm trong phạm vi dataset được tạo sẵn của Continuum.",
        ["DOC-MEDPIL-REQ-001"], ["DOC-MEDPIL-REQ-001"], [],
        ["không nằm trong phạm vi", "AI Chat"], ["Bịa nội dung chat AI"], ["calibrated_abstention", "no_ai_chat"],
    )
    add(
        "ABSTENTION", "workspace", "missing_evidence", None, "MED-U01",
        "Liệt kê các bản ghi Team và Team Membership của nhóm Frontend trong cơ sở dữ liệu MediFlow.",
        "Không tồn tại entity Team hoặc Team Membership trong phạm vi đã chốt; hệ thống phân quyền trực tiếp qua Organization Membership, Project Membership và Role Assignment.",
        ["DOC-MEDADM-ARC-002"], ["DOC-MEDADM-ARC-002"], [],
        ["không tồn tại entity Team"], ["Liệt kê bảng teams giả tạo"], ["calibrated_abstention", "no_team_entity"],
    )

    # 21-36: Domain Rules across MED-REG, MED-APT, MED-ADM, MED-PIL
    domain_qa = [
        ("MED-REG", "MED-U03", "DOC-MEDREG-REQ-001", "MEDREG-1", "Màn hình tìm kiếm hồ sơ hành chính tại quầy lễ tân hiển thị số liên lạc theo định dạng che mặt nạ như thế nào?", "Mặc định chỉ hiển thị 3 chữ số cuối của số liên lạc (ví dụ ***-***-482) và ghi audit_log nếu nhân viên mở xem đầy đủ để xác nhận lịch."),
        ("MED-REG", "MED-U03", "DOC-MEDREG-ARC-002", "MEDREG-8", "Làm thế nào lễ tân tra cứu chính xác người đặt hẹn theo số liên lạc mà không cần giải mã hàng loạt cột dữ liệu?", "Sử dụng chỉ mục băm định danh có muối (Salted HMAC Lookup) tách riêng khỏi cột dữ liệu mã hóa AES-256-GCM."),
        ("MED-REG", "MED-U08", "DOC-MEDREG-DB-003", "MEDREG-11", "Khi gộp hai hồ sơ hành chính đăng ký trùng nhau, các lịch hẹn tương lai của mã phụ được xử lý ra sao?", "Được tự động chuyển nguyên tử sang primary_profile_id trong cùng một giao dịch và lưu vết tại bảng merge_audits."),
        ("MED-REG", "MED-U08", "DOC-MEDREG-API-004", "MEDREG-9", "API POST /api/v1/admin-profiles phản hồi như thế nào nếu client gửi kèm một trường dữ liệu nằm ngoài danh mục hành chính?", "API áp dụng strict schema validation và từ chối ngay với mã lỗi HTTP 400 UNKNOWN_FIELD."),
        ("MED-APT", "MED-U04", "DOC-MEDAPT-REQ-001", "MEDAPT-1", " Sáu trạng thái hợp lệ trong vòng đời lịch hẹn hành chính của MediFlow gồm những trạng thái nào?", "Gồm Requested, Scheduled, CheckedIn, Completed, Cancelled và Missed."),
        ("MED-APT", "MED-U11", "DOC-MEDAPT-API-003", "MEDAPT-18", "Endpoint POST /api/v1/appointments:bulk-reschedule giới hạn tối đa bao nhiêu lịch hẹn mỗi lần và xử lý thế nào nếu 1 slot đích bị đầy?", "Giới hạn tối đa 30 lịch hẹn/lần, bắt buộc quyền RECEPTION_SHIFT_LEAD cùng reschedule_reason >= 10 ký tự; nếu bất kỳ slot đích nào đầy sẽ quay lui toàn bộ batch và trả HTTP 409 SLOT_CAPACITY_EXCEEDED."),
        ("MED-APT", "MED-U04", "DOC-MEDAPT-ARC-004", "MEDAPT-20", "Nội dung tin nhắn nhắc hẹn gửi qua cổng đối tác VietNotify được phép chứa những thông tin gì?", "Theo nguyên tắc tối thiểu hóa dữ liệu tại DOC-MEDAPT-ARC-004, tin nhắn chỉ chứa mã hẹn, ngày giờ và số quầy tiếp đón."),
        ("MED-APT", "MED-U04", "DOC-MEDAPT-DB-002", "MEDAPT-14", "Vì sao phiên bản v1 của DOC-MEDAPT-DB-002 bị yêu cầu chỉnh sửa (CHANGES_REQUESTED) trước khi duyệt v2?", "Tech Lead MED-U04 yêu cầu bổ sung quy tắc khóa các dòng theo thứ tự slot_id tăng dần (ORDER BY slot_id ASC) để ngăn deadlock khi hai luồng dời lịch hàng loạt chạy song song."),
        ("MED-ADM", "MED-U05", "DOC-MEDADM-ARC-002", "MEDADM-3", "Màn hình tivi gọi số công cộng tại sảnh chờ phòng khám hiển thị thông tin gì để bảo vệ sự riêng tư?", "Chỉ hiển thị mã vé tiếp đón trong ngày (ví dụ Q-108), chữ cái viết tắt tên và số quầy tiếp đón; không hiện họ tên đầy đủ hay năm sinh."),
        ("MED-ADM", "MED-U13", "DOC-MEDADM-DB-003", "MEDADM-5", "Sau bao lâu kể từ giờ hẹn mà khách Scheduled chưa Check-in thì hệ thống tự động chuyển sang trạng thái Missed cuối ca?", "Sau 45 phút kể từ khung giờ hẹn cuối ca, hệ thống đối soát và chuyển sang trạng thái Missed (tách biệt với Cancelled chủ động)."),
        ("MED-ADM", "MED-U13", "DOC-MEDADM-API-004", "MEDADM-8", "Báo cáo lưu lượng ngày GET /api/v1/reports/daily-traffic.xlsx xuất những cột nào và xử lý tham số mở khóa cột SĐT ra sao?", "Chỉ xuất thống kê lượt hẹn theo khung giờ và mã AK-PAT-XXXXXX, đồng thời bỏ qua mọi tham số query yêu cầu xuất số điện thoại."),
        ("MED-ADM", "MED-U17", "DOC-MEDADM-TST-005", "MEDADM-20", "Điều gì xảy ra khi tài khoản nhân viên vai trò RECEPTIONIST thông thường gọi API dời lịch hàng loạt?", "Hệ thống từ chối với mã lỗi HTTP 403 vì quyền dời lịch hàng loạt chỉ cấp cho RECEPTION_SHIFT_LEAD hoặc Quản trị vận hành."),
        ("MED-PIL", "MED-U16", "DOC-MEDPIL-ARC-002", "MEDPIL-4", "Tần suất kiểm tra tự động luồng callback trạng thái tin nhắn của bot MED-BOT-NOTIFY-PROBE là bao lâu?", "Bot MED-BOT-NOTIFY-PROBE chạy tự động 24/7 mỗi 15 phút để kiểm chứng kết nối mTLS và webhook sandbox."),
        ("MED-PIL", "MED-U16", "DOC-MEDPIL-API-003", "MEDPIL-7", "Hệ thống xử lý thế nào khi webhook từ VietNotify báo trạng thái gửi tin dời lịch là FAILED sau 2 lần thử?", "Tự động gắn cờ cần xác nhận lại trên bảng điều khiển của lễ tân trưởng để chủ động liên hệ trên màn hình có kiểm toán."),
        ("MED-PIL", "MED-U06", "DOC-MEDPIL-RUN-005", "MEDPIL-21", "Thời gian chuyển mạch sang router dự phòng 4G tại quầy tiếp đón trong buổi diễn tập ngày 10/10/2026 đạt bao nhiêu giây?", "Đạt 18 giây và không làm mất bất kỳ giao dịch đặt lịch nào đang thực hiện."),
        ("MED-REG", "MED-U09", "DOC-MEDREG-DES-005", "MEDREG-12", "Biểu mẫu đăng ký nhanh cho khách vãng lai (Walk-In) được rút gọn còn bao nhiêu trường bắt buộc và mất trung bình bao lâu?", "Rút gọn còn 4 trường hành chính bắt buộc với thời gian thao tác trung bình 16 giây/lượt."),
    ]
    for pid, princ, doc_id, t_key, q_txt, a_txt in domain_qa:
        add(
            "DOMAIN_RAG", "knowledge", "normal", pid, princ, q_txt, a_txt,
            [doc_id, task_id_by_key[t_key]], [doc_id, task_id_by_key[t_key]], [],
            [doc_id], [], ["domain_rule", pid.lower()],
        )

    # 37-56: Sprint closure rules, Group Note boundaries, Work Report governance, Blockers, Source License Compliance
    extra = [
        ("SPRINT_COMPLETION_RULE", "workspace", "sprint_governance", "MED-APT", "MED-U04",
         "Các Sprint đã đóng (MEDAPT-S1 đến MEDAPT-S4) còn chứa task nào ở trạng thái IN_PROGRESS hoặc BLOCKED không?",
         f"Không. Theo đúng quy tắc hợp đồng Sprint của Continuum, toàn bộ Sprint COMPLETED chỉ chứa các task đã kết thúc (DONE/CANCELLED); hạng mục chưa xong cuối Sprint 4 là {task_id_by_key['MEDAPT-25']} (MEDAPT-25) đã được rollover sang Sprint 5 đang ACTIVE (MEDAPT-S5).",
         [task_id_by_key["MEDAPT-25"]], [task_id_by_key["MEDAPT-25"], "MED-APT-WR-W40-L1"], [], ["MEDAPT-S5", "MEDAPT-25"], [], ["sprint_closure"]),
        ("ACTIVE_SPRINT_LIMIT", "workspace", "sprint_governance", "MED-REG", "MED-U03",
         "Tại thời điểm 2026-10-16, dự án MED-REG có bao nhiêu Sprint đang ở trạng thái ACTIVE?",
         "Chỉ có đúng 01 Sprint đang ACTIVE là MEDREG-S5 (Sprint 5: 2026-10-05 .. 2026-10-16); các Sprint S1..S4 đều đã COMPLETED.",
         ["MED-REG-WR-W41-L1"], ["MED-REG-WR-W41-L1"], [], ["01 Sprint", "MEDREG-S5", "ACTIVE"], [], ["single_active_sprint"]),
        ("TASK_NOTE_BOUNDARY", "knowledge", "task_note_not_knowledge", "MED-APT", "MED-U04",
         "Task Note ghi chú cách truyền tham số thử nghiệm ở MEDAPT-18 có thay thế tài liệu đặc tả API chính thức DOC-MEDAPT-API-003 v2 không?",
         "Không. Task Note chỉ lưu vết thực thi trong tab công việc (status=CONFIRMED, knowledge_eligible=false); nguồn tri thức API chính thức là DOC-MEDAPT-API-003 v2 đã APPROVED.",
         [note_id_by_key["MEDAPT-18"], "DOC-MEDAPT-API-003"], ["DOC-MEDAPT-API-003"], [note_id_by_key["MEDAPT-18"]],
         ["knowledge_eligible=false", "DOC-MEDAPT-API-003"], ["Trích dẫn Task Note thay cho API spec"], ["group_note_boundary"]),
        ("WORK_REPORT_FLOW", "workspace", "report_governance", "MED-REG", "MED-U01",
         "Ai có thẩm quyền phê duyệt báo cáo tuần cấp Leader MED-REG-WR-W40-L1 của Tech Lead Trần Quốc Khánh (MED-U03)?",
         "Chỉ Organization ADMIN Manager (MED-U01 hoặc MED-U02) mới được phê duyệt báo cáo cấp LEADER theo đúng luồng Leader -> Manager.",
         ["MED-REG-WR-W40-L1"], ["MED-REG-WR-W40-L1"], [], ["LEADER", "ADMIN"], [], ["leader_manager_flow"]),
        ("WORK_REPORT_REJECTED", "knowledge", "draft_vs_approved", "MED-APT", "MED-U04",
         "Báo cáo tuần thành viên MED-APT-WR-W40-M2 có được đưa vào kho tri thức đã duyệt không?",
         "Không. Báo cáo MED-APT-WR-W40-M2 đã bị REJECTED vì trích dẫn nhầm phản hồi chưa duyệt CFB-2026-03 như tính năng sắp bật, nên có knowledge_eligible=false.",
         ["MED-APT-WR-W40-M2"], ["MED-APT-WR-W40-M1"], ["MED-APT-WR-W40-M2"], ["REJECTED", "knowledge_eligible=false"], [], ["rejected_report"]),
        ("WORK_REPORT_CHANGES", "workspace", "report_governance", "MED-ADM", "MED-U02",
         "Báo cáo tuần Leader MED-ADM-WR-W41-L1 hiện đang ở trạng thái phê duyệt nào?",
         "Đang ở trạng thái CHANGES_REQUESTED để bổ sung số liệu đối chiếu chi tiết lượt CheckedIn và Missed theo yêu cầu của Manager.",
         ["MED-ADM-WR-W41-L1"], [], ["MED-ADM-WR-W41-L1"], ["CHANGES_REQUESTED"], [], ["report_changes_requested"]),
        ("WORK_REPORT_OVERDUE", "workspace", "report_governance", "MED-REG", "MED-U03",
         "Trạng thái nộp bài của báo cáo ngày MED-REG-WR-D1014-M2 trên danh sách theo dõi kỳ báo cáo là gì?",
         "Báo cáo đang ở trạng thái DRAFT nhưng đã quá hạn nộp (is_overdue=true, roster_submission_state=OVERDUE).",
         ["MED-REG-WR-D1014-M2"], [], ["MED-REG-WR-D1014-M2"], ["DRAFT", "OVERDUE"], [], ["overdue_report"]),
        ("WORK_REPORT_PENDING", "workspace", "report_governance", "MED-PIL", "MED-U06",
         "Báo cáo ngày MED-PIL-WR-D1015-M1 ngày 15/10/2026 đã được phê duyệt chưa?",
         "Chưa; báo cáo đang ở trạng thái PENDING_REVIEW chờ Lead MED-U06 xét duyệt nên chưa có knowledge_eligible.",
         ["MED-PIL-WR-D1015-M1"], [], ["MED-PIL-WR-D1015-M1"], ["PENDING_REVIEW"], [], ["pending_report"]),
        ("DAILY_LEADER_REPORT", "knowledge", "normal", "MED-PIL", "MED-U02",
         "Trong báo cáo ngày Leader MED-PIL-WR-D1014-L1 ngày 14/10/2026, nhóm triển khai đang phối hợp việc gì với đối tác VietNotify?",
         "Lead MED-U06 làm việc trực tiếp với kỹ sư đối tác VietNotify để thúc đẩy phê duyệt mã mẫu tin thông báo dời lịch chính thức nhằm gỡ điểm chặn MEDPIL-31.",
         ["MED-PIL-WR-D1014-L1", task_id_by_key["MEDPIL-31"]], ["MED-PIL-WR-D1014-L1", task_id_by_key["MEDPIL-31"]], [], ["VietNotify", "MEDPIL-31"], [], ["daily_leader_report"]),
        ("DAILY_MEMBER_APPROVED", "knowledge", "normal", "MED-ADM", "MED-U05",
         "Báo cáo ngày MED-ADM-WR-D1013-M1 ngày 13/10/2026 đã xác nhận kết quả kiểm tra phân quyền nào?",
         "Xác nhận tài khoản vai trò RECEPTIONIST thường bị chặn HTTP 403 khi gọi API dời lịch hàng loạt đúng theo thiết kế, và đã được Lead MED-U05 phê duyệt.",
         ["MED-ADM-WR-D1013-M1"], ["MED-ADM-WR-D1013-M1", "DOC-MEDADM-TST-005"], [], ["HTTP 403", "RECEPTIONIST"], [], ["daily_member_report"]),
        ("BLOCKED_PRINTER_REG", "workspace", "blocker_analysis", "MED-REG", "MED-U03",
         "Hạng mục nào của dự án MED-REG trong Sprint 5 đang ở trạng thái BLOCKED?",
         f"Task {task_id_by_key['MEDREG-31']} (MEDREG-31) đang BLOCKED do chờ điều phối viên mạng phòng khám An Khang xác nhận thông số máy in tem mã hành chính tại quầy số 2.",
         [task_id_by_key["MEDREG-31"]], [task_id_by_key["MEDREG-31"], "MED-REG-WR-W41-L1"], [], ["BLOCKED", "MEDREG-31"], [], ["blocker_analysis"]),
        ("BLOCKED_DOCTOR_ROOM", "workspace", "blocker_analysis", "MED-APT", "MED-U04",
         "Vì sao task MEDAPT-31 trong Sprint 5 của dự án MED-APT đang bị chặn (BLOCKED)?",
         f"Task {task_id_by_key['MEDAPT-31']} (MEDAPT-31) đang chờ Ban điều hành phòng khám An Khang chốt lịch tạm ngưng bảo trì phòng tư vấn số 4 cuối tháng 10.",
         [task_id_by_key["MEDAPT-31"]], [task_id_by_key["MEDAPT-31"]], [], ["BLOCKED", "MEDAPT-31"], [], ["blocker_analysis"]),
        ("BLOCKED_VIETNOTIFY_TEMPLATE", "workspace", "blocker_analysis", "MED-PIL", "MED-U06",
         "Điểm chặn bên ngoài nào đang giữ task MEDPIL-31 ở trạng thái BLOCKED?",
         f"Task {task_id_by_key['MEDPIL-31']} (MEDPIL-31) đang chờ cổng đối tác nhắn tin VietNotify phê duyệt mã template thông báo dời lịch hẹn ngoài môi trường sandbox.",
         [task_id_by_key["MEDPIL-31"]], [task_id_by_key["MEDPIL-31"], "MED-PIL-WR-D1014-L1"], [], ["BLOCKED", "VietNotify", "MEDPIL-31"], [], ["blocker_analysis"]),
        ("SUBTASK_HIERARCHY", "workspace", "subtask_hierarchy", "MED-APT", "MED-U04",
         "Subtask tích hợp thông báo sau khi dời lịch hàng loạt MEDAPT-19 gắn trực tiếp với task cha nào?",
         f"Subtask {task_id_by_key['MEDAPT-19']} (MEDAPT-19) là con trực tiếp 1 cấp của task {task_id_by_key['MEDAPT-18']} (MEDAPT-18).",
         [task_id_by_key["MEDAPT-18"], task_id_by_key["MEDAPT-19"]], [task_id_by_key["MEDAPT-18"], task_id_by_key["MEDAPT-19"]], [], ["MEDAPT-18", "MEDAPT-19"], [], ["subtask_1_level"]),
        ("CANCELLED_TASK_REASON", "workspace", "cancelled_scope", "MED-ADM", "MED-U05",
         "Vì sao task MEDADM-30 bị chuyển sang trạng thái CANCELLED?",
         f"Task {task_id_by_key['MEDADM-30']} (MEDADM-30) bị hủy sau khi đề xuất xuất số điện thoại đầy đủ ra Excel (CFB-2026-02 / DOC-MEDADM-EXPORT-006) bị bác bỏ vì rủi ro rò rỉ dữ liệu.",
         [task_id_by_key["MEDADM-30"], "DOC-MEDADM-EXPORT-006"], [task_id_by_key["MEDADM-30"], "DOC-MEDADM-REQ-001"], ["DOC-MEDADM-EXPORT-006@v1"], ["CANCELLED", "MEDADM-30"], [], ["cancelled_task"]),
        ("OVERTIME_SPRINT3", "workspace", "temporal_audit", "MED-APT", "MED-U04",
         "Nhóm MED-APT đã phát sinh làm thêm giờ buổi tối (17:00–22:00+07:00) ở hạng mục nào trong Sprint 3 để kịp đóng mốc tích hợp?",
         f"Phát sinh tăng ca buổi tối có kiểm soát tại các task {task_id_by_key['MEDAPT-14']} và {task_id_by_key['MEDAPT-18']} nhằm hoàn tất khóa tương tranh slot CSDL v2 và API dời lịch hàng loạt trước khi đóng Sprint 3.",
         [task_id_by_key["MEDAPT-14"], task_id_by_key["MEDAPT-18"]], [task_id_by_key["MEDAPT-14"], task_id_by_key["MEDAPT-18"], "DOC-MEDAPT-DB-002"], [], ["17:00", "MEDAPT-14", "MEDAPT-18"], [], ["overtime_audit"]),
        ("ORG_ADMIN_VISIBILITY", "workspace", "org_admin_visibility", "MED-REG", "MED-U02",
         "Principal Product & Privacy Governance Manager Lê Minh Thư (MED-U02, vai trò Organization ADMIN) có quyền kiểm tra tài liệu DOC-MEDREG-DB-003 không?",
         "Có. Với vai trò Organization ADMIN của ORG-MED, MED-U02 có quyền rà soát cấp tổ chức đối với các dự án thuộc ORG-MED.",
         ["DOC-MEDREG-DB-003"], ["DOC-MEDREG-DB-003"], [], ["ADMIN", "ORG-MED"], [], ["org_admin_access"]),
        ("OPENMRS_LICENSE_BOUNDARY", "workspace", "governance", "MED-REG", "MED-U01",
         "MediFlow có sao chép mã nguồn Java hoặc mô hình bệnh án lâm sàng từ kho tham chiếu OpenMRS (MPL-2.0 + Healthcare Disclaimer) không?",
         "Không. OpenMRS và tài liệu O3 chỉ được khảo sát để hiểu khái niệm hành chính về định danh, lịch hẹn, hàng đợi và cờ ẩn SĐT khi xuất file; toàn bộ MediFlow là dữ liệu và thiết kế hành chính synthetic độc lập.",
         ["DOC-MEDREG-REQ-001"], ["DOC-MEDREG-REQ-001"], [], ["MPL-2.0", "không sao chép", "synthetic"], [], ["license_compliance"]),
        ("MILESTONE_M3_DELAY_REASON", "knowledge", "normal", "MED-PIL", "MED-U01",
         "Vì sao mốc sẵn sàng Pilot Milestone M3 (MS-MED-03) lùi từ ngày kế hoạch 2026-10-08 sang ngày thực tế 2026-10-12?",
         "Do sự cố mưa bão mất mạng cuối Sprint 4 (DIS-MED-STORM-01) làm hạng mục kiểm thử dời lịch phải spillover sang Sprint 5, kết hợp với lịch diễn tập hạ tầng quầy lễ tân được bố trí vào ca trực Thứ Bảy 10/10/2026 trước khi mở cổng sáng Thứ Hai 12/10.",
         ["DOC-MEDPIL-RUN-005", task_id_by_key["MEDAPT-25"]], ["DOC-MEDPIL-RUN-005", "MED-PIL-WR-W40-L1", "MED-APT-WR-W40-L1"], [], ["08/10", "12/10", "DIS-MED-STORM-01"], [], ["milestone_delay"]),
        ("ROLE_NOT_FROM_TITLE", "workspace", "governance", "MED-PIL", "MED-U01",
         "Chức danh nghiệp vụ 'Senior Healthcare Admin BA' của Hoàng Minh Quân (MED-U07) có tự động mang quyền ADMIN hệ thống trên Continuum không?",
         "Không. Quyền hệ thống trên Continuum không bao giờ tự suy từ chức danh hay phòng ban; MED-U07 được gán tường minh vai trò MEMBER ở cả cấp tổ chức và cấp project.",
         ["DOC-MEDPIL-REQ-001"], ["DOC-MEDPIL-REQ-001"], [], ["MEMBER", "không bao giờ tự suy"], [], ["explicit_rbac"]),
    ]
    for row in extra:
        add(*row)

    assert len(cases) == 56, f"Expected 56 MediFlow evaluation cases, got {len(cases)}"
    return cases
