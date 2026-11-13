import json
from pathlib import Path

CATEGORY_LABELS = {
    "academic": "Học tập",
    "financial": "Tài chính",
    "graduation": "Tốt nghiệp",
    "scholarship": "Học bổng",
}
DOCUMENT_LABELS = {
    "vinuni_academic": "Quy chế đào tạo đại học chính quy",
    "vinuni_financial": "Quy định tài chính và biểu phí",
    "vinuni_graduation": "Quy trình xét tốt nghiệp và cấp bằng",
    "vinuni_scholarship": "Quy định duy trì học bổng và hỗ trợ tài chính",
}
LANGUAGE_LABELS = {"vi": "Tiếng Việt", "en": "Tiếng Anh"}


def select_value(title, values, labels):
    values = sorted(values, key=lambda value: labels.get(value, value))
    print(f"\n{title}:")
    for number, value in enumerate(values, start=1):
        print(f"  {number}. {labels.get(value, value)}")

    while True:
        selected = input("Nhập số hoặc tên, Enter để chọn tất cả: ").strip()
        if not selected:
            return None
        if selected.isdecimal() and 1 <= int(selected) <= len(values):
            return values[int(selected) - 1]
        for value in values:
            if selected.casefold() in (
                value.casefold(), labels.get(value, value).casefold()
            ):
                return value
        print("Lựa chọn không hợp lệ. Hãy nhập số hoặc tên trong danh sách.")


def read_range(title, minimum):
    while True:
        selected = input(f"\n{title} (một số hoặc min-max, Enter để bỏ qua): ").strip()
        if not selected:
            return None
        try:
            parts = selected.split("-")
            if len(parts) == 1:
                lower = upper = int(parts[0])
            elif len(parts) == 2:
                lower, upper = map(int, parts)
            else:
                raise ValueError
            if lower < minimum or lower > upper:
                raise ValueError
            return lower, upper
        except ValueError:
            print(
                f"Hãy nhập số nguyên từ {minimum} trở lên hoặc khoảng tăng dần, "
                "ví dụ 2-5."
            )


def main():
    results_folder = Path(__file__).resolve().parents[1] / "results"
    input_path = results_folder / "chunks_B.json"
    chunks = json.loads(input_path.read_text(encoding="utf-8"))
    if not chunks:
        print("Không có đoạn văn bản để lọc.")
        return

    print("Các bộ lọc được kết hợp; nhấn Enter để bỏ qua từng bộ lọc.")
    selected_category = select_value(
        "Nhóm tài liệu", {chunk["category"] for chunk in chunks}, CATEGORY_LABELS
    )
    selected_document = select_value(
        "Tài liệu", {chunk["document_id"] for chunk in chunks}, DOCUMENT_LABELS
    )
    selected_language = select_value(
        "Ngôn ngữ", {chunk["language"] for chunk in chunks}, LANGUAGE_LABELS
    )
    page_range = read_range("Khoảng trang, ví dụ 2-5", minimum=1)
    keyword = input("\nTừ khóa trong nội dung, Enter để bỏ qua: ").strip().casefold()
    length_range = read_range("Độ dài đoạn văn bản (số ký tự)", minimum=0)

    filtered_chunks = [
        chunk
        for chunk in chunks
        if (selected_category is None or chunk["category"] == selected_category)
        and (selected_document is None or chunk["document_id"] == selected_document)
        and (selected_language is None or chunk["language"] == selected_language)
        and (page_range is None or page_range[0] <= chunk["page"] <= page_range[1])
        and (not keyword or keyword in chunk["text"].casefold())
        and (
            length_range is None
            or length_range[0] <= len(chunk["text"]) <= length_range[1]
        )
    ]

    print("\nTổng số đoạn văn bản B:", len(chunks))
    print("Số đoạn văn bản trong phạm vi đã chọn:", len(filtered_chunks))
    remaining_categories = sorted({
        CATEGORY_LABELS.get(chunk["category"], chunk["category"])
        for chunk in filtered_chunks
    })
    print("Nhóm còn lại:", ", ".join(remaining_categories) or "Không có")


if __name__ == "__main__":
    main()
