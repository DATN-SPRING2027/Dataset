# Checklist triển khai kế hoạch hoàn thiện dataset

**Trạng thái:** Hoàn tất triển khai; DOCX đã kiểm tra cấu trúc, chưa có render trực quan  
**Kế hoạch gốc:** [plan.md](plan.md)  
**Quy ước:** Chỉ đánh dấu hoàn thành khi có bằng chứng kiểm tra được; giữ file `dataset_presentation.html` chưa theo dõi nguyên trạng.

## Giai đoạn 0 — Chốt phạm vi và đồng bộ dữ liệu

- [x] **T0.1** Chốt khôi phục Jira-like structured data, fixtures và evaluation corpus; giữ nguyên phạm vi demo/RAG/ACL/tiến độ.
- [x] **T0.2** Không có rubric/template RDS trong workspace; dùng RDS tổng hợp, ánh xạ về SRS/SDS và ghi rõ giới hạn này.
- [x] **T0.3** Chốt tám DOCX rendition cho PMP, BRD, SRS, RDS, SDS, Database Design/ERD, API Specification và Master Test Plan.
- [x] **T0.4** Kiểm tra lịch sử Git, generator và schema hiện tại; xác nhận có thể tái tạo issues, comments, changelog, fixtures và evaluations mà không sửa tay output.
- [x] **T0.5** Nếu khôi phục corpus, tái tạo trên nhánh công việc và lập bảng đối chiếu số lượng/key/reference với nguồn lịch sử.
- [x] **T0.6** Cập nhật README/start guide, ingestion contract, catalog và manifest theo đúng package cuối cùng.
- [x] **Gate 0** Kiểm tra inventory khớp filesystem, mọi đường dẫn khai báo tồn tại, không có file ngoài ý muốn và presentation HTML vẫn nguyên trạng.

## Giai đoạn 1 — Coverage, metadata và ownership

- [x] **T1.1** Lập coverage matrix cho company/platform và tám project; đánh dấu Present, Partial hoặc Missing cho từng loại tài liệu.
- [x] **T1.2** Gán `document_id`, canonical ID, owner, organization/project scope, classification, ACL, version, status và ngày hiệu lực.
- [x] **T1.3** Xác định nguồn chuẩn, quy tắc phê duyệt và quan hệ supersedes/superseded_by.
- [x] **T1.4** Xác nhận đủ owner/stakeholder và access groups cho 8/8 project.
- [x] **Gate 1** Không còn tài liệu không rõ owner, scope, ACL hoặc trạng thái; metadata schema nhất quán giữa MD, DOCX và JSONL.

## Giai đoạn 2 — Khởi tạo và yêu cầu

- [x] **T2.1** Rà soát, cập nhật Project Charter để khớp scope, mục tiêu, KPI, tổ chức và timeline.
- [x] **T2.2** Soạn Project Management Plan (PMP) với WBS, lịch, nguồn lực, stakeholder, giao tiếp, chất lượng và change control.
- [x] **T2.3** Soạn Business Requirements Document (BRD) cho sản phẩm thương mại điện tử đa tenant.
- [x] **T2.4** Soạn Software Requirements Specification (SRS) với FR/NFR IDs ổn định và acceptance criteria.
- [x] **T2.5** Soạn RDS theo rubric đã chốt; ánh xạ nội dung sang SRS/SDS thay vì tạo nguồn yêu cầu thứ hai.
- [x] **T2.6** Tạo tám project annexes: CAT, SRCH, CART, CHKO, PAY, INV, ORD và PLAT.
- [x] **T2.7** Rà soát Catalog PRD và tài liệu nghiệp vụ hiện có; ghi version lineage, không xóa lịch sử.
- [x] **Gate 2** Mọi yêu cầu có ID duy nhất, ưu tiên, owner, project, tiêu chí chấp nhận và mối liên hệ với backlog.

## Giai đoạn 3 — Thiết kế và tiêu chuẩn kỹ thuật

- [x] **T3.1** Soạn Software Design Specification (SDS) bao quát kiến trúc, module, luồng, tenancy, security, failure handling và observability.
- [x] **T3.2** Soạn Database Design/ERD với entity, keys, constraints, indexes, tenancy, retention và migration/rollback.
- [x] **T3.3** Soạn API Specification toàn hệ thống, tham chiếu các contract chi tiết hiện có.
- [x] **T3.4** Soạn Coding Standards cho Laravel/PHP và Vue.js.
- [x] **T3.5** Soạn Threat Model, liên kết asset, trust boundary, abuse case, mitigation và residual risk với security standard.
- [x] **T3.6** Cập nhật architecture overview, data dictionary, API contracts và ADR index để thống nhất thuật ngữ.
- [x] **Gate 3** Tám project có thiết kế, API/data dependencies và security boundary; assumptions được ghi rõ.

## Giai đoạn 4 — Backlog, truy vết và kiểm thử

- [x] **T4.1** Tạo hoặc khôi phục backlog Jira-like: epics, stories, tasks, bugs, owners, sprints, estimates, dependencies, comments và changelog.
- [x] **T4.2** Soạn Requirements Traceability Matrix (RTM) nối requirement → design/API/data → issue → test → run → release.
- [x] **T4.3** Soạn Master Test Plan cho functional, integration, regression, security, performance và accessibility.
- [x] **T4.4** Tạo test cases chức năng theo module, role và tenant; thêm positive, negative, boundary và failure cases.
- [x] **T4.5** Soạn Test Execution Report với môi trường, version, pass/fail/blocked, defects, evidence và sign-off.
- [x] **T4.6** Soạn UAT Plan/Report theo persona buyer, merchant, support và operations.
- [x] **T4.7** Giữ evaluation corpus RAG/ACL/ingestion/progress riêng với test chức năng sản phẩm.
- [x] **Gate 4** Mỗi yêu cầu approved có ít nhất một test; defect mở có issue/owner; số liệu report khớp test runs.

## Giai đoạn 5 — Triển khai, vận hành và bàn giao

- [x] **T5.1** Soạn Deployment Guide cho môi trường demo, cấu hình mẫu, migration order, health checks và rollback.
- [x] **T5.2** Hoàn thiện Operations Runbook gồm monitoring, alerts, SLO, on-call, incident, backup/restore, DR và escalation.
- [x] **T5.3** Soạn User Manual theo buyer, merchant admin, customer support và operations.
- [x] **T5.4** Soạn Release Notes/Handover với thay đổi, migration, known issues, sign-offs và support ownership.
- [x] **T5.5** Soạn Risk Register có owner, likelihood/impact, mitigation, contingency, due date và status.
- [x] **T5.6** Soạn Change Log/Change Control liên kết với lịch sử issue, tránh tạo timeline lệch nguồn.
- [x] **Gate 5** Người mới có thể dựng demo, chạy smoke flow, thao tác theo role và tiếp nhận vận hành dựa trên tài liệu.

## Giai đoạn 6 — Test fixtures về tài liệu, quyền và vòng đời nhân sự

- [x] **T6.1** Tạo duplicate MD/DOCX renditions có canonical ID để kiểm tra khử trùng lặp.
- [x] **T6.2** Tạo cặp tài liệu cũ/mới và superseded/current để kiểm tra ưu tiên phiên bản.
- [x] **T6.3** Tạo fixture mâu thuẫn có nhãn test-only và expected behavior rõ ràng.
- [x] **T6.4** Tạo tài liệu thiếu metadata, broken link, attachment và orphan issue có expected outcome.
- [x] **T6.5** Tạo tình huống nhân viên inactive/offboarding, revoked access và kiểm tra ACL cross-project/cross-tenant.
- [x] **T6.6** Đảm bảo fixtures không bị nhầm là tài liệu chính thức hoặc nội dung policy thật.
- [x] **Gate 6** Có expected behavior và kết quả kiểm chứng cho từng nhóm tình huống; không lộ tài liệu trái ACL.

## Giai đoạn 7 — Sinh, kiểm định và bàn giao

- [x] **T7.1** Sinh package hoàn chỉnh từ nguồn chuẩn/generator; ghi lại lệnh và phiên bản generator.
- [x] **T7.2** Đồng bộ manifest, documents JSONL, catalog, ingestion contract, hashes, counts và references.
- [x] **T7.3** Chạy inventory/link/anchor/schema/duplicate/traceability/ACL/owner/reference/secret checks.
- [x] **T7.4** Parse và kiểm tra nội dung cả 18 DOCX; rendition tồn tại và trỏ đúng canonical Markdown. Chưa render trang trực quan do máy không có Word/LibreOffice.
- [x] **T7.5** Đối chiếu coverage matrix với tiêu chí hoàn thành; giải thích rõ mọi ngoại lệ.
- [x] **T7.6** Rà soát diff, file được thêm/xóa, trạng thái Git và file người dùng chưa theo dõi.
- [x] **T7.7** Chuẩn bị handoff/PR summary nêu scope, kiểm tra, rủi ro và tác động cấu hình/database (nếu có); không tự push hoặc merge.
- [x] **Gate 7** Generator và integrity validator đạt; còn giới hạn render DOCX trực quan đã ghi nhận ở T7.4.

## Phụ thuộc và thứ tự

`T0.1–T0.4` → `T0.5–T0.6` → `T1.*` → `T2.*` → `T3.*` → `T4.*` → `T5.*` → `T6.*` → `T7.*`

Các fixture của Giai đoạn 6 có thể được tạo song song với tài liệu sau khi schema metadata và ACL ở Giai đoạn 1 được duyệt; không dùng fixture để thay nội dung chuẩn.

## Bằng chứng bàn giao

- Lệnh: `python -B Project1/tools/generate_v1.py` — chạy thành công, package 153/160 file; package count excludes repo-root planning and presentation files.
- Quy mô: 1,434 tài liệu logic, 2,500 Jira-like issues, 15 access groups/160 memberships, 74 requirements, 84 functional tests và 131 evaluation cases.
- DOCX: 18/18 mở được bằng python-docx, có nội dung/heading/bảng; visual render chưa thực hiện được do thiếu Word/LibreOffice.
- Secret-pattern scan và email-domain scan không phát hiện vấn đề; `git diff --check` sạch.
