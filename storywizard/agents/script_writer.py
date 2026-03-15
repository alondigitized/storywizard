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
        "- Use narration sparingly — only when visual storytelling needs support\n"
        "- For each panel, list the CHARACTER NAMES present (from the character list provided)"
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

    def revise_scripts(
        self,
        scripts: list[PanelScript],
        characters: list[Character],
        style_guide: VisualStyleGuide,
        feedback: str,
    ) -> list[PanelScript]:
        """Revise panel scripts based on editorial feedback."""
        revised = []
        for script in scripts:
            panels_summary = "\n".join(
                f"  Panel {p.panel_number}: {p.visual_direction[:100]}"
                for p in script.panels
            )
            prompt = (
                f"Revise this graphic novel panel script based on editor feedback.\n\n"
                f"SCENE {script.scene_number}: {script.scene_title}\n"
                f"Current layout: {script.layout_notes}\n"
                f"Current panels:\n{panels_summary}\n\n"
                f"{feedback}\n\n"
                f"Art style: {style_guide.art_style}\n"
                f"Mood: {style_guide.mood}\n\n"
                f"Address the editor's concerns while keeping what works well. "
                f"Create 3-6 revised panels for this scene."
            )
            revised_script = self.invoke_structured(prompt, PanelScript)
            revised.append(revised_script)
        return revised
