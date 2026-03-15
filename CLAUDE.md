# Storywizard

AI publishing pipeline that transforms public domain novels into illustrated graphic novels using Claude AI agents and Flux image generation.

## Quick Start

```bash
pip install -e .

# Requires Claude CLI (claude) installed and authenticated
# For real image generation (optional)
export FAL_KEY="your-fal-key"

# Run pipeline (mock images by default)
python run.py 43                        # Jekyll & Hyde
python run.py 84 --backend flux         # Frankenstein with real images

# Web reader
python -m web.serve                     # http://localhost:8000
```

## Project Structure

```
storywizard/
├── agents/          # 8 Claude agents (analyst, curator, designer, writer, artist, editor, focus group, publisher)
├── ingestion/       # Gutenberg book fetcher with caching
├── output/          # Markdown + JSON renderer
├── config.py        # PipelineConfig (env-aware settings)
├── models.py        # Pydantic models for the full data pipeline
├── pipeline.py      # Orchestrator running all 9 stages
web/
├── app.py           # FastAPI app (bookshelf + reader routes)
├── templates/       # Jinja2 (bookshelf.html, reader.html)
├── static/          # CSS, JS (Kindle-like reader)
├── create_demo.py   # Generate demo data without API keys
data/                # Vercel-deployed novel data
run.py               # CLI entry point with argparse
```

## Pipeline Stages

1. **Story Analyst** — extracts scenes, characters, themes from full novel text
2. **Curator** — writes compelling "why this book matters" statement
3. **Production Designer** — creates visual style guide (art style, colors, character designs)
4. **Script Writer** — converts scenes to 3-6 panel scripts with dialogue/narration
5. **Artist** — generates image prompts and renders via mock or Flux backend
6. **Critical Editor** — quality gate (score ≥7 to approve, else revision loop)
7. **Focus Group** — evaluates from 3 reader personas (teen, adult, ESL)
8. **Web Publisher** — prepares novel.json with web metadata
9. **Accessibility Reviewer** — WCAG compliance check

## Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `FAL_KEY` | For `--backend flux` | fal.ai Flux image generation |
| `IMAGE_API_KEY` | No | Legacy alias for image API key |

**Note:** Agents invoke Claude via the local `claude` CLI (no API key needed). Ensure `claude` is installed and authenticated.

## CLI Options

```
python run.py [BOOK_ID] [OPTIONS]

  BOOK_ID              Gutenberg ID (default: 43 = Jekyll & Hyde)
  --backend mock|flux  Image backend (default: mock)
  --max-scenes N       Max scenes to extract (default: 15)
  --flux-model ID      fal.ai model (default: fal-ai/flux/dev)
  --flux-aspect RATIO  Aspect ratio (default: landscape_16_9)
```

## Candidate Books

| ID | Title |
|----|-------|
| 43 | The Strange Case of Dr. Jekyll and Mr. Hyde |
| 84 | Frankenstein |
| 11 | Alice's Adventures in Wonderland |
| 46 | A Christmas Carol |
| 174 | The Picture of Dorian Gray |
| 77416 | Romance of the Three Kingdoms (Vol. 1) |

## Key Conventions

- All agent outputs use Pydantic models (see `models.py`)
- Pipeline config is a dataclass in `config.py` — reads from env vars
- Image backend is pluggable: `mock` saves `.prompt.txt`, `flux` generates PNGs
- Web reader loads from `novel.json` in each output subdirectory
- Demo data can be regenerated with `python web/create_demo.py`
- Tests: `pytest tests/`
