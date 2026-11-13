import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path


def normalize(text):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text)).strip()


def main():
    parser = argparse.ArgumentParser(description="Check benchmark labels and source evidence; does not run retrieval.")
    parser.add_argument("--split", choices=["all", "dev", "test"], default="all")
    parser.add_argument("--list", action="store_true", help="Print questions only, without answers")
    parser.add_argument("--verify-pdf", action="store_true", help="Also check evidence against original PDF pages")
    arguments = parser.parse_args()
    repository = Path(__file__).resolve().parents[2]
    questions_path = repository / "benchmark/questions.json"
    pages_path = repository / "starter/results/pages_clean.json"
    try:
        questions = json.loads(questions_path.read_text(encoding="utf-8"))
        plan = json.loads((repository / "benchmark/selection_plan.json").read_text(encoding="utf-8"))
        manifest = json.loads((repository / "data/manifest.json").read_text(encoding="utf-8"))
        pages = json.loads(pages_path.read_text(encoding="utf-8"))
        if not isinstance(questions, list) or not all(isinstance(question, dict) for question in questions):
            raise ValueError("questions.json must contain a list of question records")
        if hashlib.sha256(questions_path.read_bytes()).hexdigest() != plan["questions_sha256"]:
            raise ValueError("Questions changed after split was frozen. Review and version the selection plan before proceeding.")
        if hashlib.sha256(pages_path.read_bytes()).hexdigest() != plan["pages_clean_sha256"]:
            raise ValueError("Corpus changed after evidence verification. Recheck evidence and version the selection plan.")
        required = {"id", "split", "topic", "question", "expected_answer", "gold_source_id", "gold_page", "evidence_quote", "filter"}
        for question in questions:
            if not required <= question.keys():
                raise ValueError(f"Missing fields: {question.get('id', '<no id>')}")
            if not all(isinstance(question[field], str) and question[field].strip() for field in ["id", "question", "expected_answer", "gold_source_id", "evidence_quote"]):
                raise ValueError(f"Empty or invalid text fields: {question['id']}")
            if question["split"] not in {"dev", "test"}:
                raise ValueError(f"Invalid split: {question['id']}")
            if type(question["gold_page"]) is not int or question["gold_page"] < 1:
                raise ValueError(f"Invalid page: {question['id']}")
        if len({question["id"] for question in questions}) != len(questions):
            raise ValueError("Duplicate question IDs")
        if len({normalize(question["question"]) for question in questions}) != len(questions):
            raise ValueError("Duplicate question wording")
        counts = Counter(question["split"] for question in questions)
        if len(questions) != 20 or counts != {"dev": 15, "test": 5}:
            raise ValueError("This frozen benchmark requires exactly 15 dev and 5 test questions")
        topics = Counter(question["topic"] for question in questions)
        expected_topics = {"academic", "financial", "scholarship", "graduation"}
        if topics != {topic: 5 for topic in expected_topics}:
            raise ValueError("This benchmark requires five questions per topic")
        for split in ["dev", "test"]:
            if {question["topic"] for question in questions if question["split"] == split} != expected_topics:
                raise ValueError(f"Split does not cover all topics: {split}")
        filters = Counter(question["split"] for question in questions if question["filter"])
        if sum(filters.values()) < 3 or filters["test"] < 1:
            raise ValueError("Need at least three filter questions including one test question")
        documents = {document["source_id"]: document for document in manifest["documents"]}
        page_lookup = {(page["document_id"], page["page"]): page for page in pages}
        for source_id, expected_hash in plan["source_snapshots"].items():
            pdf_path = repository / documents[source_id]["source_path_or_url"]
            if hashlib.sha256(pdf_path.read_bytes()).hexdigest() != expected_hash:
                raise ValueError(f"Original PDF changed: {source_id}")
        selected = [question for question in questions if arguments.split == "all" or question["split"] == arguments.split]
        readers = {}
        for question in selected:
            source_key = question["gold_source_id"], question["gold_page"]
            if source_key not in page_lookup:
                raise ValueError(f"Gold page is outside selected corpus: {question['id']}")
            page = page_lookup[source_key]
            if question["topic"] != page["category"]:
                raise ValueError(f"Topic does not match source metadata: {question['id']}")
            if normalize(question["evidence_quote"]) not in normalize(page["text"]):
                raise ValueError(f"Evidence missing in extracted page: {question['id']}")
            question_filter = question["filter"]
            if not isinstance(question_filter, dict) or set(question_filter) - {"category"}:
                raise ValueError(f"Invalid filter fields: {question['id']}")
            if question_filter:
                if question_filter.get("category") != page["category"] or not question.get("filter_context"):
                    raise ValueError(f"Invalid filter context: {question['id']}")
            if arguments.verify_pdf:
                from pypdf import PdfReader

                source_id, page_number = source_key
                if source_id not in readers:
                    readers[source_id] = PdfReader(repository / documents[source_id]["source_path_or_url"])
                original_text = readers[source_id].pages[page_number - 1].extract_text() or ""
                if normalize(question["evidence_quote"]) not in normalize(original_text):
                    raise ValueError(f"Evidence missing in original PDF: {question['id']}")
        print("Benchmark check OK")
        print(f"Questions: {len(questions)} | dev: {counts['dev']} | test: {counts['test']}")
        print("Each topic: 5 questions")
        print(f"Filter questions | dev: {filters['dev']} | test: {filters['test']}")
        print(f"Evidence checked: {len(selected)} | split: {arguments.split}")
        if arguments.verify_pdf:
            print("Original PDF evidence: verified")
        print("No retrieval, embeddings, Hit@1 or Hit@3 were computed.")
        if arguments.list:
            for question in selected:
                print(f"{question['id']} [{question['topic']}]: {question['question']}")
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"Benchmark check failed: {error}\n")


if __name__ == "__main__":
    main()
