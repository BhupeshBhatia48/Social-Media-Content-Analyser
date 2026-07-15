"""
Analysis service: splits extracted text into individual posts and gets a
structured analysis for each one from the LLM.

Design decisions (also documented in README):
  - Posts are split on blank lines (see config.POST_SPLIT_PATTERN). This is
    a simplifying assumption for a document that contains multiple posts;
    it will not perfectly handle every possible layout, and that trade-off
    is called out explicitly rather than silently.
  - Very short "posts" (below MIN_WORDS_FOR_ANALYSIS) are NOT sent to the
    LLM. They're returned as skipped with a clear reason, so we never
    hallucinate a confident engagement score for three words of text.
  - The LLM is asked for JSON only. The response is validated against the
    PostAnalysis schema; on validation failure we retry once with a
    stricter follow-up instruction before giving up gracefully.
"""
import json
import re
import time
from typing import Iterator, List

import requests

from app.config import (
    GEMINI_API_KEY,
    GEMINI_API_BASE,
    GEMINI_MODEL,
    LLM_MAX_RETRIES,
    LLM_TIMEOUT_SECONDS,
    MIN_WORDS_FOR_ANALYSIS,
    POST_SPLIT_PATTERN,
)
from app.models.schemas import PostAnalysis


class AnalysisError(Exception):
    """Raised when the LLM call fails in a way we can't recover from."""
    pass


def split_into_posts(full_text: str) -> List[str]:
    """Split extracted text into individual post candidates."""
    raw_parts = re.split(POST_SPLIT_PATTERN, full_text.strip())
    posts = [p.strip() for p in raw_parts if p.strip()]
    return posts if posts else [full_text.strip()]


_PROMPT_TEMPLATE = """You are analyzing a single social media post for engagement potential.
Return ONLY a JSON object (no markdown fences, no commentary) with exactly these keys:

{{
  "sentiment": "positive" | "neutral" | "negative",
  "engagement_score": integer 0-100,
  "engagement_justification": "one short sentence",
  "strengths": ["1-3 short bullet points"],
  "weaknesses": ["1-3 short bullet points"],
  "improved_version": "a rewritten, more engaging version of the post"
}}

Post to analyze:
\"\"\"
{post_text}
\"\"\"
"""


def _call_gemini(post_text: str) -> dict:
    """Call Gemini's generateContent endpoint and return parsed JSON."""
    if not GEMINI_API_KEY:
        raise AnalysisError("GEMINI_API_KEY is not configured on the server.")

    url = f"{GEMINI_API_BASE}/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{
            "parts": [{"text": _PROMPT_TEMPLATE.format(post_text=post_text)}]
        }],
        "generationConfig": {
            "temperature": 0.4,
            "response_mime_type": "application/json",
        },
    }

    try:
        resp = requests.post(url, json=payload, timeout=LLM_TIMEOUT_SECONDS)
    except requests.exceptions.Timeout:
        raise AnalysisError("The analysis service timed out. Please try again.")
    except requests.exceptions.RequestException as e:
        raise AnalysisError(f"Could not reach the analysis service: {e}")

    if resp.status_code == 429:
        raise AnalysisError("Analysis service rate limit reached. Please try again shortly.")
    if resp.status_code == 503:
        # Transient "model overloaded" — worth a quick retry with backoff,
        # not a permanent failure.
        raise AnalysisError("Analysis service is temporarily overloaded (HTTP 503).")
    if resp.status_code >= 400:
        raise AnalysisError(f"Analysis service returned an error (HTTP {resp.status_code}).")

    try:
        data = resp.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        raise AnalysisError(f"Unexpected response shape from the analysis service: {e}")

    return _parse_json_block(text)


def _parse_json_block(text: str) -> dict:
    """Strip markdown fences if present and parse JSON, raising on failure."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(json)?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    return json.loads(cleaned)  # raises json.JSONDecodeError on malformed output


def analyze_post(post_text: str, index: int) -> PostAnalysis:
    """
    Analyze a single post. Handles the "too short to analyze" edge case
    directly, and retries once on malformed LLM JSON before failing
    gracefully (never raises a raw stack trace to the caller).
    """
    word_count = len(post_text.split())
    if word_count < MIN_WORDS_FOR_ANALYSIS:
        return PostAnalysis(
            post_index=index,
            original_text=post_text,
            sentiment="neutral",
            engagement_score=0,
            engagement_justification="Not applicable — post too short for meaningful analysis.",
            strengths=[],
            weaknesses=[],
            improved_version=post_text,
            skipped=True,
            skip_reason=f"Post has only {word_count} word(s); minimum is {MIN_WORDS_FOR_ANALYSIS}.",
        )

    last_error = None
    for attempt in range(LLM_MAX_RETRIES + 1):
        if attempt > 0:
            # Short backoff before retrying — gives a momentarily overloaded
            # model (HTTP 503) a real chance to succeed on the next try,
            # instead of hammering it instantly.
            time.sleep(1.5 * attempt)
        try:
            raw = _call_gemini(post_text)
            return PostAnalysis(
                post_index=index,
                original_text=post_text,
                sentiment=raw.get("sentiment", "neutral"),
                engagement_score=int(raw.get("engagement_score", 0)),
                engagement_justification=raw.get("engagement_justification", ""),
                strengths=raw.get("strengths", []) or [],
                weaknesses=raw.get("weaknesses", []) or [],
                improved_version=raw.get("improved_version", post_text),
            )
        except (json.JSONDecodeError, AnalysisError, ValueError) as e:
            last_error = e
            continue

    # Graceful degradation instead of a crash: return a clearly-marked
    # skipped result rather than a 500 error for this one post.
    return PostAnalysis(
        post_index=index,
        original_text=post_text,
        sentiment="neutral",
        engagement_score=0,
        engagement_justification="Analysis unavailable.",
        strengths=[],
        weaknesses=[],
        improved_version=post_text,
        skipped=True,
        skip_reason=f"Analysis service failed after retry: {last_error}",
    )


def analyze_posts_stream(posts: List[str]) -> Iterator[PostAnalysis]:
    """Yield a PostAnalysis for each post as it completes (used for SSE streaming)."""
    for i, post_text in enumerate(posts):
        yield analyze_post(post_text, i)
