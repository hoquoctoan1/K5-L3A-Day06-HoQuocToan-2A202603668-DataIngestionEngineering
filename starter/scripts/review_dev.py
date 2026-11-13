import argparse
import json
import re
import unicodedata
from pathlib import Path


def normalize(text):
    return re.sub(
        r"\s+",
        " ",
        unicodedata.normalize("NFC", text),
    ).strip()


parser = argparse.ArgumentParser()
parser.add_argument("--trace", type=Path, required=True)
arguments = parser.parse_args()

repository = Path(__file__).resolve().parents[2]

questions = json.loads(
    (repository / "benchmark" / "questions.json").read_text(
        encoding="utf-8"
    )
)
question_lookup = {
    question["id"]: question
    for question in questions
    if question["split"] == "dev"
}

trace_data = json.loads(
    arguments.trace.read_text(encoding="utf-8")
)

if trace_data["split"] != "dev":
    raise ValueError("Chương trình này chỉ chấm dữ liệu dev.")

output_path = arguments.trace.with_name("dev_review.json")

if output_path.exists():
    raise ValueError("File chấm đã tồn tại; không ghi đè nhãn đã nhập.")

reviews = []

for trace in trace_data["traces"]:
    question = question_lookup[trace["question_id"]]
    results = []

    for result in trace["results"]:
        exact_match = (
            result["document_id"] == question["gold_source_id"]
            and result["page"] == question["gold_page"]
            and normalize(question["evidence_quote"])
            in normalize(result["content"])
        )

        results.append({
            **result,
            "exact_gold_match": exact_match,
        })

    reviews.append({
        "question_id": question["id"],
        "strategy": trace["strategy"],
        "question": question["question"],
        "expected_answer": question["expected_answer"],
        "gold_source_id": question["gold_source_id"],
        "gold_page": question["gold_page"],
        "evidence_quote": question["evidence_quote"],
        "results": results,
        "hit1_exact": int(results[0]["exact_gold_match"]),
        "hit3_exact": int(any(
            result["exact_gold_match"]
            for result in results
        )),
        "manual_hit1": None,
        "manual_hit3": None,
        "manual_reason": "",
    })

output_path.write_text(
    json.dumps(reviews, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

print("Số lượt cần kiểm tra:", len(reviews))
print("File hỗ trợ chấm:", output_path)
print("Nhãn thủ công còn trống; chưa có điểm cuối cùng.")