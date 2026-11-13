import json
import unicodedata
from pathlib import Path

from pypdf import PdfReader

repository = Path(__file__).resolve().parents[2]
manifest_path = repository / "data" / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

pages = []

for document in manifest["documents"]:
    pdf_path = repository / document["source_path_or_url"]
    reader = PdfReader(pdf_path)

    for page_number in document["included_pages"]:
        text = reader.pages[page_number - 1].extract_text() or ""

        text = unicodedata.normalize("NFC", text)
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = text.replace("\u00a0", " ").strip()

        if not text:
            raise ValueError(f"Không lấy được chữ: {pdf_path.name}, trang {page_number}")

        pages.append({
            "document_id": document["source_id"],
            "source": document["source_path_or_url"],
            "page": page_number,
            "category": document["category"],
            "language": document["language"],
            "text": text,
        })

output_path = repository / "starter" / "results" / "pages.json"
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(
    json.dumps(pages, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

print(f"Đã đọc {len(pages)} trang")
print(f"Đã lưu tại: {output_path}")