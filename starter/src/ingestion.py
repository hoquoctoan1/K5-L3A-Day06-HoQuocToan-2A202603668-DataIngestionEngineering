"""PDF extraction and structure-preserving NFC normalization."""
import re
import unicodedata
from pathlib import Path

from pypdf import PdfReader
from .models import DocumentPage


def load_pdf(path: Path, document_id: str, source: str) -> list[DocumentPage]:
    pages = []
    for number, page in enumerate(PdfReader(path).pages, 1):
        text = unicodedata.normalize("NFC", page.extract_text() or "")
        text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\u00a0", " ").strip()
        pages.append(DocumentPage(document_id, source, number, text, {"empty_text": not bool(text)}))
    return pages


def normalize_text(text: str, page_number: int | None = None) -> str:
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\u00a0", " ")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    if page_number is not None and lines and lines[0] == str(page_number):
        lines.pop(0)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
