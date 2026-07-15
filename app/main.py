"""
FastAPI application entry point.

Single-service design (see strategy docs): this app both serves the API
and the static frontend, so there is exactly one thing to deploy and one
thing that can go down — deliberately chosen over a two-service split to
minimize risk for a time-boxed submission.
"""
import json
import os
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE_BYTES, MAX_UPLOAD_SIZE_MB
from app.models.schemas import ErrorResponse
from app.services.analysis import analyze_post, split_into_posts
from app.services.extraction import ExtractionError, extract_text

APP_DIR = Path(__file__).parent
STATIC_DIR = APP_DIR / "static"

app = FastAPI(
    title="Social Media Content Analyzer",
    description="Upload a PDF or image of social media posts and get structured, "
                 "actionable engagement analysis for each post.",
    version="1.0.0",
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


def _validate_upload(filename: str, content: bytes) -> str:
    """Shared validation for both endpoints. Returns the lowercase extension."""
    if not filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{extension}'. Allowed types: "
                   f"{', '.join(sorted(ALLOWED_EXTENSIONS))}.",
        )

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(content) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File is too large. Maximum allowed size is {MAX_UPLOAD_SIZE_MB} MB.",
        )

    return extension


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    """
    Streams results over Server-Sent Events as each stage completes:
      event: extraction   -> extraction metadata (pages, OCR usage) as soon as it's ready
      event: post         -> one fully-analyzed post at a time
      event: done         -> final summary
      event: error        -> a clean, human-readable error (never a raw stack trace)
    Streaming means the user sees progress immediately instead of staring
    at a spinner until the entire document has been processed.
    """
    content = await file.read()

    try:
        extension = _validate_upload(file.filename, content)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"error": e.detail})

    def event_stream():
        def sse(event: str, data: dict) -> str:
            return f"event: {event}\ndata: {json.dumps(data)}\n\n"

        try:
            extraction_result = extract_text(content, file.filename, extension)
        except ExtractionError as e:
            yield sse("error", {"error": str(e)})
            return
        except Exception as e:
            # Catch-all so an unexpected failure still reaches the client
            # as a clean message instead of killing the connection.
            yield sse("error", {"error": f"Unexpected extraction failure: {e}"})
            return

        yield sse("extraction", {
            "filename": extraction_result.filename,
            "used_ocr": extraction_result.used_ocr,
            "pages": [p.model_dump() for p in extraction_result.pages],
        })

        posts = split_into_posts(extraction_result.full_text)

        yield sse("post_count", {"count": len(posts)})

        for i, post_text in enumerate(posts):
            try:
                result = analyze_post(post_text, i)
                yield sse("post", result.model_dump())
            except Exception as e:
                # Never let one post's unexpected failure kill the whole stream.
                yield sse("post", {
                    "post_index": i,
                    "original_text": post_text,
                    "sentiment": "neutral",
                    "engagement_score": 0,
                    "engagement_justification": "Analysis unavailable.",
                    "strengths": [],
                    "weaknesses": [],
                    "improved_version": post_text,
                    "skipped": True,
                    "skip_reason": f"Unexpected error: {e}",
                })

        yield sse("done", {"post_count": len(posts)})

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# Serve the frontend last so /api/* routes above take priority.
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
