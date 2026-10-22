

## Giai đoạn 8 — Nâng cấp độ chân thực vận hành dự án thật (Enterprise Realism v1.2 — P0 + P1 + P2)

- **Nhánh triển khai:** `feat/Thang-dataset-realism-ot-agile-db`
- **Lịch làm việc, Nghỉ trưa, OT & Ngày lễ Việt Nam (`UTC+07:00`):**
  - Toàn bộ timestamp thực thi trong `issues.jsonl`, `issue_comments.jsonl`, `issue_changelog.jsonl`, `test_execution_results.jsonl`, và `recorded_at` của `documents.jsonl` dùng định dạng ISO 8601 kèm múi giờ Việt Nam `+07:00`.
  - Giờ hành chính: `08:00–12:00` và `13:00–17:00` (nghỉ trưa `12:00–13:00` có 0 hoạt động của con người).
  - Khung giờ OT buổi tối: `17:00–22:00+07:00` (`is_overtime`, `overtime_hours`, `work_mode`, `business_hours_elapsed`), tập trung ở 2 dự án `At Risk` (`NSC-CHKO`, `NSC-PAY`) và các ngày cuối Sprint.
  - Nghỉ Thứ Bảy, Chủ Nhật và 5 ngày lễ Việt Nam trong kỳ (`2026-04-27`, `2026-04-30`, `2026-05-01`, `2026-09-01`, `2026-09-02`) = **123 ngày làm việc chính thức** (20 ngày đầu 12 docs/ngày + 103 ngày sau 11 docs/ngày = 1.373 bundle docs).
  - Ngoại lệ OT cuối tuần chỉ diễn ra vào 3 ngày Thứ Bảy sự cố P0/P1 (`2026-08-29`, `2026-09-26`, `2026-10-10` từ `17:00–22:00+07:00`) trên 6 ticket sự cố/release (`CHKO-012`, `CHKO-015`, `PAY-002`, `PAY-003`, `CHKO-005`, `PLAT-005`).
  - 4 Bot hệ thống (`BOT-SFTP-SYNC`, `BOT-INV-EXPIRY`, `BOT-CI-RUNNER`, `BOT-ALERT-MANAGER`) hoạt động 24/7.
- **Cách ly quyền đa tenant, Offboarding & Nghỉ phép (PTO):**
  - Khắc phục rò rỉ ACL đa tenant: 13 thành viên đối tác/khách hàng (`ORG-MERIDIAN`, `ORG-PULSEPAY`) chỉ tham gia dự án với vai trò `external_collaborator` và không bao giờ kế thừa nhóm nội bộ Northstar (`GRP-CHECKOUT`, `GRP-CATALOG`, v.v.).
  - Sửa lỗi vi phạm thời gian nghỉ việc (`M-018`, `M-045`, `M-070` có 0 hoạt động sau `left_at`, bàn giao ticket trước ngày nghỉ) và bổ sung bàn giao nghỉ phép ngắn hạn (PTO handover).
  - Phân bổ đủ 71/71 thành viên active tham gia vào dự án; phân bổ thực thi 84 test cases cho 5 QA (`M-010`, `M-037`..`M-040`).
- **Quy luật Agile/Scrum, Đa dạng hóa nội dung & Bộ 158 Evaluation Cases:**
  - Chuyển tiếp (Spillover) toàn bộ open issues từ các Sprint 1..12 đã đóng sang `Sprint 13` (`status: "active"`) kèm lịch sử `field: "sprint"` và `spillover_count`.
  - Phân hóa tiến độ 8 dự án (`NSC-CAT` ~73% Done đến `NSC-PAY` ~34% Done), đồng bộ `CHKO-005` (`Blocked`) với `FT-CHKO-007`, loại bỏ hậu tố `Phase N` máy móc, bổ sung `parent_key` (Epic -> Story/Task/Bug), vòng lặp review/unblock phi tuyến tính, 12 mẫu tài liệu bundle và nâng bộ kiểm thử đánh giá lên **158 evaluation cases**.
