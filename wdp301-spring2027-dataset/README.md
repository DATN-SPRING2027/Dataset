# WDP301-SPRING-2027 — Bộ Dataset Synthetic Full 360° cho Continuum AI

**Trạng thái:** 100% dữ liệu tổng hợp (`synthetic = true`, `review_status = "unreviewed"`), thiết kế riêng cho tổ chức đồ án **`WDP301-SPRING-2027`** (`slug: datn-spring2027`, `_id: 6ad76c7d938f3bf53df7335e`) nhằm phục vụ kiểm thử toàn diện và buổi **Bảo vệ Đồ án WDP301**.

## 1. Cam kết cốt lõi
- **Full 360° liên kết thực thể thật:** Toàn bộ Chat 1–1 (`DIRECT`), Chat nhóm (`ROOM`), Task Comments, Task Worklogs, Task Notes (`v1` & `v2`), Work Reports và Handovers (`schemaVersion: 2`) đều nối trực tiếp vào **8 dự án `ACTIVE`**, **47 task thật** (trong tổng `474` task sẵn có) và **25 tài liệu `APPROVED` thật** (trong tổng `143` tài liệu sẵn có) của `WDP301-SPRING-2027`.
- **Bảo toàn 100% dữ liệu cũ:** Không sửa, không xóa bất kỳ bản ghi nào đã có trong `WDP301-SPRING-2027` (`"helo"`, `"Danh"`, dự án `PRTRESDAD131` đã `ARCHIVED`, `165` báo cáo `OVERDUE` cũ, `474` task, `143` tài liệu, `9` DM cũ, `4` handover cũ). Toàn bộ dữ liệu seed dùng tiền tố ObjectId định danh cố định **`6f301`** và mặc định chạy chế độ **insert-only (`$setOnInsert`)**.
- **Ẩn danh tuyệt đối trong Git:** Không lưu bất kỳ email cá nhân, mật khẩu, token hay MongoDB URI nào trong repo. Mọi bản ghi dùng **11 alias nhân vật** (`actor_pm_admin`, `actor_be_lead`, ...) và ánh xạ lúc chạy thông qua file cục bộ ngoài Git (mặc định `../.local/wdp301-actor-map.json`).
- **0 tin nhắn AI seed sẵn & tách biệt Evaluation:** `seed/` không chứa bất kỳ tin nhắn `authorType: "ASSISTANT"` hay đáp án gold nào (`containsGoldAnswers: false`). Toàn bộ `48` ca đánh giá (`28 dev` + `20 test` rời nhau 100% về ID nguồn bằng chứng) và `3` kịch bản Live E2E nằm độc lập tại `eval/wdp301_eval_cases.json`.

---

## 2. Cấu trúc thư mục (phân tầng theo `CONTINUUM-DATASET-MAPPING.md`)

```text
wdp301-spring2027-dataset/
├── README.md                                # Tài liệu hướng dẫn, quy mô, ma trận edge case & lệnh seed
├── metadata/                                # Tầng (B): Lịch sự kiện 6 tuần (+07:00) & bảng tham chiếu
│   └── timeline_and_mapping.json
├── seed/                                    # Tầng (A): Dữ liệu import vào ứng dụng (0 gold, 0 AI reply)
│   ├── chat_fixture.json                    # 7 DIRECT + 4 ROOM (213 tin nhắn người-với-người)
│   └── workspace_enrichment_fixture.json    # 56 comments, 32 worklogs, 24 notes, 18 reports, 2 handovers
├── eval/                                    # Tầng (C): Benchmark đánh giá & ACL DENY (tách khỏi seed)
│   └── wdp301_eval_cases.json               # 48 ca (28 dev / 20 test rời nguồn) + 3 kịch bản Live E2E
└── scripts/
    ├── _wdp301_catalog.mjs                  # Danh mục dự án/task/doc thật & 11 actor alias
    ├── _wdp301_chat_data.mjs                # Kịch bản 7 DM + 4 Room (đủ 10 nhóm edge case)
    ├── _wdp301_workspace_eval_data.mjs      # Comments, worklogs, notes, reports, handovers & eval cases
    ├── generate_wdp301_dataset.mjs          # Bộ sinh tất định (chạy lại tạo JSON giống hệt từng byte)
    ├── seed_wdp301_dev.mjs                  # Seeder an toàn đa DB (--dry-run / --apply / --verify / --reset-fixture)
    └── seed_wdp301_dev.test.mjs             # Unit test cho guard an toàn, mốc thời gian, idempotency & reset
```

Kiểm thử toàn vẹn Python (chạy chung với `pytest` của repo `Dataset`):
- `../tests/test_wdp301_dataset.py`

---

## 3. Quy mô dữ liệu & Ma trận 10 nhóm Edge Cases

| Thành phần | Quy mô | Điểm kiểm thử nổi bật |
| --- | ---: | --- |
| **Chat 1–1 (`DIRECT`)** | **7 hội thoại / 180 tin** | Tái sử dụng sạch 5 DM có sẵn qua `directKey` (giữ nguyên `"helo"`, `"Danh"`). `DM-01` có **86 tin** (**36 tin ngoài trang đầu `limit=50`**), mốc tuần trước (`-7d`), hôm qua (`-1d`), hôm nay (`0d`), đính chính `BE-3` (`15p -> 10p`), tin kỹ thuật dài `> 1.300` ký tự (`BE-114`), tin đã sửa/đã xóa sẵn, **3 ứng viên Live E2E**, xung đột chưa chốt `GENERAL-4`. |
| **Chat nhóm (`ROOM`)** | **4 phòng / 33 tin** | `#wdp301-war-room`, `#be-db-sag-engineering`, `#fe-design-docs`, `#wdp301-leaders-private` (chứa canary `CANARY-WDP-LEADERS-ONLY-03`). Phục vụ kiểm tra chặn `422 CHAT_ASSISTANT_DIRECT_ONLY` và ACL phòng riêng. |
| **Task Comments** | **56 bình luận** | Phủ đủ 8 dự án `ACTIVE`, bám sát `continuum_task.task_comments` strict `$jsonSchema`. |
| **Task Worklogs** | **32 bản ghi giờ công** | Đủ giờ hành chính T2–T6 (`+07:00`) + 2 ca OT tối có lý do rõ ràng (`BE-1`, `SAG-26`). |
| **Task Notes** | **24 ghi chú (`CONFIRMED`)** | 20 bản ghi chuẩn v1 (`whatDone`/`howSolved`/`whyThisWay`) + 4 bản ghi chuẩn v2 (`contentSchemaVersion: 2`, `contentMarkdown`), kèm `work_note_versions`. |
| **Work Reports** | **18 báo cáo tuần** | Đủ 2 scope (`MEMBER`, `LEADER`), đủ 5 trạng thái (`APPROVED`, `PENDING_REVIEW`, `CHANGES_REQUESTED`, `DRAFT`, `OVERDUE`), gắn `documentIds` thật. |
| **Handovers (`v2`)** | **2 gói hoàn chỉnh** | 1 gói `OPEN` đã xuất bản Revision 1 trên `BE` (`BE-1/111/112`) + 1 gói `COMPLETED` có `completionReviewNote` trên `FE`; không đụng `handover_v2_open_unique` của 4 handover cũ. |
| **Evaluation & ACL** | **48 ca + 3 Live E2E** | `28 dev` / `20 test` rời nguồn 100%, `7` ca ACL DENY / Room `422`, `2` ca `INSUFFICIENT_EVIDENCE`, ranh giới `23:48`/`00:12 (+07:00)`, phân biệt 2 tài khoản cùng tên `"Danh"`, Prompt Injection OWASP LLM01, canary bảo mật `CANARY-WDP-PRIV-01/02`. |

---

## 4. Quy ước ánh xạ nhân vật cục bộ (Ngoài Git)
Tạo file cục bộ ngoài repo Git (ví dụ `..\.local\wdp301-actor-map.json`, **tuyệt đối không commit**):

```json
{
  "organizationId": "6ad76c7d938f3bf53df7335e",
  "organizationSlug": "datn-spring2027",
  "actors": {
    "actor_pm_admin": "<24-hex-user-id>",
    "actor_be_lead": "<24-hex-user-id>",
    "actor_db_sag_lead": "<24-hex-user-id>",
    "actor_fe_lead": "<24-hex-user-id>",
    "actor_fe_dev": "<24-hex-user-id>",
    "actor_fe_offboarding": "<24-hex-user-id>",
    "actor_doc_lead": "<24-hex-user-id>",
    "actor_same_name_general": "<24-hex-user-id>",
    "actor_admin_non_member": "<24-hex-user-id>",
    "actor_general_offboarding": "<24-hex-user-id>",
    "actor_general_successor": "<24-hex-user-id>"
  }
}
```

Khi chạy `--apply`, seeder sẽ xác minh cả 11 `userId` đều đang `ACTIVE` trong `continuum_iam.organization_memberships` của `WDP301-SPRING-2027` và tự động lấy `fullName` thực tế từ `continuum_iam.users`.

---

## 5. Hướng dẫn chạy Seed an toàn, Verify & Rollback

### 5.1 Tái sinh JSON tất định (nếu chỉnh sửa kịch bản)
```powershell
node wdp301-spring2027-dataset/scripts/generate_wdp301_dataset.mjs
```

### 5.2 Dry-run (mặc định, 0 lệnh ghi DB)
```powershell
node wdp301-spring2027-dataset/scripts/seed_wdp301_dev.mjs --dry-run --anchor-date 2026-11-28 --actor-map ..\.local\wdp301-actor-map.json
```

### 5.3 Apply lên môi trường dev cô lập (insert-only mặc định)
Yêu cầu đồng thời:
- `NODE_ENV=development` và `DATN_DB_ENV=development`
- `--expected-org-id=6ad76c7d938f3bf53df7335e`
- Nếu đích là cụm remote (không phải loopback), bắt buộc truyền tường minh `--approved-cluster-host=<exact-hostname>` (chặn mọi host mang nhãn `prod/staging/uat/live`, bắt buộc TLS và xác thực).

```powershell
$env:NODE_ENV='development'; $env:DATN_DB_ENV='development'
node wdp301-spring2027-dataset/scripts/seed_wdp301_dev.mjs --apply `
  --anchor-date 2026-11-28 `
  --env-file ..\DATN_BE\.env `
  --actor-map ..\.local\wdp301-actor-map.json `
  --expected-org-id 6ad76c7d938f3bf53df7335e `
  --approved-cluster-host <exact-dev-cluster-host>
```

### 5.4 Kiểm chứng toàn vẹn (`--verify`)
```powershell
node wdp301-spring2027-dataset/scripts/seed_wdp301_dev.mjs --verify `
  --anchor-date 2026-11-28 `
  --env-file ..\DATN_BE\.env `
  --actor-map ..\.local\wdp301-actor-map.json `
  --expected-org-id 6ad76c7d938f3bf53df7335e
```

### 5.5 Rollback sạch (`--reset-fixture`)
Chỉ xóa đúng các bản ghi mang `_id` tiền tố `6f301` do fixture tạo ra (bảo toàn 100% 5 hội thoại DM có sẵn, 3 tin nhắn cũ `"helo"`/`"Danh"`, 474 task, 143 tài liệu, 165 báo cáo cũ và 4 handover cũ):
```powershell
$env:NODE_ENV='development'; $env:DATN_DB_ENV='development'
node wdp301-spring2027-dataset/scripts/seed_wdp301_dev.mjs --reset-fixture `
  --env-file ..\DATN_BE\.env `
  --actor-map ..\.local\wdp301-actor-map.json `
  --expected-org-id 6ad76c7d938f3bf53df7335e `
  --approved-cluster-host <exact-dev-cluster-host>
```

### 5.6 Chạy toàn bộ bộ test
```powershell
node --test wdp301-spring2027-dataset/scripts/seed_wdp301_dev.test.mjs
ruff check tests/test_wdp301_dataset.py
pytest tests/test_wdp301_dataset.py -q
```
