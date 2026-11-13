# Submission — bài cá nhân

## Repo bài nộp

Fork repo đề bài hoặc clone rồi đẩy lên repo cá nhân. Đặt tên gợi ý `K5-L3A-DAY06-MSSV-DataIngestion` hoặc `K5-L3B-DAY06-MSSV-DataIngestion`; theo hướng dẫn lớp nếu có quy ước khác. Điền [STUDENT.md](STUDENT.md) và nộp link repo theo kênh giảng viên/coach chỉ định. Thời hạn do giảng viên/coach thông báo.

## Cấu trúc tối thiểu

```text
STUDENT.md
README.md                         # cách setup, chạy, đường dẫn dữ liệu
src/ hoặc starter/src/             # code pipeline do học viên viết
data/manifest.*                   # nguồn, trang, quyền, cách lấy
benchmark/                        # câu hỏi, split, gold evidence
artifacts/experiment_log.csv      # cấu hình và giả thuyết A/B/C
results/                          # thống kê, trace, nhãn audit, log
report/individual/<MSSV>_<HoTen>.md
```

Mẫu báo cáo: [REPORT_TEMPLATE.md](REPORT_TEMPLATE.md). `src/` có thể đặt ở root hoặc `starter/src/`; benchmark và dữ liệu thật do học viên tạo. Nếu không được phép nộp dữ liệu gốc hoặc trace chứa nội dung bị hạn chế, cung cấp hướng dẫn truy cập/tái tạo và minh chứng được phép chia sẻ; báo cho người chấm biết cách xác minh.

## Checklist hiện trạng bài VinUni

- [ ] Quyền xử lý/chia sẻ tài liệu được xác minh: **chưa xác minh, học viên đã xác nhận**. Phần số lượng có bằng chứng 45 trang nội dung, nhưng không tick trọn tiêu chí nguồn/quyền.
- [x] Có 20 câu, 15 dev/5 test chốt trước truy xuất, evidence được kiểm chứng và câu có filter.
- [x] Model thật E5 local và PostgreSQL/pgvector lưu bền vững; ghi phiên bản và cosine.
- [x] A/B/C cùng model/corpus/benchmark; B–C chỉ thay filter.
- [x] Có đầy đủ 60 trace dev/test, nhãn AI hỗ trợ có lý do, metric, số chunk, thời gian và chi phí API có phạm vi rõ.
- [x] Có coherence, metadata, grounding và phân tích 5 khía cạnh; ghi mẫu coherence chọn sau retrieval và giới hạn AI judge.
- [x] Có mã đã hiện thực trong starter/src, script, lệnh chạy, manifest, experiment log và báo cáo cá nhân.
- [ ] Bản công bố/nộp không có dữ liệu chưa được phép chia sẻ: **chưa thể xác nhận** khi quyền PDF/trích xuất vẫn chưa xác minh. .env/venv được loại khỏi Git; artifact nội dung đang giữ local.
- [ ] Commit chốt bản hoàn thiện: **học viên tự thực hiện**, commit cũ 42f64eb chưa bao gồm bản hoàn thiện này.
- [ ] Repo mở được cho người chấm và link đã nộp: **học viên sẽ tự nộp**, chưa kiểm chứng quyền truy cập hoặc bằng chứng nộp.

Xem [báo cáo](report/individual/2A202603668_HoQuocToan.md), [hướng dẫn chạy](README.md), [audit](starter/results/final_audit/README.md). Không coi các mục đã tick kỹ thuật là xác nhận toàn bộ bài đã đáp ứng điều kiện quyền dữ liệu hoặc đã nộp thành công.
