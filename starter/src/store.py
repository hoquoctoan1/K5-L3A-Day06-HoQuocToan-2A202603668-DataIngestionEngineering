"""Parameterized, exact pgvector search and transactional snapshot replacement."""
import json
import math
from typing import Any
import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from .models import Chunk
from .embeddings import MODEL_NAME, MODEL_REVISION


class PgVectorStore:
    def __init__(self, database_url: str, dimensions: int, *, table_name: str = "rag_chunks", temporary: bool = False) -> None:
        if dimensions != 384:
            raise ValueError("This experiment requires vector(384)")
        self.dimensions = dimensions
        self.table = sql.Identifier(table_name)
        self.temporary = temporary
        self.connection = psycopg.connect(database_url, connect_timeout=5, row_factory=dict_row)

    def close(self):
        self.connection.close()

    def _vector(self, vector):
        if len(vector) != self.dimensions or not all(math.isfinite(x) for x in vector) or not any(vector):
            raise ValueError("Vector must contain 384 finite values and be nonzero")
        return json.dumps(vector, allow_nan=False)

    def create_schema(self) -> None:
        with self.connection.transaction():
            self.connection.execute("CREATE EXTENSION IF NOT EXISTS vector")
            self.connection.execute(sql.SQL("""CREATE {temporary} TABLE IF NOT EXISTS {table} (
                strategy text NOT NULL CHECK(strategy IN ('A','B')), chunk_id text NOT NULL,
                document_id text NOT NULL, source text NOT NULL, page integer NOT NULL CHECK(page>0),
                category text NOT NULL, language text NOT NULL, content text NOT NULL,
                embedding_model text NOT NULL, model_revision text NOT NULL, embedding vector(384) NOT NULL,
                PRIMARY KEY(strategy,chunk_id))""").format(
                    temporary=sql.SQL("TEMPORARY" if self.temporary else ""), table=self.table))

    def upsert(self, strategy: str, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        if strategy not in {"A", "B"} or not chunks or len(chunks) != len(vectors):
            raise ValueError("Require strategy A/B and nonempty, aligned chunks/vectors")
        ids = [c.chunk_id for c in chunks]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate chunk IDs")
        rows = [(strategy, c.chunk_id, c.document_id, c.source, c.page, c.metadata["category"],
                 c.metadata["language"], c.text, MODEL_NAME, MODEL_REVISION, self._vector(v))
                for c, v in zip(chunks, vectors)]
        with self.connection.transaction(), self.connection.cursor() as cursor:
            cursor.execute(sql.SQL("SELECT DISTINCT embedding_model,model_revision FROM {} WHERE strategy<>%s").format(self.table), (strategy,))
            if any((r["embedding_model"], r["model_revision"]) != (MODEL_NAME, MODEL_REVISION) for r in cursor.fetchall()):
                raise ValueError("Model mismatch with another strategy")
            cursor.executemany(sql.SQL("""INSERT INTO {} (strategy,chunk_id,document_id,source,page,category,language,content,embedding_model,model_revision,embedding)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::vector)
                ON CONFLICT(strategy,chunk_id) DO UPDATE SET
                document_id=EXCLUDED.document_id, source=EXCLUDED.source, page=EXCLUDED.page,
                category=EXCLUDED.category, language=EXCLUDED.language, content=EXCLUDED.content,
                embedding_model=EXCLUDED.embedding_model, model_revision=EXCLUDED.model_revision, embedding=EXCLUDED.embedding""").format(self.table), rows)
            cursor.execute(sql.SQL("DELETE FROM {} WHERE strategy=%s AND NOT(chunk_id=ANY(%s::text[]))").format(self.table), (strategy, ids))

    def search(self, strategy: str, query_vector: list[float], top_k: int = 3,
               filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        if strategy not in {"A", "B", "C"} or top_k < 1:
            raise ValueError("Invalid strategy/top_k")
        filters = filters or {}
        if strategy != "C" and filters:
            raise ValueError("Only C applies metadata filters")
        if set(filters) - {"category"}:
            raise ValueError("Only category is supported by this experiment")
        category = filters.get("category")
        if category is not None and (not isinstance(category, str) or not category):
            raise ValueError("category must be a nonempty string")
        rows = self.connection.execute(sql.SQL("""SELECT chunk_id,document_id,source,page,category,language,content,
            embedding <=> %s::vector AS distance FROM {}
            WHERE strategy=%s AND embedding_model=%s AND model_revision=%s
              AND (%s::text IS NULL OR category=%s)
            ORDER BY distance ASC,chunk_id ASC LIMIT %s""").format(self.table),
            (self._vector(query_vector), "B" if strategy == "C" else strategy,
             MODEL_NAME, MODEL_REVISION, category, category, top_k)).fetchall()
        for rank, row in enumerate(rows, 1):
            row.update(rank=rank, similarity=1-row["distance"])
        return rows
