import json
import re
import unicodedata
from pathlib import Path

results_folder = Path(__file__).resolve().parents[1] / "results"
input_path = results_folder / "pages.json"

pages = json.loads(input_path.read_text(encoding="utf-8"))

for page in pages:
    text = unicodedata.normalize("NFC", page["text"])
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\u00a0", " ")

    lines = [
        re.sub(r"[ \t]+", " ", line).strip()
        for line in text.split("\n")
    ]

    if lines and lines[0] == str(page["page"]):
        lines.pop(0)

    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    page["text"] = text

output_path = results_folder / "pages_clean.json"
output_path.write_text(
    json.dumps(pages, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

print(f"Đã chuẩn hóa {len(pages)} trang")
print("Kết quả:", output_path)
