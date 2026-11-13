# Bộ câu hỏi VinUni

20 câu theo snapshot tài liệu đã tải: 15 dev và 5 test. Mỗi nhóm có tổng cộng 5 câu. Đây không phải tư vấn chính sách hiện hành.

| Nhóm | Dev | Test | Tổng |
|---|---:|---:|---:|
| Học thuật | 4 | 1 | 5 |
| Tài chính | 4 | 1 | 5 |
| Học bổng | 4 | 1 | 5 |
| Tốt nghiệp | 3 | 2 | 5 |

## Các file

- `questions.json`: câu hỏi, đáp án, trang gold, evidence và filter. Khi truy xuất chỉ dùng `question` và `filter`; không dùng đáp án hoặc nguồn gold.
- `selection_plan.json`: mã kiểm chứng bộ câu hỏi/corpus, cách chia và tiêu chí chọn cấu hình trước khi xem kết quả test.
- 4 câu dev có filter: Q01, Q03, Q04, Q06; 1 câu test có filter: Q18. Filter là lựa chọn phạm vi giả định được cung cấp trước, không được suy ra từ đáp án.

## Chạy kiểm tra

Chạy từ thư mục `starter`:

```powershell
.\.venv\Scripts\python.exe scripts/check_benchmark.py --verify-pdf
```

Xem riêng 15 câu dev (không in đáp án):

```powershell
.\.venv\Scripts\python.exe scripts/check_benchmark.py --split dev --list
```

Các lệnh này chỉ kiểm tra định dạng, snapshot và bằng chứng. Không chạy model, không kết nối database và không tạo điểm Hit@1/Hit@3.
Đã có embedding, PostgreSQL và hai run dev/test, kèm nhãn. Entry point hiện tại là `python -m src.run` (default kiểm chứng artifact); xem README root để chạy ingest/benchmark. selection_plan.json là snapshot kế hoạch gốc; phần limitations mô tả trạng thái thời điểm chuẩn bị, không thay thế kết quả đã chạy trong final_audit/summary.json.

## Quy trình thí nghiệm

1. Chọn/điều chỉnh cấu hình bằng dev; ưu tiên Evidence Hit@3, rồi Hit@1, rồi số chunk ít hơn; nếu vẫn bằng nhau dùng thứ tự A/B/C.
2. Chốt cấu hình trước khi chạy test; không sửa cấu hình theo kết quả test và vẫn báo kết quả A/B/C một cách trung thực.
3. Chấm thủ công coherence, metadata và grounding theo GUIDE. Kiểm chứng evidence không đồng nghĩa hệ thống đã tìm đúng.
4. Nếu sửa corpus hoặc câu hỏi, xác minh lại evidence và tạo phiên bản selection plan mới; không tự bỏ kiểm tra hash để hợp thức hóa thay đổi sau khi xem test.

## Giới hạn

Dev/test cùng dùng bốn tài liệu; một số trang xuất hiện ở cả hai tập. Chia này cân bằng chủ đề nhưng không loại bỏ rò rỉ nội dung. Bộ test chỉ có 5 câu.
Câu hỏi do AI hỗ trợ soạn và đã đối chiếu evidence với PDF gốc. Người học cần đọc lại đáp án và ghi việc dùng AI trong báo cáo.
Khoảng trắng và xuống dòng được chuẩn hóa khi so evidence. Giữ nguyên lỗi tách chữ của nguồn; không giả vờ đó là thông tin khác.

## Danh sách câu hỏi

| ID | Tập | Nhóm | Trang PDF | Filter | Câu hỏi |
|---|---|---|---:|---|---|
| Q01 | dev | Học bổng | 2 | Có | Theo quy định duy trì học bổng đầu vào, học bổng tài năng có được nâng cấp mức trong quá trình học không? |
| Q02 | dev | Học thuật | 7 | Không | Theo quy chế đào tạo, một tín chỉ tương đương tổng cộng bao nhiêu giờ học, tính cả các hoạt động học tập chứ không chỉ giờ lên lớp? |
| Q03 | dev | Tài chính | 2 | Có | Ứng viên đã vào vòng phỏng vấn và không thuộc diện miễn phí phải nộp bao nhiêu tiền phí xét tuyển hồ sơ cho mỗi lần? |
| Q04 | dev | Tốt nghiệp | 5 | Có | Sau khi kế hoạch xét tốt nghiệp được thông qua, sinh viên được thông báo qua những kênh nào? |
| Q05 | dev | Học bổng | 2 | Không | Đối với học bổng tài năng toàn phần hoặc 100%, ngưỡng điểm trung bình theo năm học được nêu trong điều kiện duy trì là bao nhiêu? |
| Q06 | dev | Học thuật | 11 | Có | Để được phân loại là sinh viên toàn thời gian trong học kỳ chính, sinh viên phải đăng ký ít nhất bao nhiêu phần trăm tải học chuẩn và tương đương bao nhiêu tín chỉ? |
| Q07 | dev | Tài chính | 3 | Không | Nếu trả muộn tài liệu thư viện dành riêng cho khóa học, phí quá hạn được tính theo giờ hay ngày và mức phí là bao nhiêu? |
| Q08 | dev | Tốt nghiệp | 6 | Không | Sinh viên có tên trong danh sách xét tốt nghiệp nhưng chưa làm học phần tốt nghiệp hoặc chưa tích lũy đủ điều kiện có phải đăng ký hoãn xét tốt nghiệp không? |
| Q09 | dev | Học bổng | 3 | Không | Với học bổng tài năng các mức 50%, 60%, 70%, 80% hoặc 90%, ngưỡng điểm trung bình năm học trong điều kiện duy trì là bao nhiêu? |
| Q10 | dev | Học thuật | 12 | Không | Trong học kỳ hè, sinh viên được học tối đa bao nhiêu tín chỉ và có mức tín chỉ tối thiểu bắt buộc không? |
| Q11 | dev | Tài chính | 4 | Không | Làm lại thẻ sinh viên phải đóng bao nhiêu tiền và khoản phí được thu lúc nào? |
| Q12 | dev | Tốt nghiệp | 8 | Không | Theo mục hiệu lực thi hành, quy trình xét tốt nghiệp và cấp bằng đại học này có hiệu lực từ ngày nào? |
| Q13 | dev | Học bổng | 3 | Không | Học bổng liên thông Vinschool–VinUni mức 5% có phải đáp ứng yêu cầu gia hạn riêng được nêu trong bảng không? |
| Q14 | dev | Học thuật | 31 | Không | Trong các điều kiện xét cấp bằng, điểm trung bình tích lũy tối thiểu của các học phần thuộc chương trình phải đạt bao nhiêu trên thang 4? |
| Q15 | dev | Tài chính | 11 | Không | Sinh viên xin bảo lưu hoặc thôi học phải nộp đơn trước ngày thôi học chính thức ít nhất bao nhiêu ngày? |
| Q16 | test | Học bổng | 3 | Không | Theo dòng Hỗ trợ Tài chính từ 50%, sinh viên phải đáp ứng điều kiện điểm và hoạt động E.X.C.E.L nào để duy trì hỗ trợ? |
| Q17 | test | Học thuật | 10 | Không | Nếu nhập học khi chưa xác định ngành chính, sinh viên phải khai báo ngành chính chậm nhất vào thời điểm nào? |
| Q18 | test | Tài chính | 11 | Có | Theo mục hoàn trả học phí khi chủ động thôi học, nếu thôi học sau hai tuần kể từ ngày đầu của học kỳ thì học phí thực nộp của học kỳ đó có được hoàn lại không? |
| Q19 | test | Tốt nghiệp | 2 | Không | Về đối tượng sinh viên, quy trình xét tốt nghiệp này áp dụng cho bậc và hình thức đào tạo nào, và sinh viên phải đạt tình trạng gì? |
| Q20 | test | Tốt nghiệp | 7 | Không | Khi có nhu cầu nhận giấy chứng nhận tốt nghiệp tạm thời, sinh viên phải đăng ký với đơn vị nào và thời hạn cấp theo bảng là bao lâu kể từ quyết định công nhận tốt nghiệp và cấp bằng? |


## Kết quả đã lưu

Xem `../starter/results/final_audit/summary.json` và báo cáo cá nhân. Nhãn AI hỗ trợ chấm, không phải người chấm độc lập. Giữ nguyên questions.json và selection_plan.json đã chốt; selection_outcome.json ghi hồi cứu lựa chọn C sau khi đã có test, nêu rõ quyết định trước test dựa vào hội thoại.
