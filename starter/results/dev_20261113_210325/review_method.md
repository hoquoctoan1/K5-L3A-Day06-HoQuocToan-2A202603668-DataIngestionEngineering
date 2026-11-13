# Ghi nhận chấm dev

- Đã điền 45 lượt (15 câu dev × A/B/C) theo yêu cầu học viên. Người hỗ trợ chấm: ChatGPT/Codex (AI), không phải nhãn do học viên tự chấm hoặc giám khảo độc lập. Học viên cần đọc lại và xác nhận trước khi nộp.
- Đọc top-3 từng lượt, đối chiếu đáp án/gold và ngữ cảnh nguồn. Hit yêu cầu một chunk riêng chứa đủ bằng chứng; không ghép nhiều chunk để thay định nghĩa chính, không dùng điểm cosine để quyết định đúng.
- Chỉ cập nhật manual_hit1, manual_hit3, manual_reason. Không đổi câu hỏi, gold, nhãn tự động, nội dung chunk, thứ hạng hoặc similarity. Không chạy hoặc chấm 5 câu test.
- Q03 B/C hạng 1 bị mất phần đầu số tiền '000.000' nên không chấm đúng; hạng 2 đủ bằng chứng. Hạng 3 tài chính trang 8 được nhận diện là nguồn tương đương về phí xét tuyển, vì câu hỏi không giới hạn bậc học và đoạn có đủ 2.000.000 đồng/lần/ứng viên vào phỏng vấn. Điều này không sửa tập gold đã chốt.
- Q01 A/B có thêm bằng chứng tương đương tại tài chính trang 10; top-1 đã đúng ở nguồn gold chính nên nhãn không phụ thuộc nguồn thay thế.
- Chấm bảo thủ với đoạn bị cắt mất chủ thể/điều kiện, như Q04 và Q15 ở hạng 1 B/C. Có thể rà soát lại các ca này bằng người học, nhưng phải ghi lý do khi đổi nhãn; không coi nhãn AI là không thể sai.
- Đây chỉ là nhãn hit truy xuất dev. Chưa chấm coherence, metadata, grounding theo thang 0–2 và chưa có điểm test.
