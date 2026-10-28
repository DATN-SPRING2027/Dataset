# Northstar (`Dataset/Project1`) — Kiểm Kê Audit & Đối Chiếu Bổ Sung Lên v1.4

Ngày kiểm kê & nâng cấp: `2026-10-28`. Nguồn: các file JSONL trong `Dataset/Project1/structured`, `Dataset/Project1/evaluation` và generator `Dataset/Project1/tools/generate_v1.py` + `workflows_v13.py`. Đây là kiểm kê dữ liệu tái lập trên đĩa, **không phải** xác nhận đã seed vào MongoDB hay đã nối consumer AI runtime.

---

## 1. Bảng Số Liệu Baseline Ban Đầu (v1.3 — Trước Khi Bổ Sung)

| Project | Membership | Jira-like issue | Work Task | Task Note | Document logic | Review event | Work Report |
|---|---:|---:|---:|---:|---:|---:|---:|
| NSC-CART | 9 | 312 | 6 | 6 | 172 | 7 | 1 |
| NSC-CAT | 14 | 313 | 6 | 6 | 177 | 7 | 1 |
| NSC-CHKO | 11 | 313 | 6 | 6 | 175 | 7 | 1 |
| NSC-INV | 9 | 312 | 6 | 6 | 175 | 7 | 1 |
| NSC-ORD | 10 | 312 | 6 | 6 | 175 | 9 | 1 |
| NSC-PAY | 15 | 313 | 6 | 6 | 178 | 7 | 1 |
| NSC-PLAT | 12 | 312 | 6 | 6 | 181 | 7 | 1 |
| NSC-SRCH | 11 | 313 | 6 | 6 | 175 | 7 | 1 |

Tổng v1.3: **91** project membership, **2.500** Jira-like issue, **48** Work Task, **48** Task Note, **1.434** document logic (gồm 26 cấp tổ chức không gắn project), **58** review event, **8** Work Report và **179** ca evaluation.

---

## 2. Phân Loại Audit Bốn Mức Cho Từng Thành Phần Của Northstar

| Hạng mục kiểm kê | Phân loại Audit ở v1.3 | Phát hiện cụ thể khi đối chiếu Contract Continuum | Hành động đã thực hiện ở bản v1.4 |
| :--- | :--- | :--- | :--- |
| **Organization, User, Membership & Role** | **Đã có và đủ** (cần bổ sung bảng ID mapping) | Có 3 org (`ORG-NSC` + 2 đối tác ngoài), 74 thành viên (`71` active, `3` inactive, email `@*.invalid`), 91 project membership, role tường minh và lịch sử offboard. Không dùng entity Team của Continuum. | Giữ nguyên 100% ID cũ; bổ sung `structured/continuum_id_mapping.jsonl` (`449` bản ghi) ánh xạ sang hex24 ObjectId ổn định. |
| **Jira-like Issues (`issues.jsonl`) vs Continuum Work Tasks (`work_tasks.jsonl`)** | **Có nhưng cần bổ sung** | 2.500 issue là kho backlog mô phỏng Jira (không tự đồng nghĩa là Continuum Task). 48 `work_tasks` ở v1.3 mới dùng key có dấu gạch ngang kép (`NSC-CART-WT-01`), thiếu subtask 1 cấp, thiếu trạng thái `CANCELLED`, thiếu checklist `steps`, comment, worklog và chuỗi `task_events`. | Mở rộng lên **64 `work_tasks`** (8 task/project), chuẩn hóa `key` khớp regex Continuum (`NSCCART-1..8`) kèm `legacy_key` bảo toàn tham chiếu cũ, thêm 8 subtask 1 cấp, trạng thái `CANCELLED` + rework, checklist `steps`, **55** comment, **52** worklog và **253** `task_events`. |
| **Group Note 1 — Task Note (`task_notes.jsonl`)** | **Có nhưng cần bổ sung** | Có 48 Task Note ở v1.3 nhưng thiếu cờ ranh giới tri thức tường minh (`knowledge_eligible=false`) và các ca bàn giao sự cố đời sống. | Mở rộng lên **64 `task_notes`** khớp 64 `work_tasks`, gắn cứng `status="CONFIRMED"`, `knowledge_eligible=false`, phủ đủ bàn giao nghỉ ốm/mưa bão/nghỉ phép. |
| **Group Note 2 — Project Document, File, Version & Review** | **Có nhưng cần bổ sung** | Có 1.434 document logic (MD/DOCX/PDF/XLSX) và 58 review event không tự duyệt, nhưng cần thêm dấu vết review tài liệu gắn với sự cố gián đoạn tháng 09/2026 và giữ tổng file vật lý `<= 160`. | Giữ nguyên 1.434 document logic & toàn bộ ID cũ; bổ sung lên **60 `document_reviews`** (vẫn đảm bảo `reviewer != author`); tổng số file vật lý đạt đúng **160 / 160** (không vượt trần). |
| **Group Note 3 — Work Report & Các Kỳ Báo Cáo (`work_reports.jsonl`)** | **Có nhưng cần bổ sung** | Bản v1.3 chỉ có **8** báo cáo (`1 report/project`), toàn bộ là `WEEKLY` của `LEADER`, **chưa có** luồng `MEMBER -> TEAM_LEADER`, **chưa có** báo cáo `DAILY` và chưa đủ các trạng thái `DRAFT` quá hạn / `CHANGES_REQUESTED` / `REJECTED`. | Mở rộng lên **24 `work_reports`** (**3 báo cáo/project**: tổng cộng **10 `LEADER`** duyệt bởi Org `ADMIN` Manager + **14 `MEMBER`** duyệt bởi `TEAM_LEADER`/`ADMIN`, phủ cả `WEEKLY` và `DAILY`, đủ `APPROVED`, `PENDING_REVIEW`, `CHANGES_REQUESTED`, `REJECTED` và `DRAFT` có `is_overdue=true`). |
| **Timeline, OT, Ngày Nghỉ, Sự Cố & Bàn Giao** | **Chưa có** (ở mức cửa sổ gián đoạn cá nhân tường minh cho `work_tasks`) | v1.3 đã có lịch ngày lễ VN `+07:00` và offboarding `M-031`/`M-032`, nhưng chưa có bảng sự kiện nghỉ ốm, mưa bão đứt cáp và nghỉ phép cá nhân tác động trực tiếp lên `work_tasks` & `task_notes`. | Bổ sung đầy đủ các cửa sổ gián đoạn (`M-019` nghỉ ốm, `M-027` mưa bão mất mạng, `M-029` nghỉ phép) kèm bàn giao task, kiểm tra tự động không phát sinh hoạt động thường trong giờ nghỉ trưa `12:00-13:00` hoặc khi đang vắng mặt. |
| **Evaluation, Gold, Evidence & ACL** | **Có nhưng cần bổ sung** | 179 ca ở v1.3 chưa phủ hết luồng báo cáo `MEMBER` vs `LEADER`, `DAILY` report, subtask 1 cấp và chưa gắn nhãn quản trị trạng thái chờ người thật duyệt. | Mở rộng `evaluation/workflow_cases.jsonl` từ 21 lên **32** ca (tổng cộng **190 ca evaluation** trên toàn Northstar), gắn tường minh `review_status = "unreviewed"` (`"chưa duyệt"`) + 2 trường `reviewer_1`, `reviewer_2` cho toàn bộ 190 ca, giữ đủ **10 ca `DENY`** kiểm thử ACL/multi-tenant. |
| **Importer, Consumer Outbox -> AI Index & Handover Runtime** | **Chưa xác minh hoặc chưa có runtime hỗ trợ** | `DATN_BE` chưa có consumer tự động đẩy `capture` outbox sang chỉ mục SAG/RAG và chưa có công cụ import giữ nguyên lịch sử backdate được duyệt chạy. | Ghi rõ trạng thái `IMPORTER_REQUIRED` / `NOT_YET_AVAILABLE` tại [CONTINUUM_DATA_DICTIONARY.md](../CONTINUUM_DATA_DICTIONARY.md); không tự sửa BE/DB và không tuyên bố AI runtime đã tích hợp. |

---

## 3. Bảng Số Liệu Northstar Sau Khi Bổ Sung (v1.4 — Đã Kiểm Chứng Tái Lập 2 Lần)

| Project | Membership | Jira-like issue | Continuum Work Task | Task Note | Document logic | Review event | Work Report (`LEADER` + `MEMBER`) |
|---|---:|---:|---:|---:|---:|---:|---:|
| NSC-CART | 9 | 312 | 8 | 8 | 172 | 7 | 3 |
| NSC-CAT | 14 | 313 | 8 | 8 | 177 | 8 | 3 |
| NSC-CHKO | 11 | 313 | 8 | 8 | 175 | 7 | 3 |
| NSC-INV | 9 | 312 | 8 | 8 | 175 | 7 | 3 |
| NSC-ORD | 10 | 312 | 8 | 8 | 175 | 9 | 3 |
| NSC-PAY | 15 | 313 | 8 | 8 | 178 | 8 | 3 |
| NSC-PLAT | 12 | 312 | 8 | 8 | 181 | 7 | 3 |
| NSC-SRCH | 11 | 313 | 8 | 8 | 175 | 7 | 3 |
| **Tổng cộng** | **91** | **2.500** | **64** | **64** | **1.434** *(gồm 26 cấp org)* | **60** | **24** *(10 LEADER, 14 MEMBER)* |

- **Kiểm chứng tái lập**: Chạy `python -X utf8 -B Dataset/Project1/tools/generate_v1.py` hai lần liên tiếp cho cùng `manifest.json` SHA-256 `AE0515D32DB1E70900F0048D16BA639DD2A5C2861DE74F33EF1F3B0A22C564D3`; tổng số file vật lý **160 / 160**; toàn bộ unit test trong `Dataset/tests/` đạt PASS.
