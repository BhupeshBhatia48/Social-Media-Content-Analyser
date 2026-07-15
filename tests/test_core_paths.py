"""
Focused test suite mapped 1:1 to the edge cases and behaviours the README
documents as "handled directly" — deliberately not a padded 25-test suite.

Run with: pytest -v
"""
import io
import json

import fitz  # PyMuPDF
import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from app.main import app
from app.services import analysis as analysis_module
from app.services.extraction import ExtractionError, extract_text
from app.services.analysis import analyze_post, split_into_posts

client = TestClient(app)


# ---------- helpers to build test fixtures on the fly ----------

def make_text_pdf(text: str) -> bytes:
    """A PDF with a real, directly-extractable text layer."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 100), text, fontsize=12)
    data = doc.tobytes()
    doc.close()
    return data


def make_image_bytes(text: str, size=(600, 200)) -> bytes:
    """A plain image with text drawn on it (for OCR)."""
    img = Image.new("RGB", size, color="white")
    draw = ImageDraw.Draw(img)
    draw.text((20, 80), text, fill="black")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def make_image_only_pdf(text: str) -> bytes:
    """A PDF with no text layer at all — just an embedded image (scanned-doc style)."""
    img_bytes = make_image_bytes(text)
    doc = fitz.open()
    page = doc.new_page()
    rect = fitz.Rect(0, 0, page.rect.width, page.rect.height)
    page.insert_image(rect, stream=img_bytes)
    data = doc.tobytes()
    doc.close()
    return data


def make_blank_pdf() -> bytes:
    doc = fitz.open()
    doc.new_page()
    data = doc.tobytes()
    doc.close()
    return data


def make_blank_image_bytes(size=(400, 200)) -> bytes:
    img = Image.new("RGB", size, color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ---------- 1. Valid text-based PDF extracts correctly ----------

def test_text_pdf_extracts_directly():
    pdf_bytes = make_text_pdf("This is a great launch announcement for our new product!")
    result = extract_text(pdf_bytes, "post.pdf", ".pdf")
    assert result.pages[0].method == "direct"
    assert "launch announcement" in result.full_text
    assert result.used_ocr is False


# ---------- 2. Image-only PDF triggers OCR and returns text ----------

def test_image_only_pdf_triggers_ocr():
    pdf_bytes = make_image_only_pdf("Check out our big sale today")
    result = extract_text(pdf_bytes, "scanned.pdf", ".pdf")
    assert result.used_ocr is True
    assert result.pages[0].method == "ocr"
    assert result.pages[0].ocr_confidence is not None
    # OCR isn't perfect, but it should pick up at least some of the wording
    assert len(result.full_text.strip()) > 0


# ---------- 3. Unsupported file type is rejected with the correct error ----------

def test_unsupported_file_type_rejected():
    response = client.post(
        "/api/analyze",
        files={"file": ("notes.txt", b"hello world", "text/plain")},
    )
    assert response.status_code == 400
    assert "unsupported" in response.json()["error"].lower()


# ---------- 4. Oversized file is rejected before processing ----------

def test_oversized_file_rejected(monkeypatch):
    monkeypatch.setattr("app.main.MAX_UPLOAD_SIZE_BYTES", 10)  # 10 bytes, easy to exceed
    big_content = b"%PDF-1.4 " + b"0" * 100
    response = client.post(
        "/api/analyze",
        files={"file": ("big.pdf", big_content, "application/pdf")},
    )
    assert response.status_code == 413
    assert "too large" in response.json()["error"].lower()


# ---------- 5. Blank/empty file returns a clear "no content" response ----------

def test_blank_pdf_raises_clean_error():
    pdf_bytes = make_blank_pdf()
    with pytest.raises(ExtractionError) as exc_info:
        extract_text(pdf_bytes, "blank.pdf", ".pdf")
    assert "no readable text" in str(exc_info.value).lower()


def test_blank_image_raises_clean_error():
    img_bytes = make_blank_image_bytes()
    with pytest.raises(ExtractionError):
        extract_text(img_bytes, "blank.png", ".png")


# ---------- 6. LLM call failure is caught and returns a graceful error, not a 500 ----------

def test_llm_failure_returns_skipped_result(monkeypatch):
    def broken_call(post_text):
        raise analysis_module.AnalysisError("Simulated network failure")

    monkeypatch.setattr(analysis_module, "_call_gemini", broken_call)

    result = analyze_post("A perfectly normal length post about our product launch", index=0)
    assert result.skipped is True
    assert "simulated network failure" in result.skip_reason.lower()


# ---------- 7. Structured output always matches the Pydantic schema ----------

def test_successful_analysis_matches_schema(monkeypatch):
    fake_response = {
        "sentiment": "positive",
        "engagement_score": 82,
        "engagement_justification": "Clear call to action and enthusiastic tone.",
        "strengths": ["Strong hook", "Clear CTA"],
        "weaknesses": ["No hashtags"],
        "improved_version": "An even more engaging version of the post!",
    }
    monkeypatch.setattr(analysis_module, "_call_gemini", lambda post_text: fake_response)

    result = analyze_post("Excited to launch our new feature today!", index=2)
    assert result.post_index == 2
    assert result.sentiment == "positive"
    assert 0 <= result.engagement_score <= 100
    assert isinstance(result.strengths, list)
    assert result.skipped is False


# ---------- 8. Multi-post document is split into the expected number of posts ----------

def test_post_splitting_on_blank_lines():
    text = "First post about our launch.\n\nSecond post with different content.\n\nThird one here."
    posts = split_into_posts(text)
    assert len(posts) == 3
    assert posts[0].startswith("First post")
    assert posts[2].startswith("Third one")


# ---------- 9. Mixed PDF (text + scanned pages) merges both extraction paths ----------

def test_mixed_pdf_merges_direct_and_ocr_pages():
    doc = fitz.open()

    text_page = doc.new_page()
    text_page.insert_text((72, 100), "Directly extractable page content here.", fontsize=12)

    image_page = doc.new_page()
    img_bytes = make_image_bytes("Scanned page content")
    rect = fitz.Rect(0, 0, image_page.rect.width, image_page.rect.height)
    image_page.insert_image(rect, stream=img_bytes)

    pdf_bytes = doc.tobytes()
    doc.close()

    result = extract_text(pdf_bytes, "mixed.pdf", ".pdf")
    methods = [p.method for p in result.pages]
    assert "direct" in methods
    assert "ocr" in methods
    assert result.used_ocr is True


# ---------- 10. End-to-end: upload -> response contains all expected analysis fields ----------

def test_end_to_end_stream_contains_expected_events(monkeypatch):
    fake_response = {
        "sentiment": "neutral",
        "engagement_score": 55,
        "engagement_justification": "Decent but generic.",
        "strengths": ["Readable"],
        "weaknesses": ["Could use a hook"],
        "improved_version": "A punchier rewrite of the same post.",
    }
    monkeypatch.setattr(analysis_module, "_call_gemini", lambda post_text: fake_response)

    pdf_bytes = make_text_pdf("Our weekly update: things are going well for the team.")

    response = client.post(
        "/api/analyze",
        files={"file": ("update.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 200

    body = response.text
    assert "event: extraction" in body
    assert "event: post" in body
    assert "event: done" in body
    assert '"sentiment": "neutral"' in body or "neutral" in body
