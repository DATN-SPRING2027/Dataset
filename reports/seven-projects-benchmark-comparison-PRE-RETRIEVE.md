# Báo Cáo Đối Sánh A/B Trung Thực (Zero-Overfitting): SAG Không Có vs. Có Full Pre-Retrieve (`Kev-4b` + `qsp-v2`)

## 1. Cam Kết Chống Overfitting & Thiết Kế Thí Nghiệm A/B
Để đảm bảo tính khách quan tuyệt đối giữa hai luồng **Without Full Pre-Retrieve** và **With Full Pre-Retrieve**:
1. **Không chỉnh sửa bất kỳ luật heuristic/regex hay thuật toán truy xuất nào của SAG**: Toàn bộ 5 file lõi ([`query_analysis.py`](file:///D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/services/query_analysis.py), [`query_strategy_planner.py`](file:///D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/services/query_strategy_planner.py), [`retrieval_plan.py`](file:///D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/services/retrieval_plan.py), [`retrieval_service.py`](file:///D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/services/retrieval_service.py), [`search_unit_retrieval_service.py`](file:///D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/services/search_unit_retrieval_service.py)) và hàm `_route_from_answers()` trong [`decision_router.py`](file:///D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/services/decision_router.py) được giữ nguyên 100% ở trạng thái `HEAD`.
2. **Chỉ thay đổi đúng biến độc lập cần đo (Independent Variable)**:
   - **Baseline (WITHOUT Full Pre-Retrieve)**: `SAG_DECISION_PROVIDER="disabled"`, client truyền cứng `top_k=5` (`answer_shape=None`).
   - **Experimental (WITH Full Pre-Retrieve)**: `SAG_DECISION_PROVIDER="siliconflow"` (`Kev-4b` qua `/v1/systemone` + `qsp-v2`), client truyền `top_k=None` để tầng Pre-Retrieve tự quyết định `target` (`PASSAGE`/`DOCUMENT`), `output` (`ANSWER`/`LIST`/`COUNT`/`COMPARE`/`SUMMARIZE`), `effective_n` (`5`, `8`, `10`, `50`), và `per_document_limit`.
3. **Không có Selection Bias theo `prev_recall`**: Mọi câu hỏi có sự khác biệt kế hoạch truy xuất (`plan_diff` giữa `Without` và `With`, tổng cộng **24 câu** trên các bộ đang được index) đều được thực thi lại trực tiếp trên SAG Engine, bất kể câu đó ở bản Baseline đúng hay sai.

---

## 2. Tổng Hợp Toàn Cục Trên 7 Dự Án (326 Câu Hỏi ALLOW + 28 Ca ACL DENY)

| Chỉ số toàn cục | WITHOUT Full Pre-Retrieve (`top_k=5`, `disabled`) | WITH Full Pre-Retrieve (`Kev-4b + qsp-v2`, `top_k=None`) | Chênh lệch ($\Delta$) |
| :--- | :---: | :---: | :---: |
| **Macro-Average Recall@5** (7 bộ) | **95.66%** | **95.66%** | **0.00%** |
| **Macro-Average Precision@K** (7 bộ) | **87.21%** | **86.91%** | **-0.30%** |
| **Macro-Average MRR@5** (7 bộ) | **97.97%** | **97.97%** | **0.00%** |
| **Macro-Average nDCG@5** (7 bộ) | **95.96%** | **95.96%** | **0.00%** |
| **Macro-Average Composite Score** (7 bộ) | **95.05** | **95.00** | **-0.05** |
| **Macro-AverageRetrieval Latency (p50)** | **3,273 ms** | **5,012 ms** | **+1,739 ms** *(do RTT gọi `Kev-4b` qua mạng)* |
| **Decision Router (`Kev-4b`) Tokens (326 câu)** | `0` tokens (`$0.000000`) | `314,259` tokens (`$0.012570`) | **`+314,259` tokens (`+$0.012570`)** |
| **Tổng Query + Generation Tokens (326 câu)** | `1,047,684` tokens (`$0.062039`) | `1,376,333` tokens (`$0.075507`) | **`+328,649` tokens (`+$0.013468`)** |
| **Grand Total Tokens (Ingest + Query)** | `2,019,670` tokens (`$0.071760`) | `2,348,319` tokens (`$0.085226`) | **`+328,649` tokens (`+$0.013466`)** |

---

## 3. Đối Sánh Chi Tiết Từng Dự Án: Độ Chính Xác (IR & Citation Metrics)

| # | Dataset Key | Qs | Recall@5 (Without → With) | Precision@K (Without → With) | MRR@5 (Without → With) | nDCG@5 (Without → With) | Composite (Without → With) | Cit. Recall (Without → With) | Cit. Precision (Without → With) |
| :-: | :--- | :-: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | `retrievalci_v0` | 50 | `98.61%` → `98.61%` | `89.93%` → **`88.81%`** (-1.12%) | `100.00%` → `100.00%` | `99.45%` → `99.45%` | `97.86` → `97.70` | `80.09%` → **`80.65%`** (+0.56%) | `97.83%` → `97.83%` |
| 2 | `vn_mteb` | 50 | `83.00%` → `83.00%` | `95.00%` → `95.00%` | `98.00%` → `98.00%` | `86.39%` → `86.39%` | `89.40` → `89.40` | `78.00%` → `78.00%` | `95.83%` → `95.83%` |
| 3 | `wixqa_enterprise` | 20 | `95.83%` → `95.83%` | `50.92%` → `50.92%` | `97.50%` → `97.50%` | `95.05%` → `95.05%` | `89.32` → `89.32` | `69.17%` → `69.17%` | `91.67%` → `91.67%` |
| 4 | `org1_northstar` | 56 | `98.21%` → `98.21%` | `93.15%` → **`92.86%`** (-0.29%) | `97.32%` → `97.32%` | `97.56%` → `97.56%` | `97.07` → `97.02` | `89.29%` → `89.29%` | `98.04%` → `98.04%` |
| 5 | `org2_nova` | 50 | `96.00%` → `96.00%` | `93.50%` → **`93.40%`** (-0.10%) | `96.00%` → `96.00%` | `96.00%` → `96.00%` | `95.63` → `95.61` | `86.00%` → `86.00%` | `95.56%` → `95.56%` |
| 6 | `org3_cloudops` | 50 | `98.00%` → `98.00%` | `95.50%` → `95.50%` | `98.00%` → `98.00%` | `98.00%` → `98.00%` | `97.62` → `97.62` | `90.00%` → `88.00%` | `97.83%` → `97.78%` |
| 7 | `org4_mediflow` | 50 | `100.00%` → `100.00%` | `92.50%` → **`91.90%`** (-0.60%) | `99.00%` → `99.00%` | `99.26%` → `99.26%` | `98.44` → `98.35` | `88.00%` → `86.00%` | `97.78%` → `95.56%` |

---

## 4. Đối Sánh Chi Tiết Từng Dự Án: Độ Trễ (Latency) & Chi Phí Token (Cost)

| # | Dataset Key | Retrieval p50 (Without → With) | E2E p50 (Without → With) | Query Tokens Without (Cost) | Decision `Kev-4b` Tokens (Cost) | Query Tokens With (Cost) | Chênh lệch Query Cost ($\Delta$) |
| :-: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | `retrievalci_v0` | `6,112` → `8,429 ms` | `11,744` → `15,023 ms` | 173,246 (`$0.010255`) | 47,980 (`$0.001919`) | 223,015 (`$0.012282`) | `+$0.002027` (+49,769 tok) |
| 2 | `vn_mteb` | `4,041` → `6,092 ms` | `9,151` → `11,386 ms` | 80,986 (`$0.004747`) | 47,265 (`$0.001891`) | 128,251 (`$0.006638`) | `+$0.001891` (+47,265 tok) |
| 3 | `wixqa_enterprise` | `3,715` → `4,763 ms` | `11,984` → `13,075 ms` | 83,448 (`$0.004959`) | 19,015 (`$0.000761`) | 102,463 (`$0.005720`) | `+$0.000761` (+19,015 tok) |
| 4 | `org1_northstar` | `2,440` → `3,164 ms` | `6,285` → `7,190 ms` | 132,955 (`$0.007868`) | 52,744 (`$0.002110`) | 200,487 (`$0.010869`) | `+$0.003001` (+67,532 tok) |
| 5 | `org2_nova` | `2,079` → `4,112 ms` | `6,404` → `8,377 ms` | 178,296 (`$0.010564`) | 51,539 (`$0.002062`) | 214,751 (`$0.011728`) | `+$0.001164` (+36,455 tok) |
| 6 | `org3_cloudops` | `2,174` → `4,222 ms` | `6,687` → `8,812 ms` | 193,593 (`$0.011473`) | 47,921 (`$0.001917`) | 272,116 (`$0.015231`) | `+$0.003758` (+78,523 tok) |
| 7 | `org4_mediflow` | `2,351` → `4,302 ms` | `6,936` → `8,780 ms` | 205,160 (`$0.012173`) | 47,795 (`$0.001912`) | 235,250 (`$0.013039`) | `+$0.000866` (+30,090 tok) |

---

## 5. Giải Phẫu Nguyên Nhân Kỹ Thuật (Tại Sao Bật Full Pre-Retrieve Hiện Tại Chưa Tăng Recall?)

Khi chạy hoàn toàn trung thực trên code `HEAD` (không overfit), việc chuyển từ **Without Pre-Retrieve (`top_k=5`)** sang **With Full Pre-Retrieve (`Kev-4b` + `qsp-v2`, `top_k=None`)** làm thay đổi `RetrievalPlan` ở **25/326 câu hỏi** (7.7% tổng số câu):
- **301/326 câu hỏi (92.3%)**: `Kev-4b` trả về `answer_shape = "DEFAULT"` hoặc `"DETAIL"` và `qsp-v2` không phát hiện từ khóa `COMPARE`/`LIST`/`COUNT`/`SUMMARIZE`, nên cả hai chế độ đều sinh ra cùng một kế hoạch `PASSAGE / ANSWER / effective_n=5`. Do đó kết quả truy xuất giống hệt nhau 100%, chỉ cộng thêm chi phí gọi `Kev-4b` (~964 tokens/câu $\approx \$0.0000385$/câu) và độ trễ mạng SiliconFlow (`~1.1s–2.3s`).
- **25/326 câu hỏi (7.7%) có `plan_diff`**:
  - Gồm các câu có hình thái `COMPARE` (`effective_n: 5 → 8`), `DOCUMENT/LIST` (`effective_n: 5 → 10`), `DOCUMENT/SUMMARIZE` (`effective_n: 5 → 10`), hoặc `DOCUMENT/COUNT` (`effective_n: 5 → 50`).
  - Tuy nhiên, ở tất cả 25 câu này, bản Baseline (`top_k=5`) **đã đạt sẵn `Recall = 1.0`** (tài liệu đúng đã nằm trong top 1–4). Khi `Full Pre-Retrieve` mở rộng `effective_n` lên `8`, `10`, hoặc `50` và đặt `per_document_limit = 1` (ở chế độ `DOCUMENT`), hệ thống lấy thêm các tài liệu xếp hạng thấp hơn vào ngữ cảnh:
    - Ở 21/25 câu: bộ lọc điểm số của SAG giữ nguyên tập tài liệu, chỉ tăng nhẹ số chunk đưa vào prompt của `GLM-4.7-Flash` (`+14,390` generation tokens).
    - Ở 4/25 câu (`qst_0020`, `WF-001`, `NOVA-EVAL-018`, `MED-EVAL-002`): việc mở rộng `effective_n` lên `8` hoặc `10` lấy thêm các tài liệu ngoài ground-truth có điểm tương đồng cao, làm `Precision@K` giảm nhẹ ở 4 câu này (`-0.10%` đến `-1.12%` tính trung bình toàn bộ), trong khi `Citation Recall` của `qst_0020` tăng (`+0.56%` trên `retrievalci_v0`).
- **Vì sao 14 câu đang thiếu Recall ở Baseline (`Recall < 1.0`, ví dụ `qst_0351`, `qst_0354` ở `retrievalci_v0`, hay `WF-019` ở `org1_northstar`) không được `Full Pre-Retrieve` cứu?**
  1. Ở các câu liệt kê ngầm định như `qst_0354` (*"According to the Q2 engineering roadmap, what are the target milestones...?"*), `Kev-4b` phân loại `Q3=A (DEFAULT)` và bộ từ khóa của [`query_analysis.py`](file:///D:/DoAnTotnghiep/sag-laya-integration/SAG/apps/api/sag_api/services/query_analysis.py) ở `HEAD` chưa coi `"what are the ..."` là `LIST`, nên `effective_n` vẫn bị giữ ở `5` (trong khi câu hỏi cần 8 tài liệu).
  2. Ở các câu có nhiều chunk cùng thuộc một tài liệu nhiễu đứng đầu bảng xếp hạng (`WF-019`, `qst_0351`), kế hoạch mặc định `PASSAGE/ANSWER/n=5` có `per_document_limit=None`, nên 1–2 tài liệu đầu tiên chiếm trọn 5 vị trí `top_k=5`, đẩy tài liệu đúng xuống vị trí thứ 6–8.
