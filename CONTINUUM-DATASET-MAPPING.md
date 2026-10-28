# Checklist ánh xạ dataset vào Continuum AI

**Đối tượng:** người thiết kế, tạo, kiểm tra và sau này nhập dataset cho Nova, CloudOps và MediFlow; cũng dùng để rà soát Northstar. **Trạng thái:** yêu cầu và hướng dẫn chuẩn bị, không phải importer đã hoạt động hoặc phê duyệt seed. Các file README trong từng organization là nguồn bối cảnh; phải đọc cả tài liệu này trước khi thực hiện.

## 1. Phạm vi và nguyên tắc

- Mỗi organization phải có dữ liệu synthetic độc lập, project và thành viên phù hợp bối cảnh, độ bao phủ dự án tương đương Northstar; số lượng cụ thể chưa chốt. Team và Team Membership không thuộc phạm vi theo quyết định của Thang. Không khẳng định dữ liệu giả lập là dữ liệu thật.
- AI Chat là tính năng sản phẩm, không tạo hay nhập lịch sử AI Chat trong dataset. Câu hỏi và gold benchmark vẫn được giữ riêng cho evaluation.
- Giữ đặc trưng Waterfall của Nova, Kanban của CloudOps và Hybrid của MediFlow. Mô hình thuộc project; không ép sprint cho project không có sprint, không giả định milestone/incident đã là entity runtime.
- Chia dữ liệu thành: **(A)** dữ liệu dự kiến nhập ứng dụng theo contract được kiểm chứng; **(B)** metadata/sự kiện mô phỏng chưa có trường hoặc API tương ứng; **(C)** evaluation, gold và fixture chỉ phục vụ kiểm thử. Ghi rõ phân loại từng file/trường và lý do; không đưa gold vào index hoặc prompt của hệ thống được đánh giá.
- Dataset và ID nguồn là nguồn benchmark có phiên bản; ứng dụng và các service có contract, quyền và kho dữ liệu riêng. Có cùng tên không có nghĩa tương thích hoặc runtime đã hỗ trợ.
- Tài liệu này ghi nhận source/contract hiện thấy ngày 2026-10-28; trước khi xây importer phải kiểm tra lại revision, OpenAPI, validators, feature gate và runtime thực tế. Không tự thay schema, migration hoặc database để làm khớp dataset.

## 2. Ma trận dữ liệu cần tạo và đối chiếu

| Thành phần | Dataset cần mô tả | Đích/mapping và điều phải xác minh |
|---|---|---|
| Organization | ID nguồn, tên, thông tin tổ chức, trạng thái, phạm vi và timeline | Tạo organization bằng đường hợp lệ; ánh xạ sang ID hệ thống. Khách hàng/đối tác phải có scope riêng. |
| User và membership | User synthetic, email an toàn, chức danh, organization membership, project membership, trạng thái và thời gian hiệu lực | Tách user khỏi membership và role assignment; không dùng chức danh nghiệp vụ làm quyền. Xác minh creator, active membership và quyền theo từng project. Không lưu credentials thật. |
| Vai trò/quyền | Người quản trị, leader, member, đối tác và quyền theo scope | Đối chiếu các mã kỹ thuật `ADMIN`, `TEAM_LEADER`, `MEMBER` và policy thực tế; không tự cấp quyền từ tên vai trò hay membership. Các assignment SME/owner/successor không mặc định là role. |
| Project | ID nguồn, code, tên, creator, trạng thái, visibility, organization, thành viên | Ánh xạ ID project và membership; xác minh giá trị status/visibility, các thao tác tạo và quyền runtime. Không mặc định role Organization Admin mở mọi nội dung project. |
| Task | ID, project, title, description, type, priority, status, creator, assignee, parent, sprint tùy chọn, labels, dates, steps, version và thời điểm | Đối chiếu contract Task Workspace hiện hành. Task status: `TODO`, `IN_PROGRESS`, `IN_REVIEW`, `BLOCKED`, `DONE`, `CANCELLED`; type/priority và transitions cần xác minh theo contract. Jira-like issue không tự là Continuum Task. |
| Task comment/worklog/history | Tác giả, nội dung, thời gian, thời lượng, thay đổi trạng thái/assignee, lý do, nguồn | Ánh xạ từng loại và tham chiếu task. Kiểm tra API, quyền, event/version, khả năng giữ lịch sử và thứ tự; không giả mạo actor/thời điểm qua API. |
| Sprint | Project, tên, mục tiêu, thời gian, trạng thái, task và lịch sử chuyển sprint | Đối chiếu `PLANNED`, `ACTIVE`, `COMPLETED` và contract; chỉ tạo nếu project có sprint. Chuỗi phase/milestone không tự là sprint. |
| Task Note | Project, task, author, title, accomplishments, approach, reason, trạng thái và thời gian | Đối chiếu Task Note gắn task và contract capture. Ghi nhận Work Note độc lập nếu cần nhưng phải xác minh API tương ứng; không suy ra Task Note tự là nguồn tri thức chính thức. |
| Project Document | Project/scope, title, description, type, content, file, tác giả, phiên bản, review, trạng thái và nguồn | Ánh xạ type/status theo contract; giữ nội dung và file gốc, phiên bản được duyệt và quyền. Không tự đưa tài liệu organization-level vào project nếu chưa có contract. |
| Work Report | Project, member/leader, kỳ, frequency, accomplishments, approach, reason, blockers, next steps, document references, review | Kiểm tra `MEMBER`/`LEADER`, kỳ, trạng thái và DTO thực tế. `source_task_ids` của Northstar là metadata dataset, không tự gửi thành field API. |
| Chat giữa người | Conversation, loại hội thoại, membership, message, tác giả, thời điểm và sự kiện nếu dùng | Ánh xạ theo Chat API/quyền, phân biệt chat nhóm và tin nhắn cá nhân. Xác minh khả năng tái tạo lịch sử; không trộn chat với câu hỏi benchmark. |
| Query evaluation | Câu hỏi benchmark, project, thời điểm, nguồn, đáp án/gold, loại câu hỏi và quyền | Chỉ dùng đánh giá; không tạo hoặc import lịch sử AI Chat. UI mẫu không chứng minh kết nối AI. |
| Group Note | Bắt buộc đủ ba dạng: note trong tab công việc, tài liệu project và báo cáo hằng ngày/hằng tuần | Theo cách gọi của Thang; mapping tương ứng sang Task Note, Project Document và Work Report cần đối chiếu contract. Không tạo entity Notebook thứ tư. |
| Handover/knowledge/notification | Sự kiện bàn giao, người cũ/người nhận, việc mở, nguồn, review; sự kiện thông báo nếu kịch bản cần | Phân biệt metadata mô phỏng với entity runtime. Xác minh API, gate và consumer trước khi import; không khẳng định handover/knowledge/notification hoạt động end-to-end chỉ vì có dữ liệu. |
| Phase, milestone, rủi ro, sự cố, nghỉ phép, lịch | Thời điểm, người liên quan, nguyên nhân, tác động, trạng thái, nguồn và chuỗi xử lý | Chỉ mapping vào task/note/document khi phù hợp contract; phần chưa có entity giữ trong metadata. Không tạo schema hoặc API giả định. |

Nguồn đối chiếu: `../DATN_BE/docs/workspace/04-api-inventory.yaml`, `../DATN_FE/src/lib/queries/tasks/useTasks.ts`, `../DATN_FE/src/lib/queries/work-notes/useWorkNotes.ts`, `../DATN_BE/src/services/iam/iam.module.ts`, `../DATN_BE/src/services/chat/controllers/chat.controller.ts`, `../Document/research-docs/01_MVP_SCOPE.md`, `Project1/INGESTION_CONTRACT.md`. Kiểm tra source/contract mới nhất trước khi dùng; tên path và trạng thái trong workspace không chứng minh deployment đã sẵn sàng.

## 3. Lịch, chuỗi sự kiện và dữ liệu nhất quán

- Lập timeline và sự kiện gốc trước khi tạo bản ghi: giờ Việt Nam `+07:00`; mặc định thứ Hai–thứ Sáu 08:00–12:00, 13:00–17:00; thứ Bảy, Chủ Nhật và các ngày lễ được liệt kê theo năm là nghỉ. OT thông thường 17:00–22:00 có người, khoảng thời gian, lý do và nhãn.
- Ngoại lệ trực/sự cố cuối tuần, ngày lễ hoặc ngoài giờ phải ghi rõ lịch, lý do, người trực và thời gian; bot 24/7 tách khỏi người. Không tạo hoạt động thường cho người đang nghỉ/ốm nếu không có giải thích.
- Cho các tình huống như ốm, mưa bão, mất mạng, nghỉ phép, sai sót, việc bị chặn, chuyển người và thay đổi yêu cầu: bảo đảm nguyên nhân → tác động → xử lý/chuyển giao → note/quyết định → cập nhật task, tài liệu và báo cáo nhất quán theo thời gian.
- Có tiếng Việt, tiếng Anh và trường hợp pha trộn khi phù hợp; có dữ liệu thiếu, thay đổi quyết định, bản nháp/bản duyệt, việc hoàn thành/chưa hoàn thành và quyền bị thu hồi. Không gán mọi rủi ro cho mọi người hoặc sinh dữ liệu lặp để đủ số lượng.

## 4. Chuẩn bị mapping và import sau này

1. Lập data dictionary cho từng loại: field nguồn, kiểu, bắt buộc/tùy chọn, đích, chuyển đổi enum, phạm vi, provenance, validation, cách xử lý null và trạng thái hỗ trợ. Không bỏ silently các trường không có đích; ghi ở metadata và báo cáo.
2. Dùng ID nguồn ổn định theo từng loại và organization; lập bảng ánh xạ source ID → target ID, liên kết đầy đủ và bảo đảm chạy lại không tạo trùng. ID 24 hex synthetic không chứng minh bản ghi đã có trong MongoDB.
3. Dự kiến thứ tự theo phụ thuộc: organization và user → organization membership/role → project và project membership → sprint và task (bao gồm parent) → note/document/report → chat và thành phần khác khi có đường nhập. Kiểm tra chính sách creator/actor và thứ tự thực tế trước khi chạy.
4. Xác định cho từng loại: API được hỗ trợ, công cụ import được duyệt, chỉ metadata hay chưa khả dụng. Import Jira CSV hiện có ràng buộc riêng, không coi là importer tổng quát cho dataset này.
5. Không giả định có thể đưa `createdAt`, `authorId`, lịch sử sự kiện hoặc status bất kỳ qua API. Nếu cần bảo toàn lịch sử, thiết kế và xác minh cơ chế được phép; nếu không làm được, ghi rõ khác biệt giữa source timeline và runtime timeline.
6. Trước khi seed/import phải có môi trường đích được xác nhận, phạm vi, kế hoạch chạy lại, báo cáo lỗi, rollback và backup phù hợp; không ghi vào DB thật chỉ vì đã có dataset. Chỉ dùng đường có quyền và contract được duyệt.

## 5. Checklist nghiệm thu cho người thực hiện

- [x] Mỗi organization có project, user, membership và quyền đúng phạm vi; không yêu cầu Team hoặc Team Membership (`Project1` v1.4, `Organization2-Nova-Solutions`, `Organization3-CloudOps-Services`, `Organization4-MediFlow`).
- [x] Task, sprint khi có (`MediFlow` Hybrid 15 sprints; `Nova` Waterfall & `CloudOps` Kanban `sprint_id=null`), checklist, comment, worklog, history, note, document/file/review và report có liên kết, actor, trạng thái và thời gian hợp lệ; dữ liệu chưa có đích được thống kê riêng tại [CONTINUUM_DATA_DICTIONARY.md](CONTINUUM_DATA_DICTIONARY.md).
- [x] Timeline, ngày lễ Việt Nam 2026, khung nghỉ trưa `12:00–13:00`, OT buổi tối `17:00–22:00`, ngoại lệ trực ca, ốm/bão/offboarding/bàn giao và chuỗi tác động nhất quán; không lộ dữ liệu thật, dữ liệu lâm sàng hoặc credentials (xem thêm [GITHUB_SOURCES_AND_LICENSES.md](GITHUB_SOURCES_AND_LICENSES.md)).
- [x] Có benchmark cho từng project/giai đoạn (`358` ca tổng cộng: `190` ở Northstar + `56 × 3` ở ba organization mới): question, thời điểm, gold checklist, source ID/phiên bản, câu trả lời thiếu bằng chứng, ca mâu thuẫn và ca quyền; toàn bộ được gắn trung thực `review_status = "unreviewed"` (`"chưa duyệt"`) kèm khung `reviewer_1` / `reviewer_2` để hai người độc lập nghiệm thu.
- [x] Tách tập phát triển (`dev`) và tập kiểm tra cuối (`test`); tách gold (`evaluation/`), fixture âm (`fixtures/negative_cases.json`) và dữ liệu nguồn dự kiến index.
- [x] Có `manifest.json` phiên bản, quy mô, nguồn tham chiếu GitHub, checksum SHA-256 từng file, [CONTINUUM_DATA_DICTIONARY.md](CONTINUUM_DATA_DICTIONARY.md), `continuum_id_mapping.jsonl`, bộ validation (`tools/continuum_synth.py`, `tests/test_four_organizations.py`) và hướng dẫn tái lập hai lần sinh khớp tuyệt đối.
- [ ] Nếu import được thực hiện *(chưa thực hiện trong task chuẩn bị dataset này — chờ môi trường đích và importer riêng được duyệt)*: đối chiếu số lượng và quan hệ trước/sau, kiểm tra enum/actor/quyền, tệp tải được, truy cập chéo bị từ chối, tạo lại không trùng, lỗi có báo cáo và rollback đã được xác minh trên môi trường an toàn.
- [x] Phân biệt rõ kết quả test dataset trên đĩa với test import/API và test end-to-end thật; không đánh dấu tích hợp SAG/index hoặc handover runtime thành công khi consumer thực tế chưa được kiểm chứng.

## 6. Trạng thái sau khi hoàn thiện bộ dataset bốn organization (2026-10-28)

- **Đã chốt và hiện thực hóa trong dataset**: Quy mô, cửa sổ thời gian (`+07:00`), lịch nghỉ lễ 2026, đủ 3 dạng Group Note (`TASK_NOTE`, `PROJECT_DOCUMENT`, `WORK_REPORT`) và luồng phê duyệt `MEMBER -> TEAM_LEADER/ADMIN`, `LEADER -> Organization ADMIN` khớp `DATN_BE/src/services/capture/`.
- **Khoảng trống runtime cần lưu ý cho giai đoạn sau**: Consumer tiêu thụ outbox từ `capture` sang kho vector/SAG và luồng handover runtime tự động hiện vẫn ở trạng thái `NOT_YET_AVAILABLE`; việc nạp giữ nguyên lịch sử thời gian (`created_at`, `reviewed_at`) và tác giả đã `SUSPENDED` cần công cụ `IMPORTER_REQUIRED` theo đúng thứ tự phụ thuộc tại [CONTINUUM_DATA_DICTIONARY.md](CONTINUUM_DATA_DICTIONARY.md).
- **Quy trình con người tiếp theo**: Duyệt chéo 2 người độc lập (`reviewer_1`, `reviewer_2`) cho các ca benchmark đang mang `review_status = "unreviewed"` và chốt môi trường MongoDB đích trước khi xây dựng importer.
