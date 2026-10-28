# Checklist triển khai dataset bốn organization

Theo [kế hoạch](plan-four-organizations.md), [mapping](../CONTINUUM-DATASET-MAPPING.md), [từ điển dữ liệu](../CONTINUUM_DATA_DICTIONARY.md), [nhật ký nguồn GitHub](../GITHUB_SOURCES_AND_LICENSES.md) và README từng organization.

## Quyết định và kiểm kê

- [x] Xác minh mapping Group Note: Task Note, Project Document và Work Report; kiểm tra quyền và luồng báo cáo Member–Leader (`TEAM_LEADER`/`ADMIN` duyệt), Leader–Manager (chỉ Org `ADMIN` duyệt) theo `DATN_BE/src/services/capture/`.
- [x] Xác định quy mô, kỳ mô phỏng (`+07:00`, `08:00–12:00` & `13:00–17:00`, OT `17:00–22:00`), ngày lễ Việt Nam 2026 và project đại diện; loại trừ hoàn toàn Team/Team Membership, lịch sử AI Chat và entity Notebook thứ tư.
- [x] Kiểm kê Northstar từng loại/field/quan hệ theo 8 project; phân loại 4 mức (đã đủ, cần bổ sung, chưa có, chưa có runtime hỗ trợ) tại [northstar-gap-baseline.md](northstar-gap-baseline.md).
- [x] Kiểm tra contract BE/FE mới nhất và lập [CONTINUUM_DATA_DICTIONARY.md](../CONTINUUM_DATA_DICTIONARY.md) (enum, hex24 ID mapping, ACL, phân loại `API_SUPPORTED` / `IMPORTER_REQUIRED` / `DATASET_METADATA_ONLY` / `EVALUATION_ONLY` / `NOT_YET_AVAILABLE`).
- [x] Khảo sát repo tham chiếu thực tế (`orangehrm/orangehrm` `v5.9` GPL-3.0-or-later, `roxy-wi/IncidentRelay` `v2.4.0` Elastic-2.0, `danluu/post-mortems`, `openmrs/openmrs-core` `2.8.10` MPL-2.0 + Healthcare Disclaimer, `openmrs-contrib-o3-docs` MPL-2.0); ghi đầy đủ tại [GITHUB_SOURCES_AND_LICENSES.md](../GITHUB_SOURCES_AND_LICENSES.md) và `manifest.json` của từng gói.

## Nội dung theo organization

- [x] **Northstar (`Dataset/Project1`, v1.4)**: mở rộng lên 64 `work_tasks`, 64 `task_notes`, 60 `document_reviews`, 24 `work_reports` (`DAILY` & `WEEKLY`, `MEMBER` & `LEADER`), 190 ca evaluation (`review_status="unreviewed"`), `continuum_id_mapping.jsonl`; giữ nguyên ID cũ, 2.500 issue, 1.434 tài liệu logic và trần `160/160` file vật lý.
- [x] **Nova Solutions (`Dataset/Organization2-Nova-Solutions`, v1.0.0 — Waterfall)**: 4 project Waterfall thuần túy (`sprints=[]`, `sprint_id=null`), 6 cổng giai đoạn, tách phạm vi `CR-2026-08`, lỗi UAT hoàn thừa phép nửa ngày `0.5 -> 1.0` buộc làm lại DB v2, 128 task, 84 Task Note, 24 Project Document (28 versions, kèm 8 DOCX), 36 Work Report, 56 ca evaluation.
- [x] **CloudOps Services (`Dataset/Organization3-CloudOps-Services`, v1.0.0 — Kanban)**: 4 luồng Kanban (`sprints=[]`, `sprint_id=null`), giới hạn WIP, 3 bot 24/7 tách biệt con người, sự cố lễ Quốc khánh `02/09` leo thang sang Secondary On-Call do mưa bão, phân biệt workaround tạm thời (`CLDINC-9`) với bản sửa gốc tách pool PgBouncer (`CLDINF-19`), sự cố lệch WAF Thứ Bảy `26/09`, 128 task, 81 Task Note, 24 Project Document (kèm 6 DOCX), 36 Work Report, 56 ca evaluation.
- [x] **MediFlow (`Dataset/Organization4-MediFlow`, v1.0.0 — Hybrid)**: 100% hành chính phi lâm sàng (0 bệnh án/đơn thuốc/PII thật); 3 project `HYBRID` (4 cổng Milestone + 15 Sprint) và 1 project thực địa `WATERFALL` không chia Sprint (`MED-PIL`); phân loại 3 phản hồi phòng khám (`CFB-2026-01` duyệt, `CFB-2026-02` từ chối xuất SĐT ra Excel, `CFB-2026-03` chờ đánh giá chưa có hiệu lực); mưa bão gây spillover `MEDAPT-25` sang Sprint 5 và lùi cổng Pilot M3; 128 task, 82 Task Note, 24 Project Document (kèm 6 DOCX), 36 Work Report, 56 ca evaluation.
- [x] Cả bốn organization có thành viên, org/project membership, role tường minh; timeline làm việc, nghỉ trưa `12:00–13:00`, ngày lễ, OT tối, ca trực có lịch và tình huống nghỉ việc/nghỉ ốm/mưa bão nhất quán.

## Validation, Nghiệm thu con người & Giới hạn chưa thực hiện

- [x] Viết và chạy generators + validators cho cả 4 organization; kiểm tra tái lập bằng **2 lần sinh liên tiếp khớp tuyệt đối SHA-256 `manifest.json`**, kiểm tra khóa ngoại, timeline, review không tự duyệt, ACL và **24 fixture âm** (`negative_cases.json`).
- [x] Tạo bộ evaluation tách biệt hoàn toàn khỏi kho tri thức (`190 + 56 + 56 + 56 = 358` ca benchmark, chia tách `dev`/`test`, có đủ ca `DENY`, mâu thuẫn phiên bản và thiếu bằng chứng); gắn trung thực `review_status = "unreviewed"` (`"chưa duyệt"`).
- [ ] **Chờ con người thực hiện (ngoài phạm vi tự động của AI)**: Hai người độc lập rà soát, phân xử bất đồng và chuyển `review_status` từ `"unreviewed"` sang `"reviewed"` trước khi đóng băng bộ điểm chuẩn cuối cùng.
- [x] Ghi đầy đủ import mapping, giới hạn backdate actor/timestamp, thứ tự nạp và các khoảng trống runtime tại [CONTINUUM_DATA_DICTIONARY.md](../CONTINUUM_DATA_DICTIONARY.md).
- [ ] **Chưa thực hiện theo đúng quy tắc an toàn phạm vi**: Chưa xây runtime importer, chưa seed vào MongoDB và chưa kiểm chứng tích hợp end-to-end với SAG/AI Chat runtime (chờ môi trường đích và task riêng được Thang xác nhận).
- [x] Kiểm tra `git status`/`git diff`, quét không có secret/PII thật/dữ liệu lâm sàng và đồng bộ toàn bộ tài liệu bàn giao.
