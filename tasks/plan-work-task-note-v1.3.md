# Kế hoạch đề xuất: Dataset Project1 cho Work Task và Work Note (v1.3)

**Trạng thái:** Thang đã duyệt và đã triển khai trên nhánh `feat/Thang-dataset-work-task-note-db`.

## 1. Mục tiêu và phạm vi

Tạo một lát dữ liệu tổng hợp, tái lập được, mô tả chuỗi **Work Task → Task Note → Project Document/Work Report → review → evaluation** trong `Project1`. Bộ dữ liệu phục vụ benchmark và demo độc lập. Không seed vào MongoDB, không sửa DATN_BE/DATN_FE/SAG, không kích hoạt ingestion runtime hoặc AI index.

Giữ nguyên 2.500 Jira-like issues và toàn bộ ID hiện có. Work Task là thực thể riêng, có tham chiếu `source_issue_key` khi bắt nguồn từ issue; không đổi tên `issues.jsonl` thành tasks. Không đưa gold answers vào demo retrieval namespace.

## 2. Căn cứ và quyết định dữ liệu

- `Project1/manifest.json` mô tả v1.2.0: 2.500 issues, 1.434 logical documents, 158 evaluation cases và giới hạn 160 file vật lý. **Cây file thực tế hiện có 163 file, còn manifest chỉ liệt kê 153**: 10 tệp `*.docx.parsed.markitdown.md` được thêm sau đó chưa vào inventory. Đây là lệch chuẩn cần xử lý trước khi mở rộng dataset.
- `Project1/tools/generate_v1.py` là nguồn sinh dữ liệu và kiểm tra toàn vẹn. Mọi thay đổi phải đi qua generator trước khi cập nhật output, không chỉnh JSONL/XLSX thủ công.
- `DATN_BE/src/services/task/workspace/task-workspace.types.ts` định nghĩa task type/status, project, assignee, sprint và quan hệ parent.
- `DATN_BE/src/services/capture/application/work-notes.types.ts` định nghĩa Task Note (title, accomplishments, approach, reason), Document/Report và trạng thái review.
- `DATN_BE/docs/openapi/work-note-events.md` quy định Task Note không là nguồn tri thức chính thức; Document/Report chỉ đủ điều kiện làm nguồn sau phê duyệt. Runtime hiện chưa có consumer event này. Evaluation chỉ kiểm tra **quy tắc kỳ vọng của dataset**, không tuyên bố hệ thống đã index được.

## 3. Thiết kế dữ liệu đề xuất

| Tệp mới trong `Project1` | Nội dung tối thiểu | Liên kết |
| --- | --- | --- |
| `structured/work_tasks.jsonl` | Task bản địa, ID ổn định, project/org, key, title, type, status, priority, assignee, sprint, thời gian, `source_issue_key` | `source_issue_key` trỏ tới issue có thật; không dùng Epic vì Workspace Task chỉ có TASK/BUG/STORY. |
| `structured/task_notes.jsonl` | ID, `task_id`, project, author, title, accomplishments, approach, reason, created/updated | Task và tác giả tồn tại, đúng project và thời gian. |
| `structured/document_reviews.jsonl` | Sự kiện submit/approve/request changes/reject/archive theo document/version, actor, timestamp | Tái dựng được trạng thái và phiên bản có hiệu lực. |
| `structured/work_reports.jsonl` | Member, project, kỳ báo cáo, frequency/scope, nội dung, document refs, trạng thái và review | Kỳ không trùng cho cùng member/project; tài liệu tham chiếu hợp lệ. |
| `evaluation/workflow_cases.jsonl` | Gold cases cho liên kết task-note-document/report, thời điểm, ACL và nguồn được duyệt | Chỉ dùng trong namespace evaluation. |

Chỉ sau khi xử lý 10 tệp phát sinh ở T0, năm tệp mới mới đưa tổng dự kiến về **158/160** file trong `Project1`. Nếu 10 tệp đó bắt buộc ở nguyên vị trí, phải trình lại phương án đóng gói trước khi sinh dữ liệu; không âm thầm nới giới hạn hoặc sửa số đếm manifest. Nội dung note/report là synthetic, tránh các đoạn lặp máy móc. Đề xuất lát đầu: khoảng **48 task** (6 task × 8 project), **1–3 note/task**, một nhóm nhỏ document review và report phủ các luồng chính. Số lượng cuối cùng được điều chỉnh theo chất lượng kịch bản và giới hạn file, không coi tăng số dòng là mục tiêu.

## 4. Công việc theo thứ tự

### T0 — Khôi phục tính nhất quán của package hiện tại

- Truy nguồn 10 tệp Markdown parse từ DOCX, kiểm tra ai đang sử dụng chúng. Phương án đề xuất: nếu chỉ là dẫn xuất phục vụ RetrievalCI Bench, chuyển chúng ra khỏi `Project1` sang vùng artifact của benchmark, giữ nguyên nội dung và cập nhật tham chiếu liên quan. Không xóa file hoặc thay đổi canonical DOCX.
- Đếm lại toàn bộ file thực tế và đối chiếu manifest sau khi xử lý. Nếu không thể chuyển an toàn, dừng tại checkpoint này và trình Thang phương án khác.
- **Đạt:** `Project1` có ≤160 file, inventory bao phủ toàn bộ file trong package theo đúng policy; không có tham chiếu benchmark bị gãy.

### T1 — Khóa contract và chọn kịch bản

- Lập bảng ánh xạ từ Jira issue sang Work Task, enum status/type và quyền theo project; chọn task có DONE, IN_REVIEW, BLOCKED, spillover, đổi assignee và ca đối tác.
- Chốt quy tắc ID ổn định, chronology, phạm vi hiển thị của Task Note, version hiện hành của Document và report period.
- **Đạt:** Mỗi trường sinh ra đều có nguồn/ý nghĩa; không có quan hệ mồ côi hoặc mapping status mơ hồ.

### T2 — Sinh Work Task và Task Note

- Mở rộng generator tại điểm tạo `issues` để tạo task và note từ kịch bản đã chọn; lưu `source_issue_key` nhưng không sửa lịch sử issue.
- Nội dung note nêu việc làm, cách thực hiện và lý do; ít nhất một kịch bản chứa thay đổi quyết định hoặc blocker theo thời gian.
- **Đạt:** Generator chạy lặp cho cùng output; tất cả task/note đúng project, member, ACL và mốc thời gian.

### T3 — Sinh review và Work Report

- Bổ sung review event cho một phần tài liệu có sẵn, gồm ít nhất: approved version, changes requested rồi approved, bản mới chưa duyệt, archived.
- Bổ sung report member/leader ở một số kỳ, có tài liệu tham chiếu và người review hợp lệ; không cho tự duyệt.
- **Đạt:** Có thể tính trạng thái và nguồn hiện hành từ event; report period không trùng và tham chiếu không mồ côi.

### T4 — Evaluation và kiểm định

- Thêm workflow cases: hỏi nguyên nhân của task, truy dấu note → tài liệu, chọn version được duyệt, loại note chưa thành nguồn chính thức, lọc quyền chéo tenant/project, lịch sử của người đã offboard.
- Thêm validation cho khóa ngoại, project/org, timestamp, lịch làm việc, reviewer, ACL, trạng thái cuối, nguồn gold và giới hạn file.
- **Đạt:** Các ca dương/âm đều xác định expected answer và nguồn được/không được cite; validator phát hiện được fixture sai có chủ đích.

### T5 — Đóng gói, đồng bộ và bàn giao

- Cập nhật `manifest.json`, `INGESTION_CONTRACT.md`, `00_START_HERE.md`, `Dataset_Catalog.xlsx` và tài liệu đánh giá liên quan theo output thực tế. Cập nhật version lên v1.3.0 khi dữ liệu hoàn tất.
- Kiểm tra toàn bộ diff; tách dữ liệu evaluation khỏi corpus; rà soát secret, file sinh ngoài ý muốn và nội dung trùng lặp.
- **Đạt:** Manifest count/hash khớp file; package ≤160 file; hướng dẫn ingest ghi rõ Task Note không được đưa vào nguồn tri thức chính thức.

## 5. Quality gates và bằng chứng bàn giao

1. Chạy kiểm định có sẵn của generator và các kiểm thử dataset liên quan; ghi lệnh, số ca đạt/trượt và checksum đầu ra. Trước tiên tái hiện và giải quyết sai lệch 163/153 file ở T0.
2. Sinh lại hai lần trong môi trường sạch và so hash các output mới để chứng minh tính xác định.
3. Đối chiếu thủ công vài chuỗi task → note → review → report ở ít nhất hai project, gồm một ca quyền bị từ chối.
4. Xác nhận số file thật, manifest inventory, Excel catalog và tổng evaluation cases.
5. Rà soát `git status`, complete diff, changed-file list và commit history; code review trước khi báo nhánh sẵn sàng. Không tự push hoặc merge.

## 6. Rủi ro và giới hạn

| Rủi ro | Cách xử lý |
| --- | --- |
| Generator hiện chứa nhiều kiểm tra/count cố định cho v1.2 | Đổi kiểm tra cùng lúc với dữ liệu mới; không xóa assertion chỉ để qua validation. |
| Work Task/Note có contract khác Jira issue | Dùng ánh xạ tường minh, giữ issue nguyên vẹn và kiểm tra từng enum/quan hệ. |
| Cây `Project1` đã có 163 file, vượt giới hạn 160 và lệch manifest 10 file | T0 kiểm tra tham chiếu rồi chuyển artifact parse ra khỏi package nếu an toàn; nếu không, dừng để duyệt lại packaging. |
| 160 file vật lý là giới hạn cứng của package | Tối đa 5 tệp dữ liệu mới dự kiến sau T0; không tạo file phụ trong `Project1`. |
| ACL của tài liệu, task và thành viên khác nhau | Kiểm tra quyền trước khi gán gold source; thêm ca từ chối truy cập. |
| Runtime chưa có Work Note event consumer | Chỉ đánh giá tính đúng của dữ liệu và quy tắc nguồn; không gọi là E2E ingestion của ứng dụng. |

## 7. Điểm duyệt của Thang

Phê duyệt kế hoạch này đồng nghĩa cho phép bắt đầu triển khai **trong repo Dataset trên nhánh task riêng** theo phạm vi ở §1–5, gồm việc di chuyển 10 artifact parse **chỉ khi** xác minh được không làm gãy tham chiếu. Mọi nhu cầu seed DB, sửa API/UI hoặc mở rộng sang repo khác sẽ có kế hoạch và nhánh/PR riêng.

## 8. Kết quả triển khai

- Chuyển nguyên nội dung 10 Markdown parse DOCX sang `RetrievalCI_Bench_v0_2026/examples/project1_parsed_docx/` sau khi xác minh không có tham chiếu trong source Dataset. `Project1` hiện có 159 file, manifest kiểm kê đủ 158 file còn lại.
- Sinh 48 Work Task, 48 Task Note, 58 document review events, 8 Work Report và 21 workflow evaluation cases. Tổng evaluation tăng từ 158 lên 179; 2.500 issue và 1.434 logical document giữ nguyên.
- Có hai LEADER report; APPROVED, CHANGES_REQUESTED và REJECTED đều được phủ. Task Note và report chưa duyệt không đủ điều kiện làm nguồn tri thức.
- Generator tự kiểm định đạt; 8 unit tests cho liên kết, ACL, reviewer, eligibility và tính tái lập đạt. Excel có bốn tab workflow mới, số dòng khớp JSONL.
- Chạy generator thêm một lần và so SHA-256 của 5 JSONL mới, Excel và manifest: cả 7 output giống hệt từng byte. Không có thay đổi nội dung ở các JSONL v1.2 hiện hữu.
- Giới hạn đã xác nhận: dữ liệu cũ gán `DOC-PAY-ADR-001` cho M-018 dù M-018 không có Project Membership tại NSC-PAY. Không thêm review event giả cho tài liệu này; ca evaluation chỉ kiểm tra trạng thái legacy `Superseded`. Fixture test-only `FIX-CONFLICT-POLICY` dùng để kiểm tra event `ARCHIVED`.
- RetrievalCI Bench `tests/test_project.py` chạy trên Windows còn lỗi đường dẫn dấu gạch chéo (`str(tmp_path.resolve())` khác `repo_root`), không liên quan tới việc chuyển artifact và không sửa test để che lỗi.
- Không có `ruff` trong môi trường Python hiện tại; không cài thêm package chỉ để kiểm tra thay đổi nhỏ này.
