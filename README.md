# Social Media Content Analyzer

Upload a PDF or image of social media posts. The app extracts the text (with
automatic OCR fallback for scanned pages), splits it into individual posts,
and returns a structured, actionable analysis for each one — sentiment,
an engagement score, strengths, weaknesses, and a rewritten, more engaging
version — streamed to the browser as each post finishes.

**Live app:** _add your deployed URL here_
**Repo:** _add your GitHub link here_

---

## Approach (~200 words)

I built this as a single FastAPI service that both serves the API and a built React frontend, rather than splitting frontend/backend into two deployed services — fewer moving parts means fewer things that can break when an evaluator tests it cold. Text extraction uses PyMuPDF first, per page; any page that returns too little text is treated as scanned/image content and is rendered to an image and run through Tesseract OCR instead, so a single PDF can mix directly-extracted and OCR'd pages. Extracted text is split into individual posts on blank lines — a documented, simplifying assumption (see below). Each post is sent to Gemini 2.5 Flash with a prompt requesting JSON only; the response is validated against a Pydantic schema before it ever reaches the frontend, with retries on malformed output or transient failures (e.g. HTTP 503) and a clearly labeled "skipped" result if that also fails, instead of a crash. Very short posts are skipped before calling the LLM at all, to avoid hallucinated scores on near-empty input. Results stream to the browser over Server-Sent Events as each post completes. The frontend is a React + Tailwind app with an animated score indicator, an overall verdict summary, and an expandable word-level diff showing exactly what changed between the original and improved post.

---

## Setup

### Backend

```bash
git clone <this-repo>
cd <this-repo>
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# System dependency: Tesseract OCR (not installable via pip)
# macOS:   brew install tesseract
# Ubuntu:  sudo apt-get install tesseract-ocr
# Windows: https://github.com/UB-Mannheim/tesseract/wiki

cp .env.example .env
# then edit .env and set GEMINI_API_KEY (free tier: https://aistudio.google.com/apikey)
```

### Frontend

The production build is already committed under `app/static/`, so you can
run the backend alone (below) and it'll serve the pre-built UI. If you want
to modify the frontend, rebuild it after making changes:

```bash
cd frontend
npm install
npm run build          # outputs to frontend/dist/
cp -r dist/* ../app/static/
cd ..
```

For active frontend development with hot reload:

```bash
cd frontend
npm install
npm run dev             # runs on http://localhost:5173, proxies /api to :8000
```
Run the backend (`uvicorn app.main:app --reload`) in another terminal at the
same time — Vite's dev server proxies `/api/*` requests to it automatically
(see `frontend/vite.config.js`).

### Running the backend

```bash
uvicorn app.main:app --reload
```

Then open `http://localhost:8000`.

### Running tests

```bash
pytest -v
```

### Docker (recommended for deployment)

```bash
docker build -t sm-analyzer .
docker run -p 8000:8000 --env-file .env sm-analyzer
```

A `Dockerfile` is included with a multi-stage build: the first stage builds
the React frontend with Node, the second stage installs Python dependencies
and Tesseract and copies the built frontend into `app/static/`. This is the
most reliable deployment path since some native buildpack environments
don't reliably support `apt-get` in the build step. `render.yaml` is
included as a reference for a native Python deploy (it builds the frontend
as part of its build command too), but the Dockerfile is the more
dependable path.

---

## Environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | Yes | — | Gemini API key (free tier) |
| `GEMINI_MODEL` | No | `gemini-2.5-flash` | Model used for analysis |
| `MAX_UPLOAD_SIZE_MB` | No | `15` | Max accepted upload size |

---

## API

### `POST /api/analyze`
Multipart form upload, field name `file`. Accepts `.pdf`, `.png`, `.jpg`,
`.jpeg`, `.webp`.

Returns `text/event-stream`. Events, in order:

| Event | Payload |
|---|---|
| `extraction` | `{ filename, used_ocr, pages: [{page_number, method, ocr_confidence, char_count}] }` |
| `post_count` | `{ count }` |
| `post` | One `PostAnalysis` object per completed post (see `app/models/schemas.py`) |
| `done` | `{ post_count }` |
| `error` | `{ error }` — sent instead of the above if extraction fails |

### `GET /api/health`
Returns `{"status": "ok"}`. Used for uptime checks.

---

## Design decisions & assumptions

- **Post splitting** assumes posts in a document are separated by a blank
  line. This is a simplifying assumption for take-home scope — it won't
  perfectly handle every possible document layout (e.g., posts separated
  only by a change in font/heading), but it's simple, predictable, and
  correct for the common case of one-post-per-paragraph test documents.
- **OCR fallback threshold**: a PDF page is sent to OCR if PyMuPDF's direct
  text extraction yields fewer than 20 characters. This threshold is
  configurable in `app/config.py`.
- **Short posts (< 3 words)** are not sent to the LLM at all — they're
  returned as `skipped` with a reason. This avoids the LLM confidently
  scoring three words of text as if it were a real post.
- **Single-service deployment** was chosen over separate frontend/backend
  deploys specifically to reduce the number of things that can independently
  break (CORS config, two cold starts, two sets of env vars) during
  evaluation.

## Known limitations

The following edge cases are deliberately **not** fully implemented, in
favor of getting the core pipeline genuinely solid. They're called out here
rather than silently dropped:

- **Duplicate uploads** are not detected or deduplicated.
- **Unicode/emoji-heavy posts** are passed through as-is; they aren't
  specially normalized, and very unusual Unicode could occasionally affect
  post-splitting.
- **Malformed OCR output** (e.g., OCR mis-reading distorted or low-res
  scans) is passed to the LLM as-is; there's no post-OCR text cleanup pass.
- **Extremely long documents** are not chunked — a very large multi-post
  PDF is split into as many posts as blank lines produce, and each is
  analyzed individually, but there's no cap on total post count per request.
- **Multiple posts with ambiguous boundaries** (no blank line between them)
  will be treated as a single post.

## What I'd do with more time

- Chunk/paginate very long documents and cap concurrent LLM calls.
- Add a lightweight OCR text cleanup pass (common OCR misreads) before
  sending text to the LLM.
- Deduplicate identical uploads by content hash.
- Token-level streaming of the LLM's own output, rather than per-post
  streaming, for even faster perceived responsiveness.

## Screenshots

_Add 2-3 screenshots here after deploying: the upload screen, the
extraction-path badges, and a fully analyzed post card._
