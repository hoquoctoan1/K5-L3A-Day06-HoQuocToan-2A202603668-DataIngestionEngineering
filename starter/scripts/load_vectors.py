import argparse
import json
import os
import time
from pathlib import Path

import psycopg
from dotenv import load_dotenv

parser = argparse.ArgumentParser()
parser.add_argument("--strategy", choices=["A", "B"], required=True)
arguments = parser.parse_args()

strategy = arguments.strategy
starter_folder = Path(__file__).resolve().parents[1]
load_dotenv(starter_folder / ".env")

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise ValueError("Chưa có DATABASE_URL trong .env.")

input_path = starter_folder / "results" / f"embeddings_{strategy}.json"
data = json.loads(input_path.read_text(encoding="utf-8"))
chunks = data["chunks"]

if data["strategy"] != strategy or data["dimensions"] != 384:
    raise ValueError("File không đúng cấu hình hoặc số chiều.")

if not chunks:
    raise ValueError("File không có chunk; dừng để tránh xóa dữ liệu.")

chunk_ids = [chunk["chunk_id"] for chunk in chunks]

if len(set(chunk_ids)) != len(chunk_ids):
    raise ValueError("Có chunk_id bị trùng trong file.")

rows = []

for chunk in chunks:
    if len(chunk["embedding"]) != 384:
        raise ValueError(f"Vector sai số chiều: {chunk['chunk_id']}")

    rows.append((
        strategy,
        chunk["chunk_id"],
        chunk["document_id"],
        chunk["source"],
        chunk["page"],
        chunk["category"],
        chunk["language"],
        chunk["text"],
        data["embedding_model"],
        data["model_revision"],
        json.dumps(chunk["embedding"], allow_nan=False),
    ))

start_time = time.perf_counter()

with psycopg.connect(database_url, connect_timeout=5) as connection:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT embedding_model, model_revision
            FROM rag_chunks
            WHERE strategy <> %s
            """,
            (strategy,),
        )

        expected_model = (
            data["embedding_model"],
            data["model_revision"],
        )

        if any(record != expected_model for record in cursor.fetchall()):
            raise ValueError("Cấu hình khác đang dùng model hoặc phiên bản khác.")

        cursor.executemany(
            """
            INSERT INTO rag_chunks (
                strategy, chunk_id, document_id, source, page,
                category, language, content,
                embedding_model, model_revision, embedding
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s::vector
            )
            ON CONFLICT (strategy, chunk_id)
            DO UPDATE SET
                document_id = EXCLUDED.document_id,
                source = EXCLUDED.source,
                page = EXCLUDED.page,
                category = EXCLUDED.category,
                language = EXCLUDED.language,
                content = EXCLUDED.content,
                embedding_model = EXCLUDED.embedding_model,
                model_revision = EXCLUDED.model_revision,
                embedding = EXCLUDED.embedding
            """,
            rows,
        )

        cursor.execute(
            """
            DELETE FROM rag_chunks
            WHERE strategy = %s
              AND NOT (chunk_id = ANY(%s::text[]))
            """,
            (strategy, chunk_ids),
        )

        cursor.execute(
            "SELECT COUNT(*) FROM rag_chunks WHERE strategy = %s",
            (strategy,),
        )

        stored_count = cursor.fetchone()[0]

        if stored_count != len(chunks):
            raise ValueError("Số dòng trong database không khớp file.")

elapsed = time.perf_counter() - start_time

print("Cấu hình:", strategy)
print("Số chunk trong database:", stored_count)
print("Thời gian nạp:", round(elapsed, 2), "giây")