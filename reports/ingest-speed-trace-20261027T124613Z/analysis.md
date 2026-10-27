# Phân tích trace tốc độ ingest một file

File Markdown 34.236 byte, project mới, dense graph bật. Bốn lượt với cùng file đạt 30,894–33,294 giây từ lúc bắt đầu upload đến lần đầu quan sát tree `ACTIVE`. Trace chi tiết dưới đây là lượt 33,176 giây. Các mốc được lấy bằng đồng hồ đơn điệu; trạng thái được kiểm tra mỗi 0,5 giây.

> Phạm vi dữ liệu thực tế của các lượt lịch sử là schema `sag` của môi trường dev, còn registry nằm ở schema benchmark. Xem [đính chính phạm vi](../ingest-scope-correction-20261027.md).

## Dòng thời gian

| Mốc từ upload | Việc đang chạy | Thời gian đo |
|---|---|---:|
| 0,00–0,09 s | Upload service | 0,09 s |
| 0,25–2,58 s | Dedup và temporal | 2,33 s |
| 2,77–14,19 s | Index SearchUnit | 11,42 s |
| 3,38–11,25 s | Embedding 285 văn bản, nằm trong bước index | 7,87 s |
| 11,26–12,74 s | Đảm bảo collection/index Qdrant, nằm trong bước index | 1,48 s |
| 14,31 s | Quan sát được trạng thái `SEARCH_READY` | — |
| 15,26–17,25 s | Tạo KnowledgeUnit Foundation | 1,99 s |
| 17,30–33,07 s | Dựng và publish tree | 15,77 s |
| 33,18 s | Quan sát được tree `ACTIVE` | — |

`SEARCH_READY` là trạng thái nội bộ. Lượt này không chạy truy vấn để xác minh rằng người dùng có thể retrieval đúng ở mốc 14,31 giây.

## Bên trong 15,77 giây dựng tree

| Bước | Thời gian |
|---|---:|
| Dựng snapshot | 8,27 s |
| Trong snapshot: tính và lưu graph | 3,40 s |
| Trong 3,40 s graph: CPU graph | 3,00 s |
| Trong snapshot: dựng routing | 3,98 s |
| Publish tree | 7,47 s |
| Trong publish: chuẩn bị candidate bằng CPU | 1,97 s |
| Trong publish: ghi trạng thái candidate ở DB | 1,14 s |
| Trong publish: ghi payload Qdrant | 2,39 s |
| Trong publish: xóa slot, kiểm tra và chuyển active | khoảng 1,96 s |

Các dòng có chữ “trong” nằm bên trong dòng cha và **không được cộng lại**. Trace trước đã vô tình cộng graph CPU và graph persistence: 3,00 giây CPU đã nằm trong 3,40 giây persistence; cả hai nằm trong 15,77 giây tree.

Routing CPU 3,98 giây gồm khoảng 0,92 giây nạp module trong tiến trình con, 2,62 giây tính toán và phần còn lại là khởi động/điều phối/trao đổi dữ liệu. Trong phần tính toán, 49 lần tạo profile chiếm 1,63 giây; 9 lần chia cụm chiếm 0,29 giây. Các phép cosine/medoid là một phần của profile; trace này không tách riêng thời gian của chúng.

## Chỗ có thể rút ngắn

1. **Dedup trên project mới:** project này có 0 block cũ, nhưng `dedup_candidates` vẫn khởi tạo tiến trình: 1,01 giây tổng, trong đó tính toán chỉ khoảng 0,001 giây và nạp module 0,66 giây. Có thể xét bỏ riêng bước so sánh khi không có block cũ, vẫn tính/lưu signature cho các lần ingest sau. Đây là số đo cho trường hợp rỗng; cần kiểm tra tương đương đầu ra trước khi áp dụng.
2. **Khởi tạo Qdrant lặp:** preflight tạo collection/index mất 2,33 giây trước upload, sau đó bước index gọi lại helper và mất 1,48 giây. Cần xét cache trạng thái sẵn sàng theo collection và xử lý mất collection/index hoặc nhiều worker; không coi 1,48 giây là mức tiết kiệm đã được chứng minh. Preflight là biện pháp đo để tránh race index từng gây HTTP 400; thời gian preflight được tính trong tổng setup → ACTIVE là 35,508 giây.
3. **Tiến trình CPU:** mỗi phép `minhash`, `dedup_candidates`, `graph`, `routing`, `prepare_tree` dùng tiến trình mới. Các lượt nạp module đo được khoảng 0,61–0,92 giây; riêng `prepare_tree` mất khoảng 1,34 giây từ lúc gọi đến khi vào hàm con, bao gồm khởi tạo và giải tuần tự dữ liệu. Worker tái sử dụng có thể giảm chi phí này, với điều kiện vẫn giữ timeout, hủy việc và giới hạn đồng thời.
4. **Routing profile:** 1,63 giây nằm trong 49 lần tạo profile. Có thể tối ưu phép tính mà giữ kết quả và thứ tự xác định; cần đo lại output và thời gian, vì thời gian cosine/medoid chưa được tách riêng.
5. **Embedding:** batch 285 văn bản gồm 11 SearchUnit và 274 block được tính trước cho KnowledgeUnit, mất 7,87 giây. KnowledgeUnit tái sử dụng cache nên bước embedding sau chỉ mất 0,01 giây. Giảm số block dense hoặc đổi model có thể ảnh hưởng graph, routing và retrieval; phải đo riêng chất lượng và thời gian, không thể suy ra mức tiết kiệm chỉ từ tổng batch.
6. **Publish Qdrant:** ghi payload mất 2,39 giây; mã hiện gửi các batch tuần tự và đợi hoàn tất. Có thể khảo sát gom hoặc giới hạn song song, giữ nguyên xác nhận ghi, kiểm tra ACL và chuyển slot an toàn.

Lượt này không thay đổi logic sản phẩm, không chạy retrieval hay đánh giá chất lượng. Các mức tiết kiệm là cơ hội từ trace, chưa phải kết quả sau tối ưu.
