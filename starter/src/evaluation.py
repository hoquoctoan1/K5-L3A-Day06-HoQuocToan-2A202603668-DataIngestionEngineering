"""Exact evidence proxy; subjective review labels remain explicit inputs."""
import re
import unicodedata
from collections import defaultdict
from typing import Any


def _normalize(text):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text)).strip()


def evaluate_query(question: dict[str, Any], hits: list[dict[str, Any]]) -> dict[str, Any]:
    golds = [question, *question.get("alternative_gold", [])]
    results = []
    for rank, hit in enumerate(hits[:3], 1):
        matched = any(hit["document_id"] == gold["gold_source_id"] and hit["page"] == gold["gold_page"]
                      and _normalize(gold["evidence_quote"]) in _normalize(hit.get("content", hit.get("text", "")))
                      for gold in golds)
        results.append({**hit, "rank": rank, "exact_gold_match": matched})
    return {"question_id": question["id"], "split": question["split"], "results": results,
            "hit1_exact": int(bool(results) and results[0]["exact_gold_match"]),
            "hit3_exact": int(any(r["exact_gold_match"] for r in results)),
            "manual_hit1": None, "manual_hit3": None, "manual_reason": ""}


def summarize(traces: list[dict[str, Any]]) -> dict[str, Any]:
    groups = defaultdict(list)
    for trace in traces:
        groups[trace["split"], trace["strategy"]].append(trace)
    summary = {}
    for (split, strategy), rows in groups.items():
        entry = {"questions": len(rows)}
        for name, first, third in [("exact", "hit1_exact", "hit3_exact"), ("manual", "manual_hit1", "manual_hit3")]:
            if any(row.get(first) is None or row.get(third) is None for row in rows):
                entry[name] = None
            else:
                a, b = sum(row[first] for row in rows), sum(row[third] for row in rows)
                entry[name] = {"hit1_count": a, "hit3_count": b, "hit1_rate": a/len(rows), "hit3_rate": b/len(rows)}
        summary[f"{split}/{strategy}"] = entry
    return summary
