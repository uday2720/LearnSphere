from pathlib import Path
import fitz


def extract_pdf(pdf_path: str):
    """
    Returns:
        {
            "name": str,
            "page_count": int,
            "pages": list[tuple[int, str]]
        }
    """
    path = Path(pdf_path)
    doc = fitz.open(pdf_path)

    pages = []
    for index, page in enumerate(doc):
        text = page.get_text("text").strip()
        if text:
            pages.append((index + 1, text))

    result = {
        "name": path.name,
        "page_count": len(doc),
        "pages": pages,
    }
    doc.close()
    return result
