import json
from pathlib import Path

results_folder = Path(__file__).resolve().parents[1] / "results"
input_path = results_folder / "pages_clean.json"
pages = json.loads(input_path.read_text(encoding="utf-8"))

chunk_size = 500
overlap = 50
chunks = []

for page in pages:
    text = page["text"]
    start_char = 0

    while start_char < len(text):
        end_char = min(start_char + chunk_size, len(text))
        chunk_text = text[start_char:end_char]

        chunk = {
            **page,
            "chunk_id": (
                f"A:{page['document_id']}:"
                f"p{page['page']}:s{start_char}"
            ),
            "strategy": "A",
            "start_char": start_char,
            "end_char": end_char,
            "text": chunk_text,
        }

        chunks.append(chunk)

        if end_char == len(text):
            break

        start_char = end_char - overlap

output_path = results_folder / "chunks_A.json"
output_path.write_text(
    json.dumps(chunks, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

print("Số trang đầu vào:", len(pages))
print("Tổng số chunk A:", len(chunks))
print("Đã lưu tại:", output_path)