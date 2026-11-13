import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row
from sentence_transformers import SentenceTransformer

starter_folder = Path(__file__).resolve().parents[1]
repository = starter_folder.parent

subprocess.run(
    [
        sys.executable,
        str(starter_folder / "scripts" / "check_benchmark.py"),
        "--split",
        "test",
    ],
    check=True,
)

questions = json.loads(
    (repository / "benchmark" / "questions.json").read_text(
        encoding="utf-8"
    )
)
test_questions = [
    question for question in questions
    if question["split"] == "test"
]

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

run_name = datetime.now(
    timezone(timedelta(hours=7))
).strftime("test_%Y%m%d_%H%M%S")

output_folder = starter_folder / "results" / run_name
output_folder.mkdir(parents=True, exist_ok=False)

traces = []

with psycopg.connect(
    database_url,
    connect_timeout=5,
    row_factory=dict_row,
) as connection:
    with connection.cursor() as cursor:
        for question in test_questions:
            query_text = "query: " + question["question"]

            token_ids = model.tokenizer(
                query_text,
                truncation=False,
            )["input_ids"]

            if len(token_ids) > model.max_seq_length:
                raise ValueError(
                    f"Câu hỏi quá dài: {question['id']}"
                )

            embedding_start = time.perf_counter()

            query_vector = model.encode(
                query_text,
                normalize_embeddings=True,
            )

            embedding_seconds = (
                time.perf_counter() - embedding_start
            )

            vector_text = json.dumps(
                query_vector.tolist(),
                allow_nan=False,
            )

            for strategy in ["A", "B", "C"]:
                data_strategy = "B" if strategy == "C" else strategy
                applied_filter = (
                    question.get("filter", {})
                    if strategy == "C"
                    else {}
                )
                category = applied_filter.get("category")

                retrieval_start = time.perf_counter()

                cursor.execute(
                    """
                    SELECT
                        chunk_id,
                        document_id,
                        source,
                        page,
                        category,
                        language,
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
                        category,
                        category,
                    ),
                )

                results = cursor.fetchall()
                retrieval_seconds = (
                    time.perf_counter() - retrieval_start
                )

                if not results:
                    raise ValueError(
                        f"Không có kết quả: "
                        f"{question['id']} / {strategy}. "
                        "Kiểm tra dữ liệu và model trong database."
                    )

                for rank, result in enumerate(results, start=1):
                    result["rank"] = rank
                    result["similarity"] = 1 - result["distance"]

                traces.append({
                    "question_id": question["id"],
                    "split": "test",
                    "strategy": strategy,
                    "data_strategy": data_strategy,
                    "question": question["question"],
                    "applied_filter": applied_filter,
                    "query_embedding_seconds": embedding_seconds,
                    "retrieval_seconds": retrieval_seconds,
                    "results": results,
                    "review_status": "unreviewed",
                })

                print(
                    question["id"],
                    strategy,
                    "đã lưu", len(results), "kết quả",
                )

output = {
    "run_name": run_name,
    "split": "test",
    "embedding_model": model_name,
    "model_revision": model_revision,
    "metric": "cosine",
    "top_k": 3,
    "question_count": len(test_questions),
    "search_count": len(traces),
    "traces": traces,
}

output_path = output_folder / "traces.json"
output_path.write_text(
    json.dumps(output, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

print("Hoàn thành:", len(traces), "lượt tìm kiếm")
print("File kết quả:", output_path)
print("Chưa chấm Hit@1/Hit@3; cần kiểm tra bằng chứng.")