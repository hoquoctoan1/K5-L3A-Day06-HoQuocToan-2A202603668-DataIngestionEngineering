# Báo cáo cá nhân — Day06 Data Ingestion Engineering

- Học viên: **Hồ Quốc Toản — 2A202603668 — L3A** (đã được học viên xác nhận).
- Chủ đề: tra cứu quy định học tập và chính sách sinh viên VinUni.
- Repo: https://github.com/hoquoctoan1/K5-L3A-Day06-2A202603668-DataIngestionEngineering
- Đã có pipeline thực, 3 cấu hình, 20 câu hỏi, 60 lượt dev/test và audit 5 khía cạnh. Quyền dữ liệu chưa xác minh; chưa chốt commit và học viên tự nộp.
- Chỉ dùng số liệu có artifact hoặc phép chạy kiểm chứng thực tế. Nhãn là AI hỗ trợ đánh giá, có lý do; chưa có người chấm độc lập xác nhận.

## 1. Dữ liệu, quyền và pipeline

Snapshot 4 PDF nguồn chính thức policy.vinuni.edu.vn, 67 trang vật lý. Giữ 50 trang, tính bảo thủ 45 trang nội dung. Không khẳng định snapshot là chính sách mới nhất đang hiệu lực.

| Source ID / nhóm | Trang vật lý | Trang nạp | Trang tính nội dung |
|---|---:|---|---:|
| vinuni_scholarship / scholarship | 3 | 2–3 | 2 |
| vinuni_academic / academic | 34 | 4–34 | 28 |
| vinuni_financial / financial | 14 | 2–13 | 11 |
| vinuni_graduation / graduation | 16 | 2,5,6,7,8 | 4 |

Manifest ghi tên, URL, hash, version/ngày biết được, nguồn metadata và số ký tự; dùng trang vật lý từ 1. Loại bìa/lịch sử sửa đổi/mục lục, trang rỗng/chỉ số, bản dịch lặp. Lưu đồ tốt nghiệp 3–4 bị loại vì mất quan hệ khi trích chữ; dùng mô tả 5–7. Năm trang ngắn giữ bổ sung nhưng không tính vào tối thiểu: học thuật 25,30,34; tài chính 7; tốt nghiệp 8. Không nhân bản dữ liệu.

**Quyền xử lý/tái phân phối: chưa xác minh, theo xác nhận học viên.** Không ghi Public là giấy phép mở. Chưa có giấy phép/văn bản cho phép được cung cấp; các PDF/trace chứa nội dung giữ local và chưa được đưa lên GitHub trong đợt hoàn thiện này. Thông tin này là điều kiện còn thiếu trước khi khẳng định bài nộp đáp ứng đầy đủ yêu cầu quyền dữ liệu.

pypdf đọc text, Unicode NFC, CRLF/CR về LF, NBSP/dấu cách ngang/dòng trống được chuẩn hóa; chỉ bỏ dòng đầu nếu trùng đúng số trang. Giữ nguồn/trang/category/language. Chưa OCR, tái dựng bảng hoặc sửa hết từ bị tách/header nhiều thành phần. 50 trang sạch có 113.729 ký tự, không rỗng. B từng có 24 chunk chỉ số trang (374 chunk); sửa header còn 350, không còn chunk chỉ số. A có 273. Xem [cleanup audit](../../starter/results/cleanup_audit.json), [manifest](../../data/manifest.json), [chọn trang](../../data/DATA_SELECTION.md).

## 2. Model, store, metadata và cách chạy

Embedding: intfloat/multilingual-e5-small, revision **614241f622f53c4eeff9890bdc4f31cfecc418b3**, SentenceTransformers local CPU, vector **384** chiều, normalize_embeddings=True. Document thêm `passage: `, query thêm `query: `. Kiểm tra token để không âm thầm truncate. Dùng chung model/revision/corpus cho A/B/C.

Version quan sát: SentenceTransformers 6.3.0, torch 2.11.0+cpu, transformers 5.22.2, pypdf 6.21.4, psycopg 3.3.8. PostgreSQL **16.16**, pgvector **0.8.7**, Docker image `pgvector/pgvector:0.8.7-pg16`, cổng 127.0.0.1:55433, DB day6_lab. Bảng rag_chunks lưu bền vững trong Docker volume; PK(strategy,chunk_id); exact cosine `<=>`, không HNSW/IVFFlat. A=273, B=350 dòng/ID phân biệt; C dùng B.

Metadata bắt buộc: document_id từ source_id manifest, source đường dẫn PDF, page vật lý. category do người chuẩn bị phân loại theo loại tài liệu (academic/financial/scholarship/graduation); language vi/en theo phần được chọn. C dùng category trong WHERE SQL trước ORDER BY/LIMIT 3. Giá trị filter là input giả định đã cung cấp trước, không lấy từ gold. Version/ngày nguồn chưa được đưa vào filter; không đoán hiệu lực tài liệu.

Upsert giao dịch theo stable ID rồi xóa ID cũ không còn trong snapshot cùng chiến lược; từ chối rỗng/ID trùng/sai chiều/model. Kiểm chứng mới trong bảng tạm: nạp A/B hai lần không tăng số dòng; giảm A 273→272 rồi nạp lại 273 loại đúng ID thừa; sau kiểm tra bảng production có cùng fingerprint. Đây là phép kiểm tra cập nhật snapshot, không khẳng định đã thử mọi loại sửa tài liệu.

Mã chính tại [starter/src](../../starter/src), entry point `python -m src.run`; các script từng bước tại [starter/scripts](../../starter/scripts). Hàm src mới đã đối chiếu đúng toàn bộ text/ID chunk gốc, normalization 50 trang, vector thực và 6 truy xuất dev Q01/Q06. Không tinh chỉnh retrieval bằng test.

Setup và tải model/PDF theo [README](../../README.md). Từ starter:

```powershell
.\.venv\Scripts\python.exe -m src.run
.\.venv\Scripts\python.exe -m src.run --stage ingest
.\.venv\Scripts\python.exe -m src.run --stage benchmark --split dev
# Chọn cấu hình bằng dev, sau đó mới chạy test.
.\.venv\Scripts\python.exe -m src.run --stage benchmark --split test
```

Default chỉ kiểm chứng artifact, không rerun test. Ingest ghi lại artifact/thời gian mới; benchmark tạo run mới. Các nhãn hiện báo cáo gắn đúng run gốc. Không commit .env/key/venv.

## 3. Ba cấu hình và bộ benchmark

| Cấu hình | Chunking | Overlap | Truy xuất |
|---|---|---|---|
| A | fixed-size tối đa 500 ký tự, theo từng trang | 50 ký tự | exact cosine, không filter |
| B | nhóm đoạn theo dòng trống, tối đa 500; đoạn dài ưu tiên dấu kết câu rồi khoảng trắng, cuối cùng cắt cứng | 50 ký tự khi chia nhóm dài, không overlap giữa mọi nhóm | exact cosine, không filter |
| C | giữ nguyên toàn bộ B | như B | thêm category nếu câu hỏi có filter; không có thì như B |

A–B chỉ thay cách chunking; B–C chỉ thay filter. 500 là ký tự, không phải từ/token. B vẫn có thể bắt đầu giữa từ do overlap hoặc tạo heading riêng.

20 câu trong [questions.json](../../benchmark/questions.json), chốt 15 dev Q01–15 / 5 test Q16–20. Mỗi chủ đề có 5 câu; dev học bổng/học thuật/tài chính/tốt nghiệp = 4/4/4/3, test = 1/1/1/2. Filter dev Q01,Q03,Q04,Q06; test Q18. 20 evidence đều xác minh với PDF và pages_clean sau NFC/gộp khoảng trắng. Không đưa đáp án/source gold vào vector query/filter.

Theo [selection_plan.json](../../benchmark/selection_plan.json) v1.0, ưu tiên dev Evidence Hit@3 → Hit@1 → ít chunk → A/B/C. C được chọn trên dev trước khi chạy test trong hội thoại. [selection_outcome.json](../../benchmark/selection_outcome.json) được bổ sung hồi cứu sau test, không phải bằng chứng timestamp trước test. Không sửa câu hỏi/corpus/vector/thứ hạng/nhãn hit trong đợt hoàn thiện.

## 4. Kết quả retrieval và tài nguyên

Hit yêu cầu một chunk có đủ evidence hoặc tương đương được chấm rõ; không ghép nhiều chunk để tính Hit@3. Similarity không phải xác suất đúng.

| Cấu hình | Split | Manual Hit@1 | Manual Evidence Hit@3 | Exact Hit@1 / Hit@3 | Chunk/vector | SQL tổng / trung bình (giây) |
|---|---|---|---|---|---:|---|
| A | dev | 8/15 | 11/15 | 8/15 / 11/15 | 273 | 0.118340 / 0.007889 |
| A | test | 3/5 | 3/5 | 2/5 / 2/5 | 273 | 0.086608 / 0.017322 |
| B | dev | 8/15 | 11/15 | 8/15 / 11/15 | 350 | 0.096906 / 0.006460 |
| B | test | 2/5 | 4/5 | 2/5 / 3/5 | 350 | 0.033832 / 0.006766 |
| C | dev | 9/15 | 12/15 | 9/15 / 12/15 | 350 | 0.099251 / 0.006617 |
| C | test | 2/5 | 4/5 | 2/5 / 3/5 | 350 | 0.028440 / 0.005688 |

Manual khác exact ở Q19/A (chỉ cắt đuôi từ “nghiệp”, giữ đủ bậc/hình thức/điều kiện trong cùng chunk) và Q20/B,C (riêng hạng 2 giữ loại giấy tạm thời, P.QLĐT, 07 ngày sau QĐ; chỉ thiếu chữ g đầu). Không chấp nhận hạng 1 Q20/B,C vì thời hạn phía trên thuộc hàng 12, trong khi câu hỏi cần hàng 13. Nhãn exact giữ nguyên false và lý do tương đương công bố trong [test review method](../../starter/results/test_20261113_214547/review_method.md). Không khẳng định nhãn AI không thể sai.

Thời gian SQL lấy trực tiếp từ retrieval_seconds trong trace, chỉ đo truy vấn/fetch. Query được encode một lần/câu rồi dùng cả A/B/C; không cộng ba lần khi tính tổng. Tổng query encode dev 0.985535s, test 0.225724s; không bao gồm tải model. Một lượt đo/mẫu nhỏ, chưa có độ lệch chuẩn latency.

| Cấu hình | Min / max ký tự | Mean / median | Tổng ký tự chunk có overlap | Encode-only gốc (giây) |
|---|---|---|---:|---:|
| A | 78 / 500 | 457,43 / 500 | 124.879 | 15.760165 |
| B | 17 / 500 | 355,02 / 398 | 124.257 | 18.407498 |
| C | dùng B | dùng B | dùng B | không encode riêng |

Thời gian gốc đo quanh model.encode, chưa bao gồm đọc/ghi, kiểm tra token, tải model hoặc nạp DB. Đã có phép đo lại riêng bằng pipeline src và model thật trong bảng tạm; không thay thế số gốc:

| Đo lại | Chunking (s) | Encode kiểm tra token + encode (s) | Upsert bảng tạm (s) | Tổng passage token có prefix |
|---|---:|---:|---:|---:|
| A | 0.001776 | 25.749322 | 0.413874 | 30674 |
| B | 0.007275 | 19.261539 | 0.298598 | 30972 |

Đọc + chuẩn hóa dùng chung: 7.832190s; mở model: 33.845741s; wall tổng đo lại A+B: 88.608537s (có cả kiểm chứng/tokenization phụ trợ). Một lần chạy, file/model cache ấm; không bao gồm tải ban đầu, cài thư viện hay khởi động Docker. Chi tiết [ingest measurement](../../starter/results/final_audit/ingest_measurement.json). Không có log full-ingest lần gốc nên không gán số đo lại thành thời gian gốc.

**Chi phí API embedding/LLM của pipeline: 0 USD**, vì CPU local và PostgreSQL local, không gọi API trả phí. Điện, mạng, phần cứng, công sức và tài khoản ChatGPT chưa được tổng hợp; tổng chi phí vận hành không có số xác minh. Model tải lần đầu không nằm trong thời gian/chi phí API trên.

## 5. Coherence, metadata và grounding

| Cấu hình | Coherence /2 (n) | Metadata đúng/đủ | Test Q18: top-3 đúng phạm vi | Grounding 0/1/2 (số câu), mean /2 |
|---|---|---|---|---|
| A | 1,0 (10) | 15/15 | 1/1 quan sát; không filter | 2/0/3; 1,2 |
| B | 1,2 (10) | 15/15 | 1/1 quan sát; không filter | 1/0/4; 1,6 |
| C | 1,2 (10) | 15/15 | 1/1; có cưỡng chế filter | 1/0/4; 1,6 |

Coherence: 10 trang đầu khi sắp (document_id, page số), anchor ở floor(len(text)/2), chọn chunk bao phủ với start lớn nhất (tie theo ID), cùng vị trí cho A/B/C; C dùng đúng B. Plan được lưu trước đọc/chấm mẫu, nhưng sau khi đã xem retrieval test. Vì 10 vị trí đều ở học thuật Anh, không suy rộng sang toàn corpus. 30 nhãn có text/lý do; A thường cắt đầu/cuối, B giữ trọn hơn ở S03/S08 nhưng vẫn có nhiều fragment. Không coi B/C là hai mẫu độc lập.

Metadata: đọc 45 bản ghi test; đối chiếu source/path/page với PDF, ID/text với chunk, category/language với manifest và loại tài liệu. Tất cả 15/15 mỗi chiến lược đúng/đủ, không có nghĩa retrieval đều đúng. category giúp Q06 dev lấy đúng academic: C hit trong khi A/B miss. Test chỉ Q18 yêu cầu financial; A/B tình cờ cũng trả financial, chỉ C thực thi WHERE category. Metadata hiện chưa lọc version/audience hoặc hiệu lực chính sách, nhãn category không chứng minh quyền tài liệu.

Grounding: đọc nội dung top-3 với cùng thang 0/1/2; đủ evidence và source/page được 2, thiếu điều kiện/ngữ cảnh được 1, không có evidence đúng đối tượng được 0. Q16/A=0 vì chỉ có học bổng tài năng, Q17 cả ba=0; Q16/B,C và Q18–20 đủ nền nên 2. Các lý do được ghi riêng, không tự sao từ Hit@3, không chấm câu trả lời LLM chưa sinh.

## 6. Phân tích, ví dụ lỗi và lựa chọn

1. **Dev Q06**: A/B top-3 là tài chính, C lọc academic lấy hạng 1 `B:vinuni_academic:p11:c5`, trang 11, đủ 80%=12 tín chỉ. Dev C Hit@3 tăng đúng 1/15 so với B. Các câu không filter C giống B.
2. **Test Q16/A**: `A:vinuni_scholarship:p2:s900` trả học bổng toàn phần 3,2, sai đối tượng Hỗ trợ Tài chính từ 50% cần 2,0. Hạng 3 A là học bổng 50–90% cần 2,5, vẫn sai. B/C hạng 3 `B:vinuni_scholarship:p3:c4`, trang 3, giữ trọn đúng dòng nên hit. Đây là khác biệt do chunking, không phải filter.
3. **Test Q17 cả ba miss**: gold học thuật trang 10 nhưng trả học phí/học lại/hoãn tốt nghiệp. Có bằng chứng trong corpus nhưng semantic search không xếp vào top-3. Yếu tố hỏi Việt/tài liệu Anh có thể liên quan, chưa có thí nghiệm riêng chứng minh nguyên nhân.
4. **Test Q20/B,C top-1**: `B:vinuni_graduation:p7:c2` chứa mô tả giấy tạm thời nhưng thiếu đơn vị/thời hạn của hàng 13; mốc 07 ngày hiện có thuộc hàng 12. Không lấy nhầm mốc. Riêng hạng 2 đủ evidence tương đương nên Hit@3=1. Dù B kết thúc ưu tiên câu, bảng vẫn có thể bị cắt qua hàng/cột.

A ít hơn B 77 chunk, encode-only gốc thấp hơn trong một lần đo. Dev A/B Hit@1 và Hit@3 bằng nhau; test A top-1 cao hơn B/C nhưng Hit@3 thấp hơn. Không tuyên bố B tốt hơn ở mọi mục tiêu. B/C dùng chung 350 vector, C không thêm chi phí embedding, chỉ thêm điều kiện SQL. Test B=C vì chỉ có Q18 filter và B đã trả financial. Không suy ra filter luôn cải thiện hoặc luôn vô ích.

**Giữ lựa chọn C theo dev**, ưu tiên Evidence Hit@3 đã chốt; không đổi theo test. Mẫu test 5 câu nên một câu tương đương 20 điểm phần trăm. Corpus/dev/test cùng nguồn và có trang chung; không phải kiểm tra tổng quát độc lập theo tài liệu. Một số nhãn cận biên và câu hỏi đều có AI hỗ trợ, tăng nguy cơ thiên lệch.

Nếu mở rộng: gộp heading với nội dung, giữ hàng bảng, xử lý từ bị tách có kiểm chứng, thử hybrid hoặc rerank trên dev và dùng một bộ test mới trước khi kết luận. Những cải tiến này chưa thực hiện; không gán số liệu giả định thành kết quả. Chatbot/HTML không thuộc yêu cầu bắt buộc.

## 7. Minh chứng, AI và phần còn chờ

- Trace/nhãn dev: [traces](../../starter/results/dev_20261113_210325/traces.json), [review](../../starter/results/dev_20261113_210325/dev_review.json), [phương pháp](../../starter/results/dev_20261113_210325/review_method.md).
- Trace/nhãn test: [traces](../../starter/results/test_20261113_214547/traces.json), [review](../../starter/results/test_20261113_214547/test_review.json), [summary](../../starter/results/test_20261113_214547/test_summary.json), [phương pháp](../../starter/results/test_20261113_214547/review_method.md).
- Audit: [coherence](../../starter/results/final_audit/coherence.json), [metadata](../../starter/results/final_audit/metadata.json), [grounding](../../starter/results/final_audit/grounding.json), [tổng hợp](../../starter/results/final_audit/summary.json), [runtime](../../starter/results/final_audit/runtime_validation.json), [kế hoạch mẫu](../../artifacts/coherence_sample_plan.json).
- [Experiment log](../../artifacts/experiment_log.csv), [môi trường](../../starter/results/final_audit/environment.json), [hướng dẫn chạy](../../README.md).

Đã dùng ChatGPT/Codex hỗ trợ giải thích, viết/sửa mã, chọn trang/chuẩn bị câu hỏi, chấm bằng chứng và soạn báo cáo. Kiểm chứng gồm hash nguồn, PDF evidence, toàn bộ chunk/vector, trace/nhãn, SQL local và phép chạy model thật; không coi AI judge là người chấm độc lập. Không có metric câu trả lời sinh bởi LLM.

**Còn chờ học viên:** xác minh quyền xử lý/chia sẻ bốn PDF và nội dung trích xuất; quyết định/cung cấp cách chia sẻ hợp lệ cho người chấm; tự kiểm tra/commit bản cuối và tự nộp link. Học viên đã xác nhận tên, MSSV, lớp, repo; chưa cung cấp commit chốt hoặc bằng chứng nộp. Không tự tick đã nộp. Quyền chưa xác minh vẫn giữ nguyên trong manifest và checklist.
