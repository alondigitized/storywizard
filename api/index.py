"""Vercel serverless entry point for the Storywizard web app."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from mangum import Mangum

# Paths — works both locally and on Vercel
ROOT_DIR = Path(__file__).parent.parent
WEB_DIR = ROOT_DIR / "web"
STATIC_DIR = WEB_DIR / "static"
TEMPLATES_DIR = WEB_DIR / "templates"
DATA_DIR = ROOT_DIR / "data"

app = FastAPI(title="Storywizard", description="AI Graphic Novel Library")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


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


# Mangum handler for Vercel serverless
handler = Mangum(app, lifespan="off")
