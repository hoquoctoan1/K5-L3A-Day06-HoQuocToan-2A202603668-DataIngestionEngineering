import json
import re
from pathlib import Path


def choose_chunk_end(text, start_char, chunk_size, overlap):
    limit = min(start_char + chunk_size, len(text))

    if limit == len(text):
        return limit

    window = text[start_char:limit + 1]

    sentence_ends = [
        match.end()
        for match in re.finditer(r"[.!?](?=\s)", window)
        if overlap < match.end() <= chunk_size
    ]

    if sentence_ends:
        return start_char + sentence_ends[-1]

    word_boundaries = [
        match.start()
        for match in re.finditer(r"\s+", window)
        if overlap < match.start() <= chunk_size
    ]

    if word_boundaries:
        return start_char + word_boundaries[-1]

    return limit

def split_page_text(text, chunk_size, overlap):
    paragraphs = [
        part.strip()
        for part in re.split(r"\n[ \t]*\n", text)
        if part.strip()
    ]

    paragraph_groups = []
    current_chunk = ""

    for paragraph in paragraphs:
        if current_chunk:
            candidate = current_chunk + "\n\n" + paragraph
        else:
            candidate = paragraph

        if current_chunk and len(candidate) > chunk_size:
            paragraph_groups.append(current_chunk)
            current_chunk = paragraph
        else:
            current_chunk = candidate

    if current_chunk:
        paragraph_groups.append(current_chunk)

    page_chunks = []

    for group_text in paragraph_groups:
        start_char = 0

        while start_char < len(group_text):
            end_char = choose_chunk_end(
                group_text,
                start_char,
                chunk_size,
                overlap,
            )

            page_chunks.append(group_text[start_char:end_char])

            if end_char == len(group_text):
                break

            start_char = end_char - overlap

    return page_chunks


results_folder = Path(__file__).resolve().parents[1] / "results"
input_path = results_folder / "pages_clean.json"
pages = json.loads(input_path.read_text(encoding="utf-8"))

chunk_size = 500
overlap = 50
chunks = []

for page in pages:
    if not page["text"].strip():
        raise ValueError(
            f"Trang rỗng: {page['document_id']}, trang {page['page']}"
        )

    page_chunks = split_page_text(
        page["text"],
        chunk_size,
        overlap,
    )

    for chunk_number, chunk_text in enumerate(page_chunks, start=1):
        chunk = {
            **page,
            "chunk_id": (
                f"B:{page['document_id']}:"
                f"p{page['page']}:c{chunk_number}"
            ),
            "strategy": "B",
            "text": chunk_text,
        }

        chunks.append(chunk)

output_path = results_folder / "chunks_B.json"
output_path.write_text(
    json.dumps(chunks, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

print("Số trang đầu vào:", len(pages))
print("Tổng số chunk B:", len(chunks))
print("Độ dài chunk lớn nhất:", max(len(chunk["text"]) for chunk in chunks))
print("Đã lưu tại:", output_path)