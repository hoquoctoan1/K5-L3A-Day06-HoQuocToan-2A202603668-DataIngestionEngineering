# Cấu hình và minh chứng

- `experiment_log.csv`: A/B/C, model thật và tỷ lệ Hit@1/Hit@3 dev/test từ nhãn AI hỗ trợ đã lưu. Cột số là tỷ lệ 0–1; n/N ghi trong notes và báo cáo. Dùng nhãn manual; giữ điểm exact riêng trong summary.
- `coherence_sample_plan.json`: cùng 10 vị trí nguồn cho cả ba chiến lược, được cố định trước khi đọc/chấm mẫu coherence nhưng sau truy xuất dev/test. Cùng chunk B/C; không coi là hai lần chấm độc lập.
- `../starter/results/final_audit/`: toàn bộ nhãn coherence, metadata, grounding, tổng hợp, môi trường và kiểm chứng runtime.
- Hai run gốc: `dev_20261113_210325` và `test_20261113_214547`. Không chuyển nhãn sang run khác khi chưa đối chiếu text/ID.

Điểm API pipeline local là 0 USD; tổng chi phí vận hành chưa được đo. Các artifact chứa nội dung PDF chưa có xác minh quyền chia sẻ nên giữ local. Không coi checklist kỹ thuật là xác nhận quyền hoặc đã nộp.
