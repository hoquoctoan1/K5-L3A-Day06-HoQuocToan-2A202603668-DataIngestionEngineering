"""The same A/B algorithms as the scripts used for the saved experiments."""
import re
from .models import Chunk, DocumentPage


def fixed_size(page: DocumentPage, size: int, overlap: int) -> list[Chunk]:
    if not 0 <= overlap < size:
        raise ValueError("Require 0 <= overlap < size")
    chunks, start = [], 0
    while start < len(page.text):
        end = min(start + size, len(page.text))
        chunks.append(Chunk(f"A:{page.document_id}:p{page.page}:s{start}", page.document_id,
                            page.source, page.page, page.text[start:end],
                            {**page.metadata, "strategy": "A", "start_char": start, "end_char": end}))
        if end == len(page.text):
            break
        start = end - overlap
    return chunks


def _choose_end(text, start, size, overlap):
    limit = min(start + size, len(text))
    if limit == len(text):
        return limit
    window = text[start:limit + 1]
    ends = [m.end() for m in re.finditer(r"[.!?](?=\s)", window) if overlap < m.end() <= size]
    if ends:
        return start + ends[-1]
    spaces = [m.start() for m in re.finditer(r"\s+", window) if overlap < m.start() <= size]
    return start + spaces[-1] if spaces else limit


def by_paragraph(page: DocumentPage, max_size: int, overlap: int = 50) -> list[Chunk]:
    if not 0 <= overlap < max_size:
        raise ValueError("Require 0 <= overlap < max_size")
    groups, current = [], ""
    for paragraph in (p.strip() for p in re.split(r"\n[ \t]*\n", page.text) if p.strip()):
        candidate = current + "\n\n" + paragraph if current else paragraph
        if current and len(candidate) > max_size:
            groups.append(current)
            current = paragraph
        else:
            current = candidate
    if current:
        groups.append(current)
    chunks = []
    for group in groups:
        start = 0
        while start < len(group):
            end = _choose_end(group, start, max_size, overlap)
            chunks.append(Chunk(f"B:{page.document_id}:p{page.page}:c{len(chunks) + 1}",
                                page.document_id, page.source, page.page, group[start:end],
                                {**page.metadata, "strategy": "B"}))
            if end == len(group):
                break
            start = end - overlap
    return chunks
