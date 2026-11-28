# Continuum AI — Synthetic 1–1 Human DM Dataset (`@continuumAI`)

**Trạng thái:** Bộ dữ liệu synthetic 100% (`synthetic = true`) phục vụ phát triển, kiểm thử chất lượng truy xuất tiếng Việt, kiểm thử cô lập quyền (ACL / cross-conversation / cross-org) và kiểm thử đột biến nguồn (`edit`/`delete`) cho tính năng `@continuumAI` trong chat riêng 1–1.

- **Không chứa dữ liệu thật, không chứa mật khẩu/credentials.**
- **Không pre-seed câu trả lời AI:** toàn bộ `82` tin nhắn trong fixture là tin nhắn giữa người với người theo đúng schema `chat_conversation_messages` hiện hành của `DATN_BE` (để trống `authorType`/`contentVersion` như tin cũ để kiểm chứng tương thích ngược theo `contract.md`). Mọi câu trả lời bot (đặc biệt ở kịch bản sửa/xóa nguồn trước và sau khi AI đăng) phải do runtime thật (`DATN_BE` + `SAG`) sinh ra.
- **Tách biệt tuyệt đối dữ liệu seed và tập đánh giá:** `seed/dm_seed_fixture.json` (`containsGoldAnswers: false`) hoàn toàn không chứa đáp án mẫu, nhãn kết luận hay câu hỏi benchmark; toàn bộ câu hỏi và tiêu chí chấm nằm riêng tại `eval/dm_eval_cases.json` (`19` ca đánh giá + `3` kịch bản live E2E, `review_status = "unreviewed"` cho đến khi được người thẩm định độc lập rà soát).

---

## 1. Cấu trúc thư mục

```text
continuum-dm-ai-dataset/
├── README.md                        # Tài liệu cấu trúc, neo thời gian và hướng dẫn seed idempotent
├── seed/
│   └── dm_seed_fixture.json         # Dữ liệu seed 100% tin người-với-người (82 tin / 3 hội thoại DIRECT)
├── eval/
│   └── dm_eval_cases.json           # 19 ca đánh giá (dev/test rời nhau) + 3 kịch bản live E2E edit/delete
└── scripts/
    ├── seed_dm_chat_dev.mjs         # Script seed MongoDB idempotent với các cổng an toàn môi trường dev
    └── seed_dm_chat_dev.test.mjs    # Unit test cho guard an toàn, mốc thời gian, directKey & idempotency
```

Kiểm thử tính toàn vẹn phía Python (chạy cùng `pytest` của repo `Dataset`):
- `../tests/test_continuum_dm_dataset.py`

---

## 2. Quy mô dữ liệu & Sơ đồ ID tất định (Deterministic IDs)

| Hội thoại | Key | Tổ chức | Thành viên | Số tin nhắn | Mục đích kiểm thử |
| --- | --- | --- | --- | ---: | --- |
| **A ↔ B** | `dm_org1_ab` | Org 1 (`continuum-ai-labs`) | `member1@continuum.ai` (A), `member2@continuum.ai` (B) | **68** | Lịch sử sâu ngoài trang đầu (`#01`–`#18`, ngoài cửa sổ `limit=50` của UI), tuần trước (`-7d`), trao đổi giữa tuần (`-5d`..`-2d`), thảo luận hôm qua (`-1d`) gồm tin kỹ thuật dài (>1200 ký tự), tin đính chính (`PAY-123`), tin đã sửa/đã xóa sẵn, 3 tin ứng viên cho live E2E sửa/xóa, và 2 tin đề xuất mâu thuẫn chưa chốt (`INF-610`, `#67`–`#68`). |
| **A ↔ C** | `dm_org1_ac` | Org 1 (`continuum-ai-labs`) | `member1@continuum.ai` (A), `member3@continuum.ai` (C) | **8** | Cô lập cùng tổ chức, khác hội thoại: chứa canary độc nhất `CANARY-AC-991` (`ORCHID-8842-PRIVATE`, `420 triệu VNĐ`, `VinaPay-VIP-09`) và `CANARY-AC-992` (`PHOENIX-ALPHA`, `18.5%`) ngay trong ngày hôm qua (`-1d`). |
| **Org 2 X ↔ Y** | `dm_org2_xy` | Org 2 (`datn-dev` hoặc fallback `dm-ai-isolation-org2`) | 2 tài khoản độc lập của Org 2 | **6** | Cô lập khác tổ chức: chứa canary độc nhất `CANARY-ORG2-774` (`COBALT-7741-ORG2`, `DeltaAudit`, `22/12 lúc 10:00`) và `CANARY-ORG2-775` (`QUARTZ-5509-ORG2`). |

### Thành viên ngoài hội thoại bắt buộc xác minh (`verifiedNonMemberActorKeys`)
- `member3@continuum.ai` (**C**, cùng Org 1): chỉ là thành viên `dm_org1_ac`, tuyệt đối **không** ở trong `dm_org1_ab`.
- `manager@continuum.ai` (**Manager**, vai trò `ADMIN` của Org 1): tuyệt đối **không** ở trong `dm_org1_ab`, `dm_org1_ac` hay `dm_org2_xy`.
- Người dùng Org 2: tuyệt đối **không** ở trong bất kỳ hội thoại nào của Org 1.

### Quy ước ID tất định
- Tin nhắn `dm_org1_ab`: ObjectId `6928d1000000000000000001` .. `6928d1000000000000000068` (UUIDv4 `clientMessageId`: `6928d100-0000-4000-8000-000000000001` .. `68`).
- Tin nhắn `dm_org1_ac`: ObjectId `6928d2000000000000000001` .. `6928d2000000000000000008`.
- Tin nhắn `dm_org2_xy`: ObjectId `6928d3000000000000000001` .. `6928d3000000000000000006`.
- `directKey`: tính tự động theo đúng chuẩn `MongoChatRepository.createDirect`:
  ```text
  <organizationId_hex_lower>:<sorted_userId_1>:<sorted_userId_2>
  ```
  Nếu cặp người dùng (ví dụ `member1` ↔ `member3` trên môi trường dev) đã có sẵn hội thoại `DIRECT` khớp `directKey`, script tự động **tái sử dụng `_id` hiện có** để tránh đụng unique index `directKey_1` và không làm mất tin nhắn cũ.

---

## 3. Cơ chế neo thời gian tương đối (`--anchor-date`, `Asia/Ho_Chi_Minh`)

Mọi tin nhắn trong `seed/dm_seed_fixture.json` lưu thời gian tương đối bằng `dayOffset` + `timeLocal` theo múi giờ Việt Nam (`Asia/Ho_Chi_Minh`, `UTC+07:00`):
- Mặc định `--anchor-date` là **ngày hiện tại theo giờ Việt Nam (`Asia/Ho_Chi_Minh`)**, có thể ghim cố định để tái lập hoàn toàn bằng `--anchor-date YYYY-MM-DD`.
- **`dayOffset = 0`** (“hôm nay”): 6 tin nhắn buổi sáng (`#63`–`#68`), gồm 2 đề xuất mâu thuẫn chưa chốt cho `INF-610` (`#67`–`#68`).
- **`dayOffset = -1`** (“hôm qua”): 16 tin nhắn thảo luận (`#47`–`#62`) trong A–B, kèm tin canary cùng ngày ở A–C và Org 2 để kiểm tra bộ lọc phạm vi thời gian không bao giờ rò sang chat khác.
- **`dayOffset = -7`** (“tuần trước”): 12 tin nhắn (`#11`–`#22`, trong đó `#11`–`#18` nằm ngoài trang 50 tin gần nhất!). Về mặt lịch ISO (Thứ Hai–Chủ Nhật), `anchorDate - 7` **luôn luôn** rơi vào tuần lịch trước bất kể ngày chạy là thứ mấy trong tuần.
- **`dayOffset = -18` .. `-14`** (lịch sử cũ ngoài trang đầu): 10 tin nhắn (`#01`–`#10`), nằm hoàn toàn ngoài trang đầu (`limit=50`) của UI chat để kiểm thử nhảy về tin nguồn qua `aroundMessageId`.
- Tin đã sửa sẵn (`editedOffsetMinutes`): `#09` (`-14d`, off-page), `#38` (`-3d`), `#55` (`-1d`, `OPS-307`).
- Tin đã xóa sẵn (`deletedOffsetMinutes`, `content: ""`): `#20` (`-7d`), `#41` (`-3d`).

---

## 4. Tin nhắn ứng viên cho Live E2E Sửa / Xóa nguồn (Runtime thật)

Các ID sau được chuẩn bị sẵn trong `dm_org1_ab` (KHÔNG có tin bot pre-seed đi kèm):

| Kịch bản | Mã chủ đề | Message ID | Người gửi | Luồng kiểm thử với runtime thật |
| --- | --- | --- | --- | --- |
| **Sửa sau khi AI đăng** (`LIVE-E2E-001`) | `E2E-EDIT-401` | `6928d1000000000000000059` | A (`member1`) | Hỏi `@continuumAI` về `E2E-EDIT-401` → AI trả lời trích `#59` (`5.000.000 VNĐ`) → A sửa `#59` thành `8.000.000 VNĐ` → tin AI cũ giữ nguyên nội dung + hiện nhãn **Tin nguồn đã sửa** + mở được bản mới; lượt hỏi mới trả `8.000.000 VNĐ`. |
| **Xóa sau khi AI đăng** (`LIVE-E2E-002`) | `E2E-DEL-402` | `6928d1000000000000000060` | B (`member2`) | Hỏi `@continuumAI` về `E2E-DEL-402` → AI trả lời trích `#60` (`23:15`, `reconcile-02`) → B xóa `#60` → tin AI cũ giữ nguyên nội dung + hiện nhãn **Tin nguồn đã xóa** + vô hiệu hóa liên kết; lượt hỏi mới trả thiếu căn cứ. |
| **Đổi/xóa trước khi AI đăng** (`LIVE-E2E-003`) | `E2E-RACE-403` | `6928d1000000000000000061` | A (`member1`) | Gửi `@continuumAI` hỏi `E2E-RACE-403`, đồng thời sửa/xóa `#61` trước khi worker commit → hủy đăng kết quả cũ với mã lỗi riêng cho nguồn thay đổi. |

---

## 5. Hướng dẫn chạy Seed (Idempotent) & Kiểm thử

### 5.1 Dry-run (mặc định, không ghi DB)
```powershell
# Dry-run offline (không cần MONGODB_URI)
node continuum-dm-ai-dataset/scripts/seed_dm_chat_dev.mjs --dry-run --anchor-date 2026-11-28

# Dry-run có kết nối để kiểm tra độ khớp tài khoản trong continuum_iam (không ghi DB)
node continuum-dm-ai-dataset/scripts/seed_dm_chat_dev.mjs --dry-run --env-file ..\DATN_BE\.env
```

### 5.2 Apply vào môi trường dev cô lập (idempotent, chạy lặp không tạo trùng)
Script **chặn ghi** trừ khi cả `NODE_ENV=development` và `DATN_DB_ENV=development` đều được đặt, URI MongoDB hợp lệ (không chọn DB ở path, không tắt TLS trên Atlas, không chứa nhãn hostname production) và không log bất kỳ secret nào.

```powershell
$env:NODE_ENV = "development"
$env:DATN_DB_ENV = "development"
node continuum-dm-ai-dataset/scripts/seed_dm_chat_dev.mjs --apply --env-file ..\DATN_BE\.env

# Xác minh chỉ đọc sau khi seed
node continuum-dm-ai-dataset/scripts/seed_dm_chat_dev.mjs --verify --env-file ..\DATN_BE\.env
```

> **Tính an toàn khi chạy lặp:** Script upsert tin nhắn theo `_id` tất định và chỉ cập nhật `lastMessageAt`/`lastMessagePreview` nếu hội thoại chưa có tin mới hơn. Các tin nhắn live hoặc phản hồi `@continuumAI` đã sinh trong quá trình kiểm thử sẽ được **giữ nguyên hoàn toàn**.

### 5.3 Chạy bộ kiểm thử tự động
```powershell
# Kiểm thử unit & idempotency của script seed (Node built-in test runner)
node --test continuum-dm-ai-dataset/scripts/seed_dm_chat_dev.test.mjs

# Kiểm thử tính toàn vẹn fixture, tách biệt seed/eval, canary & timeline (Python pytest)
pytest tests/test_continuum_dm_dataset.py -q
```
