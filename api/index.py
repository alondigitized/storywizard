"""Vercel serverless entry point for the Storywizard web app."""

from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from fastapi.templating import Jinja2Templates

# On Vercel, the function runs from /var/task/
# Resolve paths relative to this file
ROOT_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT_DIR / "web"
TEMPLATES_DIR = WEB_DIR / "templates"
STATIC_DIR = WEB_DIR / "static"
DATA_DIR = ROOT_DIR / "output"

app = FastAPI(title="Storywizard", description="AI Graphic Novel Library")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

MIME_TYPES = {
    ".css": "text/css",
    ".js": "application/javascript",
    ".html": "text/html",
    ".json": "application/json",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".svg": "image/svg+xml",
    ".txt": "text/plain",
}


def _discover_novels() -> list[dict]:
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
    json_path = DATA_DIR / slug / "novel.json"
    if not json_path.exists():
        return None
    data = json.loads(json_path.read_text())
    data["slug"] = slug
    return data


# --- Debug (remove after deploy works) ---

@app.get("/api/index")
async def vercel_root(request: Request):
    """Vercel may route here directly — redirect to real root."""
    return await bookshelf(request)


@app.get("/debug")
async def debug(request: Request):
    return {
        "path": request.scope.get("path"),
        "raw_path": request.scope.get("raw_path", b"").decode(),
        "root_path": request.scope.get("root_path", ""),
        "url": str(request.url),
        "root_dir": str(ROOT_DIR),
        "web_dir_exists": WEB_DIR.exists(),
        "templates_dir_exists": TEMPLATES_DIR.exists(),
        "static_dir_exists": STATIC_DIR.exists(),
        "data_dir_exists": DATA_DIR.exists(),
        "data_contents": [p.name for p in DATA_DIR.iterdir()] if DATA_DIR.exists() else [],
        "cwd": os.getcwd(),
        "file_location": str(Path(__file__).resolve()),
    }


# --- Main routes ---

@app.get("/", response_class=HTMLResponse)
async def bookshelf(request: Request):
    novels = _discover_novels()
    return templates.TemplateResponse(
        "bookshelf.html", {"request": request, "novels": novels}
    )


@app.get("/static/{file_path:path}")
async def serve_static(file_path: str):
    full_path = STATIC_DIR / file_path
    if not full_path.exists() or not full_path.is_file():
        return HTMLResponse("Not found", status_code=404)
    suffix = full_path.suffix.lower()
    content_type = MIME_TYPES.get(suffix, "application/octet-stream")
    return Response(content=full_path.read_bytes(), media_type=content_type)


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


@app.get("/covers/{slug}")
async def serve_cover(slug: str):
    path = DATA_DIR / slug / "cover.png"
    if not path.exists() or not path.is_file():
        return HTMLResponse("Not found", status_code=404)
    return Response(content=path.read_bytes(), media_type="image/png")


@app.get("/panels/{slug}/{filename}")
async def serve_panel(slug: str, filename: str):
    path = DATA_DIR / slug / "panels" / filename
    if not path.exists() or not path.is_file():
        return HTMLResponse("Not found", status_code=404)
    suffix = path.suffix.lower()
    content_type = MIME_TYPES.get(suffix, "application/octet-stream")
    return Response(content=path.read_bytes(), media_type=content_type)
