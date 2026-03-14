"""Script Writer agent — converts scenes into panel scripts."""

from __future__ import annotations

from storywizard.agents.base import BaseAgent
from storywizard.models import PanelScript, Scene, Character, VisualStyleGuide


class ScriptWriter(BaseAgent):
    """Converts novel scenes into graphic novel panel scripts.

    The Script Writer takes each crucial scene and breaks it into individual
    panels with dialogue, narration, visual directions, and layout notes.
    This is the blueprint the Artist will follow.
    """

    name = "Script Writer"
    system_prompt = (
        "You are an experienced graphic novel script writer who adapts literary "
        "works into visual panel scripts. For each scene, you create:\n\n"
        "1. LAYOUT NOTES — how the panels should be arranged on the page\n"
        "2. INDIVIDUAL PANELS, each with:\n"
        "   - VISUAL DIRECTION: What the artist should draw — composition, "
        "camera angle, character positions, expressions, lighting, background\n"
        "   - DIALOGUE: Speech bubble text (keep concise and punchy)\n"
        "   - NARRATION: Caption box text for internal thoughts or scene-setting\n"
        "   - SOUND EFFECTS: If applicable\n\n"
        "Guidelines:\n"
        "- Each scene should have 3-6 panels\n"
        "- Vary panel sizes for visual rhythm (wide establishing shots, "
        "tight close-ups for emotion)\n"
        "- Show, don't tell — convert prose descriptions into visual action\n"
        "- Dialogue should be adapted from the source, not copied verbatim — "
        "keep it natural for speech bubbles\n"
        "- Use narration sparingly — only when visual storytelling needs support"
    )

    def write_script(
        self,
        scene: Scene,
        characters: list[Character],
        style_guide: VisualStyleGuide,
    ) -> PanelScript:
        """Write a panel script for a single scene."""
        char_lookup = {c.name: c for c in characters}
        scene_chars = "\n".join(
            f"- {name}: {char_lookup[name].description}"
            for name in scene.characters
            if name in char_lookup
        )

        prompt = (
            f"Write a graphic novel panel script for this scene.\n\n"
            f"SCENE {scene.scene_number}: {scene.title}\n"
            f"Summary: {scene.summary}\n"
            f"Emotional tone: {scene.emotional_tone}\n"
            f"Visual description: {scene.visual_description}\n\n"
            f"Characters present:\n{scene_chars}\n\n"
            f"Key dialogue from the novel:\n"
            + "\n".join(f'  "{d}"' for d in scene.key_dialogue)
            + f"\n\nArt style: {style_guide.art_style}\n"
            f"Mood: {style_guide.mood}\n\n"
            f"Create 3-6 panels for this scene."
        )
        return self.invoke_structured(prompt, PanelScript)

    def write_all_scripts(
        self,
        scenes: list[Scene],
        characters: list[Character],
        style_guide: VisualStyleGuide,
    ) -> list[PanelScript]:
        """Write panel scripts for all scenes."""
        scripts = []
        for scene in scenes:
            script = self.write_script(scene, characters, style_guide)
            scripts.append(script)
        return scripts
