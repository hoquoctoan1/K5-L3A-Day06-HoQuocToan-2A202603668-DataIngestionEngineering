import argparse
import json
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row
from sentence_transformers import SentenceTransformer

parser = argparse.ArgumentParser()
parser.add_argument("--strategy", choices=["A", "B", "C"], required=True)
parser.add_argument("--question", required=True)
parser.add_argument(
    "--category",
    choices=["academic", "financial", "scholarship", "graduation"],
)
arguments = parser.parse_args()

question = arguments.question.strip()

if not question:
    raise ValueError("Câu hỏi không được để trống.")

if arguments.strategy != "C" and arguments.category:
    raise ValueError("Chỉ cấu hình C được dùng filter.")

data_strategy = "B" if arguments.strategy == "C" else arguments.strategy

starter_folder = Path(__file__).resolve().parents[1]
load_dotenv(starter_folder / ".env")

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise ValueError("Chưa có DATABASE_URL.")

model_name = "intfloat/multilingual-e5-small"
model_revision = "614241f622f53c4eeff9890bdc4f31cfecc418b3"

model = SentenceTransformer(
    model_name,
    revision=model_revision,
    device="cpu",
    local_files_only=True,
)

query_text = "query: " + question

token_ids = model.tokenizer(
    query_text,
    truncation=False,
)["input_ids"]

if len(token_ids) > model.max_seq_length:
    raise ValueError("Câu hỏi vượt giới hạn token.")

query_vector = model.encode(
    query_text,
    normalize_embeddings=True,
)

vector_text = json.dumps(query_vector.tolist(), allow_nan=False)

with psycopg.connect(
    database_url,
    connect_timeout=5,
    row_factory=dict_row,
) as connection:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT embedding_model, model_revision
            FROM rag_chunks
            WHERE strategy = %s
            """,
            (data_strategy,),
        )

        stored_models = cursor.fetchall()

        if (
            len(stored_models) != 1
            or stored_models[0]["embedding_model"] != model_name
            or stored_models[0]["model_revision"] != model_revision
        ):
            raise ValueError("Dữ liệu thiếu hoặc không khớp model truy vấn.")

        cursor.execute(
            """
            SELECT
                chunk_id,
                document_id,
                source,
                page,
                category,
                content,
                embedding <=> %s::vector AS distance
            FROM rag_chunks
            WHERE strategy = %s
              AND embedding_model = %s
              AND model_revision = %s
              AND (%s::text IS NULL OR category = %s)
            ORDER BY distance ASC, chunk_id ASC
            LIMIT 3
            """,
            (
                vector_text,
                data_strategy,
                model_name,
                model_revision,
                arguments.category,
                arguments.category,
            ),
        )

        results = cursor.fetchall()

print("Cấu hình:", arguments.strategy)
print("Câu hỏi:", question)
print("Filter:", arguments.category or "Không lọc")

if not results:
    print("Không có chunk trong phạm vi đã chọn.")

for rank, result in enumerate(results, start=1):
    similarity = 1 - result["distance"]

    print(f"\nKẾT QUẢ {rank}")
    print("Chunk:", result["chunk_id"])
    print("Điểm tương đồng:", round(similarity, 4))
    print("Nguồn:", result["source"])
    print("Trang:", result["page"])
    print("Nhóm:", result["category"])
    print("Nội dung:")
    print(result["content"])