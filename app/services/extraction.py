"""
Extraction service: turns an uploaded PDF or image into plain text.

Strategy (documented in README too):
  - PDFs: try PyMuPDF's direct text extraction per page first (fast, exact).
  - Any page that yields too little text (below MIN_CHARS_FOR_DIRECT_EXTRACTION)
    is assumed to be a scanned/image page and is rendered to an image and
    run through Tesseract OCR instead. This means a single PDF can mix
    directly-extracted and OCR'd pages ("mixed PDF" edge case).
  - Plain images (png/jpg/webp) always go straight to OCR.

Every page's extraction method and (for OCR) confidence is tracked so the
frontend can show the user exactly what happened, per the
"extraction path transparency" differentiator.
"""
import io
from typing import List, Tuple

import fitz  # PyMuPDF
import pytesseract
from PIL import Image

from app.config import MIN_CHARS_FOR_DIRECT_EXTRACTION
from app.models.schemas import ExtractionResult, PageExtractionInfo


class ExtractionError(Exception):
    """Raised for extraction failures that should surface as clean 4xx errors."""
    pass


def _ocr_image(image: Image.Image) -> Tuple[str, float]:
    """Run Tesseract on a PIL image, return (text, average_confidence)."""
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    text = pytesseract.image_to_string(image)

    confidences = [int(c) for c in data.get("conf", []) if str(c).isdigit() and int(c) >= 0]
    avg_conf = (sum(confidences) / len(confidences)) if confidences else 0.0
    return text.strip(), round(avg_conf, 1)


def _extract_pdf(file_bytes: bytes, filename: str) -> ExtractionResult:
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        raise ExtractionError(f"Could not open PDF — the file may be corrupted: {e}")

    if doc.page_count == 0:
        raise ExtractionError("PDF has no pages.")

    pages: List[PageExtractionInfo] = []
    full_text_parts: List[str] = []
    used_ocr = False

    for i, page in enumerate(doc):
        direct_text = page.get_text().strip()

        if len(direct_text) >= MIN_CHARS_FOR_DIRECT_EXTRACTION:
            pages.append(PageExtractionInfo(
                page_number=i + 1,
                method="direct",
                char_count=len(direct_text),
            ))
            full_text_parts.append(direct_text)
        else:
            # Treat as scanned/image-only page — render and OCR it.
            used_ocr = True
            pix = page.get_pixmap(dpi=200)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            ocr_text, confidence = _ocr_image(img)

            pages.append(PageExtractionInfo(
                page_number=i + 1,
                method="ocr",
                ocr_confidence=confidence,
                char_count=len(ocr_text),
            ))
            full_text_parts.append(ocr_text)

    doc.close()
    full_text = "\n\n".join(part for part in full_text_parts if part)

    return ExtractionResult(
        filename=filename,
        pages=pages,
        full_text=full_text,
        used_ocr=used_ocr,
    )


def _extract_image(file_bytes: bytes, filename: str) -> ExtractionResult:
    try:
        img = Image.open(io.BytesIO(file_bytes))
        img.load()
    except Exception as e:
        raise ExtractionError(f"Could not open image — the file may be corrupted or unsupported: {e}")

    ocr_text, confidence = _ocr_image(img)

    page_info = PageExtractionInfo(
        page_number=1,
        method="ocr",
        ocr_confidence=confidence,
        char_count=len(ocr_text),
    )

    return ExtractionResult(
        filename=filename,
        pages=[page_info],
        full_text=ocr_text,
        used_ocr=True,
    )


def extract_text(file_bytes: bytes, filename: str, extension: str) -> ExtractionResult:
    """
    Main entry point. Dispatches to PDF or image extraction based on extension.
    Raises ExtractionError for anything that should be surfaced as a clean
    error to the client rather than a stack trace.
    """
    if not file_bytes:
        raise ExtractionError("Uploaded file is empty.")

    if extension == ".pdf":
        result = _extract_pdf(file_bytes, filename)
    elif extension in (".png", ".jpg", ".jpeg", ".webp"):
        result = _extract_image(file_bytes, filename)
    else:
        raise ExtractionError(f"Unsupported file type: {extension}")

    if not result.full_text.strip():
        raise ExtractionError(
            "No readable text could be extracted from this file, even after OCR. "
            "The file may be blank, too low-resolution, or contain no text."
        )

    return result
