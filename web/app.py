"""Storywizard web application — bookshelf and graphic novel reader."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from storywizard.models import GraphicNovel

WEB_DIR = Path(__file__).parent
STATIC_DIR = WEB_DIR / "static"
TEMPLATES_DIR = WEB_DIR / "templates"
OUTPUT_DIR = Path(__file__).parent.parent / "output"

app = FastAPI(title="Storywizard", description="AI Graphic Novel Library")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _discover_novels() -> list[dict]:
    """Scan the output directory for completed graphic novels."""
    novels = []
    if not OUTPUT_DIR.exists():
        return novels

    for novel_dir in sorted(OUTPUT_DIR.iterdir()):
        if not novel_dir.is_dir():
            continue
        metadata_path = novel_dir / "novel.json"
        if metadata_path.exists():
            data = json.loads(metadata_path.read_text())
            data["slug"] = novel_dir.name
            data["dir"] = str(novel_dir)
            novels.append(data)
    return novels


def _load_novel(slug: str) -> dict | None:
    """Load a graphic novel's full data by slug."""
    novel_dir = OUTPUT_DIR / slug
    metadata_path = novel_dir / "novel.json"
    if not metadata_path.exists():
        return None
    return json.loads(metadata_path.read_text())


@app.get("/", response_class=HTMLResponse)
async def bookshelf(request: Request):
    """Main bookshelf page showing all available graphic novels."""
    novels = _discover_novels()
    return templates.TemplateResponse(
        "bookshelf.html", {"request": request, "novels": novels}
    )


@app.get("/read/{slug}", response_class=HTMLResponse)
async def reader(request: Request, slug: str):
    """Kindle-like reader for a specific graphic novel."""
    novel = _load_novel(slug)
    if not novel:
        return HTMLResponse("<h1>Novel not found</h1>", status_code=404)
    return templates.TemplateResponse(
        "reader.html", {"request": request, "novel": novel, "slug": slug}
    )


@app.get("/api/novels")
async def api_novels():
    """API endpoint returning all available novels."""
    return _discover_novels()


@app.get("/api/novels/{slug}")
async def api_novel(slug: str):
    """API endpoint returning full novel data."""
    novel = _load_novel(slug)
    if not novel:
        return {"error": "not found"}
    return novel


@app.get("/covers/{slug}")
async def serve_cover(slug: str):
    """Serve book cover image."""
    path = OUTPUT_DIR / slug / "cover.png"
    if path.exists() and path.is_file():
        return FileResponse(path)
    return HTMLResponse("Not found", status_code=404)


@app.get("/character_refs/{slug}/{filename}")
async def serve_character_ref(slug: str, filename: str):
    """Serve character reference images from the output directory."""
    path = OUTPUT_DIR / slug / "character_refs" / filename
    if path.exists() and path.is_file():
        return FileResponse(path)
    return HTMLResponse("Not found", status_code=404)


@app.get("/panels/{slug}/{filename}")
async def serve_panel(slug: str, filename: str):
    """Serve panel images and prompts from the output directory."""
    path = OUTPUT_DIR / slug / "panels" / filename
    if path.exists() and path.is_file():
        return FileResponse(path)
    return HTMLResponse("Not found", status_code=404)
