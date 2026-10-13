# Kế hoạch hoàn thiện hồ sơ dự án Northstar Commerce

**Trạng thái:** Đã triển khai và kiểm định trên nhánh `feat/Thang-dataset-docs-completeness-20261013` (2026-10-13).  
**Ngày lập:** 2026-10-13  
**Phạm vi:** Bộ dữ liệu mô phỏng nền tảng thương mại điện tử đa tenant Northstar Commerce Systems, lấy cảm hứng miền nghiệp vụ từ Bagisto; stack tham chiếu Laravel và Vue.js. Toàn bộ tài liệu dự án sinh ra bằng tiếng Anh.

## Mục tiêu

Hoàn thiện bộ hồ sơ xuyên suốt vòng đời phần mềm: khởi tạo, quản lý dự án, yêu cầu, thiết kế, phát triển, kiểm thử, phát hành, vận hành và bàn giao. Tài liệu phải áp dụng được cho cả nền tảng và tám workstream: Catalog, Search, Cart, Checkout, Payment, Inventory, Orders/Returns và Platform.

Mỗi yêu cầu phải truy vết được đến thiết kế, ticket/backlog, test case, kết quả kiểm thử và release. Tài liệu phải có phiên bản, chủ sở hữu, phạm vi tổ chức/dự án và quyền truy cập để phục vụ demo, tìm kiếm/RAG, ACL và phân tích tiến độ.

## Đường cơ sở đã kiểm tra

- Repo hiện có 22 tài liệu formal: 12 Markdown và 10 DOCX. Các tài liệu đã có gồm Project Charter, một PRD cho Catalog, tổng quan kiến trúc, hợp đồng API Checkout, test plan hồi quy Checkout, runbook release/rollback, data dictionary, tiêu chuẩn phân loại dữ liệu/bảo mật, ADR, RCA, SOP và tài liệu tích hợp.
- Nhiều loại đã có nội dung liên quan nhưng chỉ ở phạm vi một module; chúng chưa thay thế PMP, BRD, SRS, RDS hoặc SDS toàn hệ thống.
- `origin/main` đang ở merge commit `4374a79` sau PR #1. PR đó đã gỡ các Markdown bundle, evaluation cases, fixtures và structured Jira JSONL khỏi cây hiện tại.
- Sau lần gỡ này, `Project1` có 27 file vật lý, trong đó 22 tài liệu formal. Tuy vậy `manifest.json` vẫn khai báo 107 file, 56 bundle và 1.400 bản ghi tài liệu; inventory còn 106 đường dẫn, trong đó 80 đường dẫn không còn trên đĩa. `manifest.json` tự loại khỏi inventory là đúng chính sách.
- File chưa được theo dõi `dataset_presentation.html` ở repo root là dữ liệu người dùng; phải giữ nguyên và không đưa vào thay đổi tài liệu này nếu chưa được yêu cầu.

### Quyết định đã chốt khi triển khai

- Khôi phục đầy đủ dữ liệu Jira-like, fixtures và evaluation corpus bằng generator; không chép tay output hàng loạt.
- Không có rubric/template RDS của trường trong workspace, nên dùng RDS tổng hợp theo nghiệp vụ và liên kết nguồn yêu cầu/thiết kế với SRS/SDS.
- Tạo DOCX rendition cho tám deliverable cốt lõi: PMP, BRD, SRS, RDS, SDS, Database Design/ERD, API Specification và Master Test Plan.
- Giữ nguyên `dataset_presentation.html`; package ingest nằm trong `Project1`.

## Quyết định thiết kế tài liệu

1. **Markdown là nguồn chuẩn để quản lý phiên bản.** DOCX là bản trình bày/phát hành được tạo từ nguồn chuẩn; cặp Markdown/DOCX có `canonical_document_id` và metadata chỉ rõ rendition, tránh coi bản sao là hai nguồn độc lập.
2. **SRS và SDS là nguồn chuẩn theo nội dung.** SRS sở hữu mã yêu cầu và tiêu chí chấp nhận; SDS sở hữu thiết kế. RDS là hồ sơ tổng hợp theo mẫu trường học/khách hàng, liên kết hoặc kết xuất nội dung đã duyệt từ SRS/SDS, không tạo bộ yêu cầu thứ hai.
3. **Dùng hồ sơ nền tảng chung cộng với tám project annex.** Không sao chép nguyên PMP/SRS/SDS toàn hệ thống thành tám bộ độc lập. Mỗi annex mô tả phạm vi, yêu cầu, API/dữ liệu, phụ thuộc, rủi ro và kiểm thử riêng của một workstream.
4. **Tài liệu hiện có được mở rộng khi đúng vai trò.** Giữ các tài liệu tập trung như Checkout API Contract, Checkout Regression Plan, Platform Architecture Overview và Release/Rollback Runbook làm tài liệu chi tiết được tài liệu tổng thể tham chiếu.
5. **Dữ liệu chỉ là synthetic.** Stack và miền nghiệp vụ tham chiếu không đồng nghĩa sao chép mã nguồn Bagisto hoặc đưa bí mật/dữ liệu thật vào tài liệu.

## Kế hoạch theo giai đoạn

### Giai đoạn 0 — Đồng bộ nguồn và khôi phục tính nhất quán

- Chốt lựa chọn khôi phục full simulation corpus hay giữ docs-only. Mặc định khuyến nghị khôi phục để đáp ứng use case Jira, ACL, RAG và tiến độ.
- Kiểm tra `tools/generate_v1.py` trên nhánh mới nhất; xác nhận generator có thể tái tạo bundles, structured issues, fixtures và evaluation. Nếu thiếu, phục hồi nguồn sinh trong một thay đổi có thể tái lập, không copy tay hàng loạt file sinh.
- Cập nhật `manifest.json`, `00_START_HERE.md`, `INGESTION_CONTRACT.md` và `Dataset_Catalog.xlsx` từ đúng kết quả cuối cùng.

**Checkpoint 0:** mọi file inventory tồn tại; số lượng thực tế khớp metadata; phạm vi repo được ghi rõ; file presentation chưa theo dõi vẫn nguyên trạng.

### Giai đoạn 1 — Ma trận tài liệu, quyền hạn và truy vết

- Tạo `document_coverage_matrix.md` với hàng cho từng tài liệu bắt buộc/nâng cao, cột cho từng phạm vi: company, platform, tám project, owner, audience, ACL, version/status, nguồn hiện có, gap và ticket liên quan.
- Chuẩn hóa metadata cho tài liệu: `document_id`, `canonical_document_id`, `version`, `status`, `owner_id`, `organization_id`, `project_id`, `scope`, `classification`, `access_groups`, `created_at`, `updated_at`, `supersedes`, `superseded_by`, `source_issue_keys`, `requirement_ids`.
- Thiết lập quy tắc trạng thái Draft → In Review → Approved → Superseded; xác định bản nào có quyền chuẩn khi có xung đột.

**Checkpoint 1:** 8/8 project có owner, phạm vi, quyền truy cập và danh sách gap; không còn tài liệu không rõ trạng thái hoặc nguồn chuẩn.

### Giai đoạn 2 — Khởi tạo, nghiệp vụ và đặc tả yêu cầu

Tạo/cập nhật các tài liệu nguồn chuẩn sau:

- `Project_Management_Plan.md` — PMP: phạm vi, mục tiêu, stakeholder, WBS, timeline, nguồn lực, giao tiếp, change control, chất lượng và rủi ro.
- `Business_Requirements_Document.md` — BRD toàn sản phẩm: vấn đề kinh doanh, merchant/buyer/support needs, quy tắc nghiệp vụ, KPI, phạm vi và ngoài phạm vi.
- `Software_Requirements_Specification.md` — SRS: FR/NFR có ID ổn định, use case, quyền/role, dữ liệu vào-ra, acceptance criteria, constraint và assumption.
- `Requirements_and_Design_Specification.md` — RDS theo định dạng tổng hợp, có bảng ánh xạ sang SRS/SDS và nguồn chi tiết.
- Tám file trong `project-annexes/`: `NSC-CAT`, `NSC-SRCH`, `NSC-CART`, `NSC-CHKO`, `NSC-PAY`, `NSC-INV`, `NSC-ORD`, `NSC-PLAT`. Mỗi file ghi mục tiêu, scope, stakeholder, use case, requirement IDs, dependencies, acceptance criteria và Jira issue keys.
- Cập nhật Charter và Catalog PRD nếu có lệch scope/KPI; giữ nguyên version lineage cũ thay vì ghi đè lịch sử.

**Checkpoint 2:** mỗi requirement có ID duy nhất, priority, owner, acceptance criteria và project; RDS không tạo nội dung mâu thuẫn với SRS/SDS.

### Giai đoạn 3 — Thiết kế và tiêu chuẩn kỹ thuật

- `Software_Design_Specification.md` — SDS: architecture views, service/module boundaries, sequence/data flows, failure handling, tenancy boundary, authn/authz, caching/async, observability và quyết định thiết kế.
- `Database_Design_and_ERD.md`: ERD, entity/field, primary/foreign keys, constraints, indexes, tenant keys, retention, migration và rollback.
- `API_Specification.md`: danh mục API toàn hệ thống theo module; auth, request/response, error model, pagination, idempotency, webhooks, versioning và link tới contract chi tiết.
- `Coding_Standards.md`: Laravel/PHP và Vue.js conventions, validation, error handling, logging, testing, review và dependency policy.
- `Threat_Model.md`: asset, trust boundaries, abuse cases, threat analysis, mitigations, residual risks; liên kết với Security Data Classification and Access Standard.
- Cập nhật Platform Architecture Overview, data dictionary, ADR index và các API contracts hiện có để thống nhất thuật ngữ.

**Checkpoint 3:** mỗi module trong 8 annex có thiết kế, data/API dependencies và security boundary; mọi technology/version được ghi rõ hoặc đánh dấu assumption.

### Giai đoạn 4 — Backlog, kiểm thử và nghiệm thu

- Khôi phục hoặc tạo lại Jira-like backlog theo scope đã chốt: epic/story/task/bug, owner, sprint, estimate, trạng thái, acceptance criteria, comment/changelog và dependencies.
- `Requirements_Traceability_Matrix.md` (RTM): `requirement_id → design/API/data component → issue_key → test_case_id → run_id/result → release`.
- `Master_Test_Plan.md`: scope, test levels, environment, test data, entry/exit criteria, severity, automation, security, performance, accessibility và regression approach.
- `Software_Test_Cases.md` hoặc JSONL có schema tương ứng: test ID, requirement, preconditions, role/tenant, steps, expected result, priority và negative case cho đủ tám module.
- `Test_Execution_Report.md`: run/version/environment, pass/fail/blocked, defects, evidence, waiver và sign-off.
- `UAT_Plan.md` và `UAT_Report.md`: merchant, buyer, support, operations personas; acceptance/sign-off.
- Giữ evaluation corpus riêng cho kiểm thử ingestion/RAG/ACL; phân biệt rõ với test cases chức năng của sản phẩm thương mại điện tử.

**Checkpoint 4:** tất cả requirement approved có ít nhất một test; lỗi mở có issue và owner active; báo cáo thể hiện rõ kết quả thực tế so với kỳ vọng.

### Giai đoạn 5 — Release, triển khai, vận hành và bàn giao

- `Deployment_Guide.md`: môi trường, cấu hình mẫu không chứa bí mật, migration order, deployment, smoke/health checks và rollback.
- Mở rộng hoặc liên kết `Commerce_Release_and_Rollback_Runbook.docx` với `Operations_Runbook.md`: monitoring, alerts, SLO, on-call, incident response, backup/restore, DR và escalation.
- `User_Manual.md`: hướng dẫn theo vai trò buyer, merchant admin, customer support và operations; luồng thao tác, lỗi thường gặp và quyền truy cập.
- `Release_Notes_and_Handover.md`: release/version, thay đổi, migration, known issues, sign-offs, support ownership và handover checklist.
- `Risk_Register.md`: risk ID, likelihood/impact, owner, mitigation, contingency, due date và trạng thái.
- `Change_Log_and_Change_Control.md`: quy trình đề xuất/duyệt/thực thi thay đổi; liên kết lịch sử Jira thay vì tạo timeline thứ hai không đồng bộ.

**Checkpoint 5:** một người mới có thể dựng môi trường demo, chạy smoke flow, dùng sản phẩm theo role và tiếp nhận vận hành theo tài liệu.

### Giai đoạn 6 — Version, ACL và tình huống kiểm thử tài liệu

- Tạo phiên bản Draft/Approved/Superseded có quan hệ `supersedes` rõ; chỉ tạo xung đột nội dung khi được gắn nhãn fixture kiểm thử.
- Mỗi tài liệu mang scope company/project/tenant và ACL nhất quán với group membership; tài liệu đối tác không lộ sang tenant khác.
- Duy trì edge cases có chủ đích: duplicate DOCX/Markdown rendition, bản cũ, tài liệu mâu thuẫn, thiếu metadata, link hỏng, attachment, orphan issue, nhân viên inactive/offboarding, access revoked và tài liệu ngoài phạm vi.
- Tách fixture lỗi khỏi tài liệu chuẩn; đánh dấu expected behavior để demo và đánh giá không hiểu nhầm fixture là chính sách thật.

### Giai đoạn 7 — Sinh dữ liệu, kiểm chứng và bàn giao

- Sinh lại package bằng generator; không sửa trực tiếp các output do generator quản lý.
- Đồng bộ `documents.jsonl`, manifest, catalog, ingestion contract, file hashes, count, version lineage, project/issue references và quyền ACL.
- Chạy validator của generator và các audit chuyên biệt: inventory, broken links, future/orphan references (ngoại trừ fixture), duplicate groups, requirement traceability, ACL isolation, owner inactive, DOCX XML/render, Markdown anchors và secret scan.
- Review diff toàn bộ; tách thay đổi khôi phục dữ liệu khỏi thay đổi tài liệu nếu cần để PR dễ review; không force-push và không merge thay người dùng.

## Bộ tài liệu đích

| Nhóm | Tài liệu đích | Hiện trạng |
|---|---|---|
| Khởi tạo/quản lý | Charter, PMP, BRD | Charter có; PMP/BRD thiếu; Charter cần rà soát |
| Yêu cầu | SRS, RDS, 8 project annexes | PRD Catalog có một phần; SRS/RDS và annexes thiếu |
| Thiết kế | SDS, Database Design/ERD, API Specification, Coding Standards, Threat Model, ADR index | Architecture/API/data/security/ADR có từng phần; bộ tổng thể thiếu |
| Phát triển | Backlog/Product-Sprint Backlog, Change Control/Log | Có lịch sử trong phiên bản corpus ban đầu; vắng khỏi `origin/main` hiện tại |
| Kiểm thử | Master Test Plan, Functional Test Cases, Test Execution Report, UAT Plan/Report, RTM | Checkout test plan và RAG evaluations có từng phần; bộ sản phẩm tổng thể thiếu |
| Phát hành/vận hành | Deployment Guide, Operations Runbook, User Manual, Release Notes/Handover, Risk Register | Release/Rollback Runbook có một phần; các tài liệu còn lại thiếu hoặc chưa đủ |

Kết quả: 31 Markdown formal được bổ sung, tổng cộng 43 formal Markdown, tám project annexes, tám DOCX rendition và 10 DOCX canonical. Package ingest `Project1` có 153 file vật lý, dưới ngưỡng 160; kế hoạch và presentation ở repo root không thuộc package. Có 1,434 tài liệu logic, 74 requirement, 84 functional test case và 131 evaluation case. Không tạo bộ hồ sơ tổng thể lặp lại tám lần.

## Tiêu chí hoàn thành

- 100% nhóm tài liệu core được đánh dấu Present/Partial/Missing trong coverage matrix; 8/8 project có annex và owner.
- Có đủ Charter, PMP, BRD, SRS, RDS, SDS, Database Design, API Specification, Backlog, Coding Standards, Test Plan, Test Cases, Test Report, Deployment Guide, User Manual, Release Notes/Handover; có RTM, Risk Register, Change Control, ADR, Threat Model, UAT và Operations Runbook.
- Yêu cầu approved truy vết được đến Jira issue, test case và release; mọi ngoại lệ được nêu rõ.
- 100% metadata bắt buộc có owner, scope, status, version, dates, organization/project và ACL.
- Manifest inventory khớp file vật lý; link/anchor/reference hợp lệ, ngoại trừ fixture lỗi được đánh dấu rõ.
- DOCX rendition trỏ về canonical Markdown; bản superseded không bị coi là bản hiện hành.
- Nội dung dự án bằng tiếng Anh, synthetic-only, không có bí mật; validator và generator đều chạy thành công.

## Rủi ro và cách xử lý

| Rủi ro | Tác động | Cách xử lý |
|---|---|---|
| PR #1 đã loại Jira/evaluation corpus nhưng manifest vẫn khai báo corpus cũ | Dataset không tái lập, sai count và mất use case ACL/tiến độ | Chốt docs-only hay phục hồi; khuyến nghị phục hồi qua generator/lịch sử Git rồi cập nhật metadata |
| SRS, SDS, RDS cùng được biên soạn độc lập | Mâu thuẫn yêu cầu và thiết kế | SRS/SDS là nguồn nội dung; RDS là bản tổng hợp có liên kết nguồn |
| DOCX và Markdown bị ingest như hai tài liệu khác nhau | Kết quả RAG trùng lặp | Dùng canonical ID/rendition metadata; duplicate chỉ xuất hiện trong fixture |
| Tài liệu không khớp ticket/sprint hoặc người nghỉ việc còn owner issue mở | Sai tiến độ và sai truy vết | Kiểm tra khóa tham chiếu, thời gian, status và owner trong validator |
| Tăng số file quá nhiều | Khó demo, khó quản lý phiên bản | Một bộ master + tám annexes; DOCX chỉ tạo cho deliverables cần trình bày; giữ giới hạn vật lý |
| Branch/main thay đổi bởi PR khác | Ghi đè hoặc lập kế hoạch trên trạng thái cũ | Bắt đầu từ `origin/main` mới nhất, giữ nguyên `dataset_presentation.html`, không force-push |

## Giới hạn kiểm định đã biết

- Generator integrity validation, inventory/hash/reference checks, ACL expectation checks, secret-pattern scan, email-domain scan và parse 18 DOCX bằng `python-docx` đều đạt.
- DOCX có nội dung, heading và bảng; kiểm tra render trực quan theo trang chưa chạy được vì môi trường Windows hiện tại không có Microsoft Word hoặc LibreOffice.
- Báo cáo chạy chức năng là dữ liệu mô phỏng: 82 Passed, 1 Failed và 1 Blocked trên 84 case; không được trình bày như kết quả chạy hệ thống thật.
