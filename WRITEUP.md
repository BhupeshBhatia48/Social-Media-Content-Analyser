# Approach Write-up (Deliverable 3)

I built this as a single FastAPI service that serves both the API and the
static frontend, rather than splitting frontend/backend into two deployed
services — fewer moving parts means fewer things that can break when tested
cold. Text extraction uses PyMuPDF per page; any page returning too little
text is treated as scanned content and rendered to an image for Tesseract
OCR, so one PDF can mix directly-extracted and OCR'd pages. Extracted text
is split into posts on blank lines, a documented simplifying assumption.
Each post goes to Gemini 2.5 Flash with a JSON-only prompt; the response is
validated against a Pydantic schema before reaching the frontend, with one
retry on malformed output and a clearly labeled "skipped" result if that
also fails, instead of a crash. Very short posts skip the LLM call entirely
to avoid hallucinated scores on near-empty input. Results stream to the
browser over Server-Sent Events as each post completes, and the UI shows
exactly which extraction path — direct text or OCR, with confidence — was
used per page. Known limitations (duplicate detection, OCR text cleanup,
document chunking) are documented rather than silently skipped.

(198 words)
