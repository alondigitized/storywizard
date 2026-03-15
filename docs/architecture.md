# Storywizard Architecture

## System Overview

Storywizard is a multi-agent AI pipeline that converts public domain novels into illustrated graphic novels. It uses Claude AI for all text analysis/generation tasks and Flux (via fal.ai) for image generation.

```
Novel Text (from Gutenberg)
    ↓
[Story Analyst] → StoryAnalysis (characters, scenes, themes)
    ↓
[Curator] → CuratorStatement (why this book matters)
    ↓
[Production Designer] → VisualStyleGuide (art, colors, designs)
    ↓
[Script Writer] → PanelScript[] (scenes → panels)
    ↓
[Artist] → GeneratedPanel[] (images + prompts)
    ↓
[Critical Editor] → EditorialReview (score, approval)
    ↓ (if rejected, loops back — up to max_revision_rounds)
    ↓
[Focus Group] → FocusGroupFeedback[] (persona evaluations)
    ↓
[Assemble] → GraphicNovel
    ↓
[Renderer] → markdown + JSON files
    ↓
[Web Publisher] → novel.json (web-optimized)
    ↓
[Accessibility Reviewer] → WCAG compliance report
    ↓
Output Directory (web-ready graphic novel)
```

## Agent Architecture

All agents extend `BaseAgent` (`storywizard/agents/base.py`), which provides:

- `invoke(system_prompt, user_prompt)` — raw text response from Claude
- `invoke_structured(system_prompt, user_prompt, output_model)` — Pydantic-validated structured response

The base agent handles JSON schema generation and validation. Default model: `claude-sonnet-4-6`.

### Agent Details

| # | Agent | Input | Output | Purpose |
|---|-------|-------|--------|---------|
| 1 | **StoryAnalyst** | `source_text`, `StoryMetadata` | `StoryAnalysis` | Reads full novel, extracts scenes (up to `max_scenes`), characters, themes, narrative arc |
| 2 | **Curator** | `StoryAnalysis` | `CuratorStatement` | Writes `human_truth`, `historical_moment`, `living_relevance`, `invitation`, `one_line` — adapts to audience |
| 3 | **ProductionDesigner** | `StoryAnalysis` | `VisualStyleGuide` | Defines art style, color palette (5 colors with meaning), character designs, environment notes, typography, consistency rules |
| 4 | **ScriptWriter** | `scenes[]`, `characters[]`, `VisualStyleGuide` | `PanelScript[]` | Creates 3-6 panels per scene with `visual_direction`, `dialogue[]`, `narration`, `sound_effects[]`, `layout_notes` |
| 5 | **Artist** | `PanelScript[]`, `VisualStyleGuide`, output path | `GeneratedPanel[]` | Crafts image prompts incorporating style guide, then generates via mock or Flux backend |
| 6 | **CriticalEditor** | `StoryMetadata`, `VisualStyleGuide`, `PanelScript[]`, `GeneratedPanel[]` | `EditorialReview` | Scores 1-10 across visual consistency, narrative coherence, dialogue quality, pacing. Approves if ≥7 |
| 7 | **FocusGroup** | `StoryMetadata`, `VisualStyleGuide`, `PanelScript[]`, `EditorialReview` | `FocusGroupFeedback[]` | 3 personas: Reluctant Teen Reader (15yo), Visual Learner Adult (35yo), ESL Student (22yo) |
| 8 | **WebPublisher** | `GraphicNovel`, output path | `novel.json` | Adds web metadata: description, tags, accent color, cover background, reading time, SEO description |
| 9 | **AccessibilityReviewer** | `GraphicNovel` | JSON report | Checks alt text, reading order, color contrast, keyboard nav, screen reader support |

## Data Models

All defined in `storywizard/models.py` as Pydantic `BaseModel` classes:

```
StoryMetadata
  ├── title, author, gutenberg_id, genre, setting, time_period

StoryAnalysis
  ├── metadata: StoryMetadata
  ├── characters: Character[] (name, description, visual_traits, role)
  ├── scenes: Scene[] (scene_number, title, summary, characters, emotional_tone, key_dialogue, visual_description)
  ├── themes: str[]
  └── narrative_arc: str

CuratorStatement
  ├── human_truth, historical_moment, living_relevance
  ├── invitation, one_line, target_audience

VisualStyleGuide
  ├── art_style, color_palette[], mood
  ├── character_designs: CharacterDesign[]
  ├── environment_notes, typography_notes
  ├── consistency_rules[]
  └── full_style_document

PanelScript
  ├── scene_number, scene_title, layout_notes
  └── panels: Panel[] (panel_number, visual_direction, dialogue[], narration, sound_effects[])

GeneratedPanel
  ├── scene_number, panel_number
  ├── image_prompt, image_path, alt_text

EditorialReview
  ├── overall_score (1-10), approved
  ├── visual_consistency, narrative_coherence, dialogue_quality, pacing
  ├── issues[], suggestions[], summary

FocusGroupFeedback
  ├── persona_name, persona_description
  ├── accessibility_score, engagement_score
  ├── strengths[], concerns[], suggestions[]
  ├── would_read, summary

GraphicNovel (final assembly)
  ├── metadata, curator_statement, style_guide
  ├── panel_scripts[], generated_panels[]
  ├── editorial_review, focus_group_feedback[]
```

## Image Generation

Two backends in `storywizard/agents/artist.py`:

### Mock Backend (default)
- Saves image prompts as `panels/sceneNN_panelNN.prompt.txt`
- No API calls, free for testing

### Flux Backend (`--backend flux`)
- Uses fal.ai with `fal-client` SDK
- Default model: `fal-ai/flux/dev`
- Saves PNG images + `.prompt.txt` alongside
- Requires `FAL_KEY` environment variable
- Cost: ~$0.025 per image (~$1.50 for a full novel)

The Artist agent embeds style guide context into each image prompt to ensure visual consistency.

## Web Application

### Stack
- **Backend**: FastAPI + Jinja2
- **Frontend**: Vanilla HTML/CSS/JS (no framework)
- **Deployment**: Vercel (serverless via `api/index.py`)

### Routes

| Route | Description |
|-------|-------------|
| `GET /` | Bookshelf — library grid of all novels |
| `GET /read/{slug}` | Reader — Kindle-like reading interface |
| `GET /api/novels` | JSON list of all novels (metadata only) |
| `GET /api/novels/{slug}` | Full novel data |
| `GET /panels/{slug}/{filename}` | Serve panel images |

### Reader Features
- Page-by-page navigation (arrow keys, click, swipe)
- Table of contents sidebar
- Font size adjustment
- Light/dark theme toggle
- Full-screen mode
- Progress bar
- Reading preferences saved to localStorage

### Data Flow for Web
```
output/{slug}/novel.json → FastAPI → Jinja2 template → Reader UI
                                  → API endpoints → JSON responses
```

For Vercel deployment, novel data is copied to `data/` (committed to git) and served from there.

## Output Structure

Each pipeline run produces:

```
output/{slug}/
├── novel.json              # Complete structured data
├── graphic_novel.md        # Readable graphic novel document
├── style_guide.md          # Production design reference
├── editorial_review.md     # Editor's assessment
├── focus_group.md          # Persona feedback
├── accessibility_review.json
└── panels/
    ├── scene01_panel01.png (or .prompt.txt)
    ├── scene01_panel01.prompt.txt
    └── ...
```

## Configuration

`PipelineConfig` in `storywizard/config.py`:

| Setting | Default | Env Var |
|---------|---------|---------|
| `anthropic_api_key` | — | `ANTHROPIC_API_KEY` |
| `model_name` | `claude-sonnet-4-6` | — |
| `image_backend` | `mock` | — |
| `image_api_key` | — | `IMAGE_API_KEY` |
| `flux_model` | `fal-ai/flux/dev` | — |
| `flux_aspect_ratio` | `landscape_16_9` | — |
| `max_scenes` | 15 | — |
| `max_panels_per_scene` | 6 | — |
| `max_revision_rounds` | 2 | — |
| `output_dir` | `output` | — |
| `stories_dir` | `stories` | — |

## Ingestion

`storywizard/ingestion/gutenberg.py`:

- Fetches plain text from `https://www.gutenberg.org/cache/epub/{id}/pg{id}.txt`
- Strips boilerplate headers/footers
- Caches downloaded text in `stories/` directory
- Pre-curated candidate list with metadata for 5 classic novels
- Returns `(StoryMetadata, full_text)` tuple

## Testing

```bash
pytest tests/
```

Tests cover agent invocations, model validation, and pipeline integration.
