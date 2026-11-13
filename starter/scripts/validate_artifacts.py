"""Read-only verification of saved corpus, vectors, reviews and library parity."""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.models import DocumentPage
from src.ingestion import load_pdf, normalize_text
from src.chunking import fixed_size, by_paragraph
from src.evaluation import evaluate_query


def validate(repository):
    def read(relative):
        return json.loads((repository / relative).read_text(encoding="utf-8"))
    plan = read("benchmark/selection_plan.json")
    for relative, key in [("benchmark/questions.json", "questions_sha256"), ("starter/results/pages_clean.json", "pages_clean_sha256")]:
        assert hashlib.sha256((repository / relative).read_bytes()).hexdigest() == plan[key]
    manifest = read("data/manifest.json")
    clean = read("starter/results/pages_clean.json")
    clean_lookup = {(p["document_id"], p["page"]): p for p in clean}
    assert sum(d["counted_page_count"] for d in manifest["documents"]) >= 30
    for document in manifest["documents"]:
        pdf = repository / document["source_path_or_url"]
        assert hashlib.sha256(pdf.read_bytes()).hexdigest() == plan["source_snapshots"][document["source_id"]]
        raw = load_pdf(pdf, document["source_id"], document["source_path_or_url"])
        for number in document["included_pages"]:
            assert normalize_text(raw[number-1].text, number) == clean_lookup[document["source_id"], number]["text"]
    chunk_counts = {}
    for strategy, function in [("A", lambda p: fixed_size(p, 500, 50)), ("B", lambda p: by_paragraph(p, 500, 50))]:
        expected = read(f"starter/results/chunks_{strategy}.json")
        generated = []
        for page in clean:
            obj = DocumentPage(page["document_id"], page["source"], page["page"], page["text"],
                               {"category": page["category"], "language": page["language"]})
            generated.extend(function(obj))
        assert len(generated) == len(expected)
        for actual, original in zip(generated, expected):
            for field in ["chunk_id", "document_id", "source", "page", "text"]:
                assert getattr(actual, field) == original[field]
            for field in ["category", "language", "strategy"]:
                assert actual.metadata[field] == original[field]
        embedded = read(f"starter/results/embeddings_{strategy}.json")
        assert embedded["dimensions"] == 384 and embedded["model_revision"] == "614241f622f53c4eeff9890bdc4f31cfecc418b3"
        assert len(embedded["chunks"]) == len(expected)
        for original, vector_record in zip(expected, embedded["chunks"]):
            assert all(vector_record[k] == v for k, v in original.items())
            v = vector_record["embedding"]
            assert len(v) == 384 and all(math.isfinite(x) for x in v)
            assert abs(sum(x*x for x in v)-1) < 1e-5
        chunk_counts[strategy] = len(expected)
    questions = {q["id"]: q for q in read("benchmark/questions.json")}
    reviews_checked = 0
    for split, folder in [("dev", "dev_20261113_210325"), ("test", "test_20261113_214547")]:
        trace = read(f"starter/results/{folder}/traces.json")
        reviews = read(f"starter/results/{folder}/{split}_review.json")
        lookup = {(r["question_id"], r["strategy"]): r for r in reviews}
        ids = {q["id"] for q in questions.values() if q["split"] == split}
        assert set(lookup) == {(qid,s) for qid in ids for s in "ABC"}
        assert len(trace["traces"]) == len(lookup) == 3*len(ids)
        for row in trace["traces"]:
            question = questions[row["question_id"]]
            review = lookup[row["question_id"],row["strategy"]]
            result = evaluate_query(question, row["results"])
            assert result["hit1_exact"] == review["hit1_exact"] and result["hit3_exact"] == review["hit3_exact"]
            assert 0 <= review["manual_hit1"] <= review["manual_hit3"] <= 1 and review["manual_reason"]
            assert len(review["results"]) == len(row["results"]) == 3
            for actual, original in zip(review["results"], row["results"]):
                assert all(actual[k] == v for k,v in original.items())
            assert row["applied_filter"] == ((question.get("filter") or {}) if row["strategy"] == "C" else {})
            reviews_checked += 1
    return {"pages": len(clean), "counted_pages": sum(d["counted_page_count"] for d in manifest["documents"]),
            "chunk_counts": chunk_counts, "reviewed_searches": reviews_checked,
            "checks": "PDF/source hashes; 50-page normalization; all A/B chunks exactly match src implementation; all stored vector dimensions/norms; all 60 dev/test reviews/traces/exact labels/filters"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    print(json.dumps(validate(args.repository), ensure_ascii=False, indent=2))
