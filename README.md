# VinUni — Day06 Data Ingestion Engineering

Bài cá nhân của **Hồ Quốc Toản — 2A202603668 — L3A**. Đọc 4 PDF, chuẩn hóa 50 trang (45 trang nội dung tính bảo thủ), chia chunk A/B, embedding E5 local và tìm kiếm bằng PostgreSQL + pgvector. C dùng chung B và thêm category filter khi đầu vào có yêu cầu.

## Kết quả và tài liệu bàn giao

| Cấu hình | Dev Hit@1 | Dev Evidence Hit@3 | Test Hit@1 | Test Evidence Hit@3 |
|---|---|---|---|---|
| A | 8/15 | 11/15 | 3/5 | 3/5 |
| B | 8/15 | 11/15 | 2/5 | 4/5 |
| C | 9/15 | 12/15 | 2/5 | 4/5 |

Chọn C bằng dev trước test theo hội thoại; bản ghi lựa chọn bằng file được bổ sung sau test và ghi rõ tính hồi cứu. Nhãn do AI hỗ trợ chấm, có lý do từng lượt. Các trường hợp evidence tương đương và điểm exact khác manual được báo riêng, không thay nhãn exact.

- [Báo cáo cá nhân](report/individual/2A202603668_HoQuocToan.md)
- [Thông tin học viên](STUDENT.md), [experiment log](artifacts/experiment_log.csv), [hướng dẫn artifact](artifacts/README.md)
- [Câu hỏi/gold](benchmark/questions.json), [kế hoạch gốc](benchmark/selection_plan.json), [ghi nhận lựa chọn](benchmark/selection_outcome.json)
- [Tổng hợp định lượng](starter/results/final_audit/summary.json), [audit](starter/results/final_audit/README.md)
- [Trạng thái bài nộp](SUBMISSION.md)

## Dữ liệu và quyền

Xem [manifest](data/manifest.json) để có URL, tên file, hash và trang được chọn. Đặt 4 PDF theo đúng `source_path_or_url` trong manifest, tại `data/` ở root repo. Không dùng `format-example.json` làm corpus. Không đổi tên file hoặc hash để bỏ kiểm chứng snapshot.

**Quyền xử lý/chia sẻ bốn PDF chưa được xác minh**, học viên đã xác nhận. Hoàn thiện local không xác nhận đủ quyền công bố. PDF và artifact chứa nội dung toàn văn được giữ local và đưa vào .gitignore; chưa upload/commit/push trong đợt hoàn thiện này. Câu hỏi, trích dẫn trong benchmark/báo cáo cũng cần được xem xét về quyền khi nộp/công bố. Người chấm cần được cung cấp quyền truy cập hoặc hướng dẫn tái tạo hợp lệ; xem SUBMISSION.md.

## Setup Windows PowerShell

Cần Python 3.11 (môi trường thực nghiệm hiện có), Docker + Compose và model local. Chạy từ root repo:

```powershell
cd starter
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --timeout 120 --retries 10 -r requirements-local.txt
Copy-Item .env.example .env
docker compose -p day6_student_starter up -d --wait
.\.venv\Scripts\python.exe scripts/check_setup.py
```

Chỉ copy `.env.example` khi chưa có `.env`; giữ cấu hình local đang dùng. Không commit `.env` hoặc môi trường `.venv`. Cổng hiện tại `127.0.0.1:55433`, DB `day6_lab`; Docker volume giữ dữ liệu. Không xóa volume để xử lý lỗi setup.

Tải đúng revision model một lần nếu chưa có cache (lệnh có truy cập mạng và cần tải model):

```powershell
.\.venv\Scripts\python.exe -c "from src.embeddings import MyEmbedder; MyEmbedder(local_files_only=False)"
```

Các bước embedding/query sau đó dùng `local_files_only=True`, CPU, E5 revision `614241f622f53c4eeff9890bdc4f31cfecc418b3`, vector 384 chiều đã chuẩn hóa. Document có tiền tố `passage: `, query có `query: `.

## Chạy pipeline

Từ `starter/`, kiểm chứng artifact hiện có mà không viết lại chúng:

```powershell
.\.venv\Scripts\python.exe -m src.run
```

Tạo lại corpus/chunk/embedding và nạp database (sẽ thay artifact ingest; lưu bản cũ nếu muốn giữ thời gian lần gốc):

```powershell
.\.venv\Scripts\python.exe -m src.run --stage ingest
```

Chạy benchmark dev rồi test vào thư mục timestamp mới:

```powershell
.\.venv\Scripts\python.exe -m src.run --stage benchmark --split dev
# Chốt chiến lược trên dev trước khi chạy test.
.\.venv\Scripts\python.exe -m src.run --stage benchmark --split test
```

Không dùng kết quả test để sửa cấu hình rồi báo như holdout độc lập. File trace mới chưa có nhãn review; dùng `scripts/review_dev.py` hoặc `scripts/review_test.py --trace <đường-dẫn-traces.json>` và đọc evidence theo GUIDE. Các nhãn đang nộp chỉ thuộc hai run gốc `dev_20261113_210325` và `test_20261113_214547`.

Tra cứu một câu:

```powershell
.\.venv\Scripts\python.exe scripts/search_chunks.py --strategy C --question "Học bổng tài năng có được nâng cấp không?" --category scholarship
```

## Tổ chức mã và giới hạn

`starter/src/` hiện thực extraction/normalization, A/B chunking, local E5, PgVectorStore và exact evaluation; `src.run` nối các script đã dùng để tạo thí nghiệm. Các script thí nghiệm gốc không bị viết lại khi bổ sung src. Kiểm chứng cho thấy text/ID của toàn bộ 273 chunk A và 350 chunk B trùng dữ liệu gốc, vector thực và thứ hạng dev đã kiểm tra tương đương. Audit chạy lại dùng bảng tạm, bảng production giữ nguyên.

API embedding/LLM trả phí trong pipeline: **0 USD**; không đồng nghĩa tổng chi phí điện/mạng/máy/ChatGPT bằng 0. Test chỉ 5 câu, dev/test dùng chung nguồn và có trang chung; câu hỏi Việt với quy chế học thuật Anh. Audit do AI hỗ trợ; mẫu coherence deterministic được chốt sau truy xuất, trước khi chấm mẫu và chỉ phủ 10 trang học thuật.

Tài liệu đề bài giữ tại [GUIDE](GUIDE.md), [BENCHMARK](BENCHMARK.md), [RULES](RULES.md), [RUBRIC](RUBRIC.md), [CHECKPOINTS](CHECKPOINTS.md), [mẫu báo cáo](REPORT_TEMPLATE.md). Chatbot/HTML không bắt buộc và chưa triển khai.
