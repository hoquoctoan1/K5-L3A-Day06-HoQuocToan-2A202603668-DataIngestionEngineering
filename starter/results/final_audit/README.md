# Audit bổ sung của bài VinUni

- `summary.json`: số tử/mẫu retrieval dev/test, latency thực từ trace, coherence/metadata/grounding và chi phí API có giới hạn rõ.
- `coherence.json`: 30 nhãn (10 vị trí × A/B/C), text được chấm và lý do. C dùng cùng B. Kế hoạch tại `../../../artifacts/coherence_sample_plan.json`; chọn sau khi đã thấy test, trước khi chấm coherence. Mẫu chỉ gồm PDF học thuật Anh, không suy rộng sang toàn corpus.
- `metadata.json`: 45 bản ghi top-3 test với nguồn/trang/category/language đã đối chiếu. A/B cũng ra đúng financial ở Q18 nhưng không áp dụng filter; C mới thực sự cưỡng chế filter SQL.
- `grounding.json`: 15 nhãn nội dung top-3, thang 0–2, có lý do riêng; không phải điểm câu trả lời sinh bởi LLM.
- `environment.json`: version thư viện hiện có.
- `runtime_validation.json`: kiểm chứng module src trùng dữ liệu gốc, vector thật, thứ hạng dev và nạp lặp/stale chunks trong bảng tạm. Bảng rag_chunks production giữ nguyên.
- `ingest_measurement.json`: đo lại toàn quá trình từ extraction đến lưu vector trong bảng tạm, dùng model thật; một lần chạy, cache/file ấm. Không thay thời gian embedding/thí nghiệm gốc bằng thời gian mới.

Người hỗ trợ chấm: ChatGPT/Codex (AI), cũng đã hỗ trợ soạn câu hỏi nên có nguy cơ thiên lệch và sai sót tương quan. Chưa có xác nhận của giám khảo độc lập. Hit nhị phân được giữ trong run gốc, không tự suy từ cosine. Q19/A và Q20/B,C chấp nhận evidence tương đương, được giải thích trong review_method.md của test.

## Kiểm chứng lại

Từ starter, chạy `python scripts/summarize_results.py` để tổng hợp nhãn, `python scripts/audit_runtime.py` để thử nạp lặp/stale trong bảng tạm, hoặc `python scripts/measure_ingest.py` để đo ingest mới bằng model thật. Hai lệnh sau cần PostgreSQL đang chạy và model cache, tạo file recheck có timestamp để không thay số đo đã lưu.
