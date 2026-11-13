# Chạy pipeline VinUni Day06

Đây là bản đã hiện thực của starter PostgreSQL + pgvector. Hướng dẫn setup, dữ liệu, chạy ingest/dev/test và giới hạn nằm tại [README root](../README.md).

Chạy từ thư mục này:

```powershell
.\.venv\Scripts\python.exe -m src.run
```

Mặc định chỉ kiểm chứng artifact hiện có. `--stage ingest` chạy lại đọc/chuẩn hóa/chunk/embedding/nạp vector; `--stage benchmark --split dev` hoặc `test` chạy truy xuất vào run mới. Không mặc định chạy lại test khi kiểm tra môi trường.

- `src/`: các hàm/thành phần Python đã triển khai và entry point.
- `scripts/`: các script từng bước đã tạo kết quả thí nghiệm, script kiểm tra artifact.
- `results/`: hai run dev/test gốc, nhãn và audit bổ sung.
- `requirements-local.txt`: thư viện local theo môi trường đã kiểm chứng.
- `docker-compose.yml`, `init.sql`, `.env.example`: PostgreSQL/pgvector local.

Corpus thật nằm ở `../data/`, theo `../data/manifest.json`. `starter/data/` không phải nguồn thí nghiệm này. `.env`, PDF và artifact nội dung giữ local; quyền dữ liệu chưa được xác minh. Không ghi kết quả của run mới đè lên nhãn của run cũ.
