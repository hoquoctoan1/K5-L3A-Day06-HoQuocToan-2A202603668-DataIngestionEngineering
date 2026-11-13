import argparse
import json
import time
from importlib.metadata import version
from pathlib import Path

from sentence_transformers import SentenceTransformer

parser = argparse.ArgumentParser()
parser.add_argument("--strategy", choices=["A", "B"], required=True)
arguments = parser.parse_args()

strategy = arguments.strategy
results_folder = Path(__file__).resolve().parents[1] / "results"
input_path = results_folder / f"chunks_{strategy}.json"

chunks = json.loads(input_path.read_text(encoding="utf-8"))

model_name = "intfloat/multilingual-e5-small"
model_revision = "614241f622f53c4eeff9890bdc4f31cfecc418b3"

model = SentenceTransformer(
    model_name,
    revision=model_revision,
    device="cpu",
    local_files_only=True,
)

texts = ["passage: " + chunk["text"] for chunk in chunks]

for chunk, text in zip(chunks, texts):
    token_ids = model.tokenizer(
        text,
        truncation=False,
    )["input_ids"]

    if len(token_ids) > model.max_seq_length:
        raise ValueError(
            f"Chunk vượt giới hạn token: {chunk['chunk_id']}"
        )

start_time = time.perf_counter()

vectors = model.encode(
    texts,
    batch_size=16,
    normalize_embeddings=True,
    show_progress_bar=True,
)

embedding_seconds = time.perf_counter() - start_time

if vectors.shape != (len(chunks), 384):
    raise ValueError("Số vector hoặc số chiều không đúng.")

embedded_chunks = [
    {
        **chunk,
        "embedding": vector.tolist(),
    }
    for chunk, vector in zip(chunks, vectors)
]

output = {
    "strategy": strategy,
    "embedding_model": model_name,
    "model_revision": model_revision,
    "dimensions": 384,
    "normalize_embeddings": True,
    "document_prefix": "passage: ",
    "query_prefix": "query: ",
    "embedding_seconds": embedding_seconds,
    "package_versions": {
        "sentence-transformers": version("sentence-transformers"),
        "torch": version("torch"),
        "transformers": version("transformers"),
    },
    "chunks": embedded_chunks,
}

output_path = results_folder / f"embeddings_{strategy}.json"
output_path.write_text(
    json.dumps(output, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

print("Cấu hình:", strategy)
print("Số vector:", len(embedded_chunks))
print("Số chiều mỗi vector:", vectors.shape[1])
print("Thời gian embedding:", round(embedding_seconds, 2), "giây")
print("Đã lưu:", output_path)
