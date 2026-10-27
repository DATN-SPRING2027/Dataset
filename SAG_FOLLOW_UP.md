# Việc cần làm sau lượt kiểm chứng SAG

## Job, queue và worker

- Lượt smoke 8 file ngày 27/10/2026 tạo hai job rebuild tree; job đầu chạy khoảng 75 giây, sau đó còn job thứ hai. Cần trace lý do lập lịch và xem có thể gộp các yêu cầu rebuild mà vẫn giữ tree cập nhật hay không.
- Thiết kế trạng thái job bền vững: lease/heartbeat, phát hiện worker chết, giới hạn retry và phân biệt lỗi tạm thời với lỗi terminal. Khôi phục job sau restart phải idempotent và không khiến nhiều worker xử lý trùng.
- Có thao tác pause, cancel và dọn theo project/run, kèm xem trước phạm vi và kiểm tra các bước đang chạy. Không yêu cầu xoá toàn bộ DB chỉ để xử lý backlog.
- Đặt giới hạn concurrency và backpressure theo từng loại việc, provider và tenant; theo dõi queue depth, thời gian chờ, thời gian chạy, retry, thất bại và budget bị hoãn.
- Kiểm thử restart giữa mỗi giai đoạn, retry, worker chết, nhiều worker, dừng và chạy lại. Xác nhận tính nhất quán PostgreSQL, Qdrant, graph và tree.

## Top-K và chất lượng

- Giữ Top-K cố định 5 cho tới khi có bằng chứng đủ mạnh để thay đổi. Đo trên toàn bộ benchmark và tập thực tế, cùng dữ liệu và môi trường; theo dõi recall, precision, chất lượng câu trả lời và latency.
- Đối chứng có/không có dense cho KnowledgeUnit và graph trên cùng corpus, cấu hình, Top-K và workflow thật; kiểm tra độ chênh chất lượng, tốc độ và chi phí. Ngưỡng giảm chất lượng 1–2% cần xác định rõ metric trước khi quyết định.

## Thời gian xử lý tài liệu

- Lượt smoke 8 file mất khoảng 177 giây từ bắt đầu harness đến xong một câu hỏi; retrieval khoảng 16,35 giây và cả câu hỏi khoảng 20,05 giây. Có timeout ở Decision Router nhưng Search tiếp tục. Đây là một lần đo gồm startup, xử lý 8 file, chờ tree và query; không phải benchmark tốc độ theo từng file.
- Đo từ upload đến khi tìm kiếm thực sự khả dụng: thời gian chờ queue, parse, dedup, embedding, ghi DB/Qdrant, graph và tree. Ghi kích thước, số trang/chunk, loại file, cấu hình, hardware, provider, số worker và chi phí; phân biệt p50/p95 và throughput.
- Dùng trace để chọn nút thắt thực tế, sau đó thử batching embedding, tái sử dụng client/process, giảm round-trip và xử lý song song có giới hạn. Mỗi thay đổi phải giữ đúng chất lượng và tính nhất quán, rồi đo lại trên cùng corpus.
- Chọn các dịch vụ Big Tech và workload so sánh cụ thể, công bố cách đo và chi phí tương đương trước khi đặt mục tiêu ngang bằng; không suy ra khả năng cạnh tranh từ một file hoặc một probe nhỏ.
