#!/usr/bin/env python3
"""Enrich panel narration and dialogue using the original novel text.

Takes existing panel scripts (which have sparse narration/dialogue) and
uses Claude to expand them with substantial prose from the source novel.
Preserves visual_direction unchanged. Updates novel.json in place.

Usage:
    python3 enrich_panels.py --slug frankenstein
"""

import argparse
import json
import logging
from pathlib import Path

from storywizard.agents.base import BaseAgent
from storywizard.config import PipelineConfig
from storywizard.models import PanelScript

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("enrich_panels")

GUTENBERG_IDS = {
    "frankenstein": 84,
    "the-strange-case-of-dr.-jekyll-and-m": 43,
    "romance-of-the-three-kingdoms": 77416,
    "peter-pan": 16,
}


class NarrationEnricher(BaseAgent):
    """Enriches panel narration and dialogue from the source novel."""

    name = "Narration Enricher"
    system_prompt = (
        "You are a literary adapter who enriches graphic novel panel scripts "
        "with substantial narration and dialogue drawn from the original novel. "
        "Your goal is to ensure each panel carries enough text for the reader "
        "to follow the story with full emotional fidelity.\n\n"
        "Guidelines:\n"
        "- NARRATION should be rich, atmospheric prose — 2-4 sentences per panel. "
        "Draw from the novel's own language: its imagery, its rhythm, its voice. "
        "Paraphrase and adapt rather than copy verbatim, but preserve the author's tone.\n"
        "- DIALOGUE should be substantial — include the key exchanges that drive "
        "the scene. Use the novel's actual dialogue where possible, adapted for "
        "natural speech. Multiple lines of dialogue per panel are encouraged.\n"
        "- Every panel MUST have narration. No panel should be text-less.\n"
        "- The narration should bridge panels so the story flows continuously.\n"
        "- Preserve the emotional arc of the scene across its panels.\n"
        "- Do NOT modify visual_direction or sound_effects — only narration and dialogue.\n"
        "- Return valid JSON matching the exact PanelScript structure."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich panel text from source novel")
    parser.add_argument("--slug", required=True, help="Novel slug under output/")
    args = parser.parse_args()

    slug = args.slug
    output_dir = Path("output") / slug
    novel_path = output_dir / "novel.json"

    # Load novel.json
    logger.info("Loading %s", novel_path)
    data = json.loads(novel_path.read_text())
    scripts = [PanelScript(**s) for s in data["panel_scripts"]]

    # Load original novel text
    gutenberg_id = GUTENBERG_IDS.get(slug)
    if not gutenberg_id:
        logger.error("Unknown slug: %s. Add its Gutenberg ID to GUTENBERG_IDS.", slug)
        return
    novel_text_path = Path("stories") / f"gutenberg_{gutenberg_id}.txt"
    if not novel_text_path.exists():
        logger.error("Novel text not found: %s", novel_text_path)
        return
    novel_text = novel_text_path.read_text(encoding="utf-8")
    logger.info("Loaded source novel: %d chars", len(novel_text))

    # We'll send Claude chunks of the novel relevant to each scene
    # The novel is ~450K chars, too large for a single prompt. We'll
    # include a 10K-char excerpt around keywords from each scene.
    config = PipelineConfig()
    enricher = NarrationEnricher(config)

    enriched_scripts = []
    for i, script in enumerate(scripts):
        logger.info(
            "Enriching scene %d/%d: %s (%d panels)",
            i + 1, len(scripts), script.scene_title, len(script.panels),
        )

        # Find relevant excerpt from the novel
        excerpt = _find_relevant_excerpt(novel_text, script, max_chars=12000)

        # Build the enrichment prompt
        current_json = script.model_dump()
        prompt = (
            f"Enrich the narration and dialogue for this graphic novel scene. "
            f"The current panel scripts are too sparse — readers cannot follow "
            f"the story from the brief text alone.\n\n"
            f"SCENE: {script.scene_title}\n\n"
            f"RELEVANT EXCERPT FROM THE ORIGINAL NOVEL:\n"
            f"---\n{excerpt}\n---\n\n"
            f"CURRENT PANEL SCRIPT (needs richer narration/dialogue):\n"
            f"```json\n{json.dumps(current_json, indent=2)}\n```\n\n"
            f"INSTRUCTIONS:\n"
            f"- Expand narration to 2-4 rich sentences per panel, drawing from "
            f"the novel's prose, imagery, and voice\n"
            f"- Include more of the original dialogue — key exchanges that drive "
            f"the scene forward\n"
            f"- Every panel MUST have narration text\n"
            f"- Do NOT change visual_direction, sound_effects, characters, or panel_number\n"
            f"- Maintain the scene's emotional arc across panels\n"
            f"- Return ONLY the complete JSON for the PanelScript — no markdown, no explanation"
        )

        try:
            enriched = enricher.invoke_structured(prompt, PanelScript)
            enriched_scripts.append(enriched)

            # Log improvement
            old_text = sum(
                len(p.narration) + sum(len(d) for d in p.dialogue)
                for p in script.panels
            )
            new_text = sum(
                len(p.narration) + sum(len(d) for d in p.dialogue)
                for p in enriched.panels
            )
            logger.info(
                "  Text: %d → %d chars (%.1fx)",
                old_text, new_text, new_text / max(old_text, 1),
            )
        except Exception as e:
            logger.error("  Failed to parse enriched script: %s", e)
            logger.error("  Keeping original script for scene %d", script.scene_number)
            enriched_scripts.append(script)

    # Update novel.json
    data["panel_scripts"] = [s.model_dump() for s in enriched_scripts]
    novel_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Updated %s with enriched panel scripts", novel_path)


def _find_relevant_excerpt(
    novel_text: str, script: PanelScript, max_chars: int = 12000,
) -> str:
    """Find the most relevant excerpt from the novel for this scene.

    Searches for keywords from the scene title and panel narration/dialogue
    to locate the relevant section, then extracts a window around it.
    """
    # Build search terms from the scene
    terms = script.scene_title.lower().split()
    for panel in script.panels:
        if panel.narration:
            # Use distinctive phrases from narration
            words = panel.narration.lower().split()
            terms.extend(words[:5])
        for line in panel.dialogue:
            words = line.lower().split()
            terms.extend(words[:5])

    # Remove common words
    stopwords = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
        "for", "of", "with", "by", "from", "is", "was", "are", "were",
        "be", "been", "has", "had", "have", "this", "that", "it", "i",
        "he", "she", "they", "we", "my", "his", "her", "its", "—", "not",
    }
    terms = [t for t in terms if t not in stopwords and len(t) > 3]

    # Find best position in novel text
    text_lower = novel_text.lower()
    best_pos = 0
    best_score = 0

    # Check in 2000-char windows
    step = 2000
    for pos in range(0, len(novel_text) - step, step):
        window = text_lower[pos:pos + step]
        score = sum(1 for t in terms if t in window)
        if score > best_score:
            best_score = score
            best_pos = pos

    # Extract centered window
    start = max(0, best_pos - max_chars // 4)
    end = min(len(novel_text), start + max_chars)
    excerpt = novel_text[start:end]

    # Trim to sentence boundaries
    first_period = excerpt.find(". ")
    if first_period > 0 and first_period < 200:
        excerpt = excerpt[first_period + 2:]
    last_period = excerpt.rfind(". ")
    if last_period > len(excerpt) - 200:
        excerpt = excerpt[:last_period + 1]

    return excerpt


if __name__ == "__main__":
    main()
