"""Vercel serverless entry point for the Storywizard web app.

Vercel's @vercel/python runtime expects either:
- A WSGI app named `app`, or
- A handler function

We use the FastAPI ASGI app directly — Vercel handles the ASGI adapter.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from fastapi.templating import Jinja2Templates

# On Vercel, the function runs from /var/task/api/
# The repo root is one level up from this file's directory
ROOT_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT_DIR / "web"
TEMPLATES_DIR = WEB_DIR / "templates"
STATIC_DIR = WEB_DIR / "static"
DATA_DIR = ROOT_DIR / "data"

app = FastAPI(title="Storywizard", description="AI Graphic Novel Library")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Mime types for static files
MIME_TYPES = {
    ".css": "text/css",
    ".js": "application/javascript",
    ".html": "text/html",
    ".json": "application/json",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".txt": "text/plain",
}


def _discover_novels() -> list[dict]:
    """Load all graphic novels from the bundled data directory."""
    novels = []
    if not DATA_DIR.exists():
        return novels
    for novel_dir in sorted(DATA_DIR.iterdir()):
        if not novel_dir.is_dir():
            continue
        json_path = novel_dir / "novel.json"
        if json_path.exists():
            data = json.loads(json_path.read_text())
            data["slug"] = novel_dir.name
            novels.append(data)
    return novels


def _load_novel(slug: str) -> dict | None:
    """Load a single novel by slug."""
    json_path = DATA_DIR / slug / "novel.json"
    if not json_path.exists():
        return None
    data = json.loads(json_path.read_text())
    data["slug"] = slug
    return data


@app.get("/", response_class=HTMLResponse)
async def bookshelf(request: Request):
    novels = _discover_novels()
    return templates.TemplateResponse(
        "bookshelf.html", {"request": request, "novels": novels}
    )


@app.get("/static/{file_path:path}")
async def serve_static(file_path: str):
    """Serve static files (CSS, JS, images)."""
    full_path = STATIC_DIR / file_path
    if not full_path.exists() or not full_path.is_file():
        return HTMLResponse("Not found", status_code=404)
    suffix = full_path.suffix.lower()
    content_type = MIME_TYPES.get(suffix, "application/octet-stream")
    return Response(
        content=full_path.read_bytes(),
        media_type=content_type,
    )


@app.get("/read/{slug}", response_class=HTMLResponse)
async def reader(request: Request, slug: str):
    novel = _load_novel(slug)
    if not novel:
        return HTMLResponse("<h1>Novel not found</h1>", status_code=404)
    return templates.TemplateResponse(
        "reader.html", {"request": request, "novel": novel, "slug": slug}
    )


@app.get("/api/novels")
async def api_novels():
    return _discover_novels()


@app.get("/api/novels/{slug}")
async def api_novel(slug: str):
    novel = _load_novel(slug)
    if not novel:
        return {"error": "not found"}
    return novel


@app.get("/panels/{slug}/{filename}")
async def serve_panel(slug: str, filename: str):
    path = DATA_DIR / slug / "panels" / filename
    if path.exists():
        return PlainTextResponse(path.read_text())
    return HTMLResponse("Not found", status_code=404)


@app.get("/debug")
async def debug():
    """Debug endpoint to diagnose path issues on Vercel."""
    return {
        "root_dir": str(ROOT_DIR),
        "web_dir_exists": WEB_DIR.exists(),
        "templates_dir_exists": TEMPLATES_DIR.exists(),
        "static_dir_exists": STATIC_DIR.exists(),
        "data_dir_exists": DATA_DIR.exists(),
        "data_contents": [str(p.name) for p in DATA_DIR.iterdir()] if DATA_DIR.exists() else [],
        "templates_contents": [str(p.name) for p in TEMPLATES_DIR.iterdir()] if TEMPLATES_DIR.exists() else [],
        "cwd": os.getcwd(),
        "file_location": str(Path(__file__).resolve()),
    }
