# Lựa chọn dữ liệu VinUni

Đã kiểm kê ngày 13/11/2026. PDF gốc được giữ nguyên.

| Tài liệu | Trang đưa vào corpus | Trang không cộng vào mức tối thiểu | Số trang được tính |
|---|---|---|---|
| Quy định duy trì học bổng đầu vào và hỗ trợ tài chính | 2, 3 | Không | 2 |
| Academic Regulations for Full-Time Undergraduate Programs | 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34 | 25, 30, 34 | 28 |
| Quy định tài chính và biểu phí | 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13 | 7 | 11 |
| Quy trình xét tốt nghiệp và cấp bằng đại học chính quy | 2, 5, 6, 7, 8 | 8 | 4 |

Tổng 67 trang vật lý; giữ 50 trang; tính bảo thủ 45 trang nội dung.

## Cách dùng

- `manifest.json` là bản kê nguồn và danh sách trang. Dùng `included_pages` để đọc corpus; `counted_pages` chỉ dùng báo cáo số trang tối thiểu.
- `page_inventory.json` có quyết định giữ/bỏ, lý do và số ký tự sau chuẩn hóa của cả 67 trang.
- Chỉ đọc 4 PDF có trong manifest; bỏ qua `format-example.json` của đề.
- Giữ nguyên số trang vật lý để dẫn nguồn. Các trang bị loại vẫn nằm trong PDF gốc.
- Năm trang ngắn vẫn cần cho ngữ cảnh: quy chế trang 25, 30, 34; tài chính trang 7; tốt nghiệp trang 8. Không loại chúng bằng ngưỡng độ dài khi đọc corpus.
- Tài liệu tốt nghiệp chỉ dùng phần tiếng Việt; bỏ trang 3-4 vì lưu đồ đã có mô tả chi tiết tại trang 5-7, và bỏ phần tiếng Anh trang 9-16 để tránh lặp.

## Giới hạn và quyền dữ liệu

- Có chữ không đồng nghĩa thứ tự đọc và bảng đã hoàn hảo. Cần đối chiếu từng evidence benchmark với PDF; lưu đồ và bảng là điểm rủi ro.
- Đây là snapshot các phiên bản đã tải, không bảo đảm là quy định mới nhất đang hiệu lực.
- Chưa xác minh giấy phép xử lý/tái phân phối; không ghi là đã có quyền. Chưa đăng PDF hoặc trích xuất đầy đủ lên GitHub và chưa gửi nội dung qua API.
- `category` là nhãn phân loại của corpus; không phải trường được trường VinUni cấp sẵn. `issued_date` không thay cho ngày hiệu lực.

## Trạng thái sau hoàn thiện

Đã có pages_clean, chunk A/B, embedding, PostgreSQL và cả benchmark dev/test. Mô tả kiểm kê phía trên là lịch sử chọn trang, không phải trạng thái chưa chạy hiện tại. Các nhãn nguồn/category và số trang giữ nguyên.

Học viên đã xác nhận quyền xử lý/chia sẻ vẫn **chưa xác minh**. Không xác nhận quyền từ việc URL là công khai; xem SUBMISSION.md và báo cáo trước khi công bố/nộp nội dung.
