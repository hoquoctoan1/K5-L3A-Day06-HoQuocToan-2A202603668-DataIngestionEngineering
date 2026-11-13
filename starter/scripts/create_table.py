import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

starter_folder = Path(__file__).resolve().parents[1]
load_dotenv(starter_folder / ".env")

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise ValueError("Chưa có DATABASE_URL trong file .env.")

with psycopg.connect(database_url, connect_timeout=5) as connection:
    with connection.cursor() as cursor:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rag_chunks (
                strategy TEXT NOT NULL
                    CHECK (strategy IN ('A', 'B')),
                chunk_id TEXT NOT NULL,
                document_id TEXT NOT NULL,
                source TEXT NOT NULL,
                page INTEGER NOT NULL CHECK (page > 0),
                category TEXT NOT NULL,
                language TEXT NOT NULL,
                content TEXT NOT NULL,
                embedding_model TEXT NOT NULL,
                model_revision TEXT NOT NULL,
                embedding vector(384) NOT NULL,
                PRIMARY KEY (strategy, chunk_id)
            )
        """)

print("Bảng rag_chunks đã sẵn sàng.")