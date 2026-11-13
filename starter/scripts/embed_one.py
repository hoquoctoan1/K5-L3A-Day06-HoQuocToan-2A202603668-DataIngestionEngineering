import json
from pathlib import Path

from sentence_transformers import SentenceTransformer

results_folder = Path(__file__).resolve().parents[1] / "results"
input_path = results_folder / "chunks_A.json"
chunks = json.loads(input_path.read_text(encoding="utf-8"))

chunk = chunks[0]
document_text = "passage: " + chunk["text"]

print("Đang tải hoặc mở model E5...")

model = SentenceTransformer(
    "intfloat/multilingual-e5-small",
    device="cpu",
)

token_ids = model.tokenizer(
    document_text,
    truncation=False,
)["input_ids"]

if len(token_ids) > model.max_seq_length:
    raise ValueError("Chunk vượt giới hạn token của model.")

vector = model.encode(
    document_text,
    normalize_embeddings=True,
)

print("Mã chunk:", chunk["chunk_id"])
print("Số token đầu vào:", len(token_ids))
print("Số chiều vector:", len(vector))
print("10 giá trị đầu:", vector[:10].tolist())