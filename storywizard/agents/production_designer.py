"""Production Designer agent — creates the visual style guide."""

from __future__ import annotations

from storywizard.agents.base import BaseAgent
from storywizard.models import StoryAnalysis, VisualStyleGuide


class ProductionDesigner(BaseAgent):
    """Defines the visual identity of the graphic novel.

    The Production Designer creates a comprehensive style guide that persists
    throughout the entire graphic novel — art style, color palette, character
    designs, environment notes, and consistency rules. Every downstream visual
    decision references this guide.
    """

    name = "Production Designer"
    system_prompt = (
        "You are an award-winning graphic novel production designer. "
        "Your role is to create a comprehensive VISUAL STYLE GUIDE that will "
        "govern every artistic decision in the graphic novel.\n\n"
        "Your style guide must define:\n"
        "1. ART STYLE — the overall visual approach (e.g., noir ink wash, "
        "vibrant watercolor, gritty realism, clean ligne claire)\n"
        "2. COLOR PALETTE — primary colors and what emotions/themes they represent. "
        "How color shifts with mood and narrative tension\n"
        "3. CHARACTER DESIGNS — distinctive visual appearance for each character, "
        "including clothing, posture, distinguishing features, and color associations\n"
        "4. ENVIRONMENT NOTES — how to render settings, backgrounds, atmosphere\n"
        "5. TYPOGRAPHY — lettering style for dialogue, narration, sound effects\n"
        "6. CONSISTENCY RULES — specific rules to maintain visual coherence "
        "across all panels (proportions, lighting conventions, panel borders, etc.)\n\n"
        "Think cinematically. Your style guide should evoke the story's mood and "
        "make the graphic novel feel like a unified artistic vision, not a "
        "collection of random illustrations."
    )

    def design(self, analysis: StoryAnalysis) -> VisualStyleGuide:
        """Create a visual style guide based on the story analysis."""
        characters_desc = "\n".join(
            f"- {c.name} ({c.role}): {c.description}" for c in analysis.characters
        )
        scenes_desc = "\n".join(
            f"- Scene {s.scene_number}: {s.title} — {s.emotional_tone}"
            for s in analysis.scenes
        )

        prompt = (
            f"Create a complete visual style guide for this graphic novel adaptation.\n\n"
            f"STORY: {analysis.metadata.title} by {analysis.metadata.author}\n"
            f"Genre: {analysis.metadata.genre}\n"
            f"Setting: {analysis.metadata.setting}, {analysis.metadata.time_period}\n"
            f"Themes: {', '.join(analysis.themes)}\n"
            f"Narrative arc: {analysis.narrative_arc}\n\n"
            f"CHARACTERS:\n{characters_desc}\n\n"
            f"KEY SCENES (with emotional tones):\n{scenes_desc}\n\n"
            f"Design a cohesive visual world for this story."
        )
        return self.invoke_structured(prompt, VisualStyleGuide)
