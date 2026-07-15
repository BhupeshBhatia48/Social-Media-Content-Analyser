"""
Centralized configuration. All tunable limits live here so behaviour
(size limits, OCR thresholds, model name) can be changed in one place
without hunting through services.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

# --- Upload limits ---
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "15"))
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}

# --- Extraction ---
# If a PDF page yields fewer than this many characters via direct text
# extraction, we treat it as an image-only/scanned page and fall back to OCR.
MIN_CHARS_FOR_DIRECT_EXTRACTION = 20

# --- Post splitting ---
# Documented assumption: posts are separated by a blank line (double newline)
# in the extracted text. This is a simplifying assumption for take-home
# scope — see README "Assumptions" section.
POST_SPLIT_PATTERN = r"\n\s*\n+"

# A "post" shorter than this many words is treated as too short for
# meaningful LLM analysis and is skipped with a clear reason instead of
# sending it to the LLM (avoids hallucinated scores on near-empty input).
MIN_WORDS_FOR_ANALYSIS = 3

# --- LLM request behaviour ---
LLM_TIMEOUT_SECONDS = 20
LLM_MAX_RETRIES = 2  # retries on malformed JSON / transient failures like HTTP 503
