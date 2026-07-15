"""
Pydantic models used across the API. Keeping these in one place means the
LLM's output always gets coerced into a validated shape before it ever
reaches the frontend — the frontend never sees raw/untrusted LLM text.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class PageExtractionInfo(BaseModel):
    """Metadata about how a single page's text was obtained."""
    page_number: int
    method: str  # "direct" | "ocr"
    ocr_confidence: Optional[float] = None  # 0-100, only set when method == "ocr"
    char_count: int


class ExtractionResult(BaseModel):
    """Result of the extraction stage, before any post-splitting/analysis."""
    filename: str
    pages: List[PageExtractionInfo]
    full_text: str
    used_ocr: bool


class PostAnalysis(BaseModel):
    """
    Structured analysis for a single social media post.
    This is the schema the LLM's JSON response is validated against.
    """
    post_index: int
    original_text: str
    sentiment: str = Field(description="positive | neutral | negative")
    engagement_score: int = Field(ge=0, le=100)
    engagement_justification: str
    strengths: List[str]
    weaknesses: List[str]
    improved_version: str
    skipped: bool = False
    skip_reason: Optional[str] = None


class AnalyzeResponse(BaseModel):
    """Full response returned once all posts have been analyzed."""
    filename: str
    used_ocr: bool
    pages: List[PageExtractionInfo]
    post_count: int
    posts: List[PostAnalysis]


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
