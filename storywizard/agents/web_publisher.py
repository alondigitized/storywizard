"""Web Publisher agent — prepares and publishes graphic novels for the web."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from storywizard.agents.base import BaseAgent
from storywizard.models import GraphicNovel

logger = logging.getLogger(__name__)


class WebPublisher(BaseAgent):
    """Prepares graphic novel data for the Storywizard website.

    The Web Publisher takes the final GraphicNovel output and optimizes it
    for web delivery — generating cover metadata, SEO-friendly descriptions,
    reading time estimates, and accessibility enhancements. It also produces
    the novel.json that the web reader consumes.
    """

    name = "Web Publisher"
    system_prompt = (
        "You are a digital publishing specialist who prepares graphic novels "
        "for web delivery. Your responsibilities:\n\n"
        "1. COVER METADATA — Generate an appealing book description, genre tags, "
        "cover color scheme, and reading time estimate\n"
        "2. ACCESSIBILITY — Ensure all panels have descriptive alt text that "
        "makes the story accessible to screen reader users\n"
        "3. SEO — Create search-friendly title, description, and keywords\n"
        "4. READING EXPERIENCE — Add chapter breaks, suggest page groupings "
        "for optimal reading flow\n\n"
        "Think like a digital bookstore curator — make each graphic novel "
        "discoverable and delightful to read on screen."
    )

    def prepare_for_web(self, novel: GraphicNovel, output_dir: Path) -> dict:
        """Prepare web-optimized metadata and enhanced novel data."""
        # Generate web metadata via LLM
        prompt = (
            f"Prepare web publishing metadata for this graphic novel.\n\n"
            f"Title: {novel.metadata.title}\n"
            f"Author: {novel.metadata.author}\n"
            f"Genre: {novel.metadata.genre}\n"
            f"Setting: {novel.metadata.setting}, {novel.metadata.time_period}\n"
            f"Art style: {novel.style_guide.art_style}\n"
            f"Number of scenes: {len(novel.panel_scripts)}\n"
            f"Number of panels: {len(novel.generated_panels)}\n\n"
            f"Provide a JSON response with:\n"
            f"- \"description\": A 2-3 sentence compelling book description\n"
            f"- \"tags\": List of 5-8 genre/topic tags\n"
            f"- \"accent_color\": A hex color that matches the book's mood\n"
            f"- \"cover_bg\": A dark hex color for the book cover background\n"
            f"- \"reading_time_minutes\": Estimated reading time\n"
            f"- \"target_audience\": Brief description of ideal reader\n"
            f"- \"seo_description\": A 160-char SEO meta description\n\n"
            f"Respond with ONLY valid JSON."
        )
        raw = self.invoke(prompt)
        text = raw.strip()
        if text.startswith("```"):
            lines = text.split("\n")[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)

        try:
            web_meta = json.loads(text)
        except json.JSONDecodeError:
            logger.warning("Failed to parse web metadata, using defaults")
            web_meta = {
                "description": f"A graphic novel adaptation of {novel.metadata.title}",
                "tags": [novel.metadata.genre],
                "accent_color": "#c9a96e",
                "cover_bg": "#1a1a2e",
                "reading_time_minutes": len(novel.generated_panels) * 2,
                "target_audience": "All readers",
                "seo_description": f"Read {novel.metadata.title} as a stunning AI-generated graphic novel.",
            }

        # Merge web metadata into the novel JSON
        novel_data = json.loads(novel.model_dump_json())
        novel_data.update(web_meta)

        # Save enhanced novel.json
        output_dir.mkdir(parents=True, exist_ok=True)
        json_path = output_dir / "novel.json"
        json_path.write_text(json.dumps(novel_data, indent=2), encoding="utf-8")
        logger.info("Web-optimized novel.json saved to %s", json_path)

        return novel_data


class AccessibilityReviewer(BaseAgent):
    """Reviews the graphic novel for web accessibility compliance.

    Ensures the web version of the graphic novel is accessible to all users,
    including those using screen readers, keyboard navigation, or who have
    visual impairments.
    """

    name = "Accessibility Reviewer"
    system_prompt = (
        "You are a web accessibility specialist (WCAG 2.1 AA expert) reviewing "
        "a graphic novel for its web presentation. You check:\n\n"
        "1. ALT TEXT — Every panel image must have descriptive alt text that "
        "conveys the visual content and emotional tone\n"
        "2. READING ORDER — Text content must follow a logical reading order\n"
        "3. COLOR CONTRAST — Text must be readable against backgrounds\n"
        "4. KEYBOARD NAVIGATION — All interactive elements must be reachable\n"
        "5. SCREEN READER EXPERIENCE — The story must be comprehensible "
        "through text alone\n\n"
        "Provide specific, actionable recommendations."
    )

    def review_accessibility(self, novel: GraphicNovel) -> dict:
        """Review and enhance accessibility of the graphic novel."""
        # Build panel descriptions for review
        panels_desc = []
        for script in novel.panel_scripts:
            for panel in script.panels:
                panels_desc.append(
                    f"Scene {script.scene_number}, Panel {panel.panel_number}: "
                    f"Direction: {panel.visual_direction[:100]} | "
                    f"Dialogue: {panel.dialogue} | "
                    f"Narration: {panel.narration}"
                )

        prompt = (
            f"Review this graphic novel's web accessibility.\n\n"
            f"Title: {novel.metadata.title}\n"
            f"Art style: {novel.style_guide.art_style}\n"
            f"Color palette: {novel.style_guide.color_palette}\n\n"
            f"PANELS:\n" + "\n".join(panels_desc[:30]) + "\n\n"
            f"Provide a JSON response with:\n"
            f"- \"overall_score\": Accessibility score 1-10\n"
            f"- \"issues\": List of specific accessibility issues found\n"
            f"- \"enhanced_alt_texts\": Dict mapping \"scene_panel\" keys to improved alt text\n"
            f"- \"recommendations\": List of general recommendations\n\n"
            f"Respond with ONLY valid JSON."
        )
        raw = self.invoke(prompt)
        text = raw.strip()
        if text.startswith("```"):
            lines = text.split("\n")[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            logger.warning("Failed to parse accessibility review")
            return {
                "overall_score": 7,
                "issues": [],
                "enhanced_alt_texts": {},
                "recommendations": ["Add descriptive alt text to all panels"],
            }
