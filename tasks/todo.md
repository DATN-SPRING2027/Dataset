

## Giai đoạn 8 — Nâng cấp độ chân thực vận hành dự án thật (v1.2 — P0 + P1 + P2)

- [x] **T8.1 (P0 — Calendar, OT & Timezone)** Áp dụng múi giờ `+07:00`, giờ hành chính `08:00–12:00` & `13:00–17:00` (nghỉ trưa `12:00–13:00`), khung giờ OT buổi tối `17:00–22:00+07:00`, nghỉ T7/CN và 5 ngày lễ Việt Nam (123 ngày làm việc chính thức), 3 ngày Thứ Bảy trực chiến sự cố P0/P1 và 4 Bot hệ thống 24/7.
- [x] **T8.2 (P0 — Multi-Tenant ACL & Offboarding)** Chặn triệt để rò rỉ quyền nội bộ sang đối tác `ORG-MERIDIAN` / `ORG-PULSEPAY`, đảm bảo 0 hoạt động của cựu nhân viên sau `left_at`, bàn giao nghỉ phép (PTO) và 71/71 thành viên active đều tham gia dự án.
- [x] **T8.3 (P1 — Agile Sprint Spillover & Project Health)** Chuyển tiếp toàn bộ open issues từ Sprints 1..12 đã đóng sang Sprint 13 kèm changelog `field: "sprint"`, phân hóa tỷ lệ Done/Blocked theo dự án, và đồng bộ `CHKO-005` (`Blocked`) với `FT-CHKO-007`.
- [x] **T8.4 (P2 — Content Diversity & 158 Evaluation Cases)** Thay thế hậu tố `Phase N` bằng 28 khía cạnh kỹ thuật, bổ sung `parent_key` Epic, vòng lặp review/unblock phi tuyến tính, 12 mẫu tài liệu bundle, đa dạng hóa người chạy test (5 QA) và nâng tổng số evaluation cases lên 158.
