"""Critical Editor agent — quality gate for the graphic novel."""

from __future__ import annotations

from storywizard.agents.base import BaseAgent
from storywizard.models import (
    EditorialReview,
    GeneratedPanel,
    PanelScript,
    VisualStyleGuide,
    StoryMetadata,
)


class CriticalEditor(BaseAgent):
    """Reviews the graphic novel draft for quality and consistency.

    The Critical Editor is the quality gate — it checks for visual consistency,
    narrative coherence, dialogue quality, and pacing. It can reject the draft
    and send it back for revision.
    """

    name = "Critical Editor"
    system_prompt = (
        "You are a ruthlessly honest graphic novel editor. Your job is to ensure "
        "quality and catch problems before publication. You review:\n\n"
        "1. VISUAL CONSISTENCY — Do the image prompts maintain the style guide? "
        "Are characters described consistently across panels?\n"
        "2. NARRATIVE COHERENCE — Does the graphic novel tell a coherent story? "
        "Are scenes in logical order? Is anything confusing?\n"
        "3. DIALOGUE QUALITY — Is the dialogue natural, concise, and appropriate "
        "for speech bubbles? Does it sound like real people talking?\n"
        "4. PACING — Does the graphic novel flow well? Are there too many panels "
        "in some scenes and too few in others?\n"
        "5. FAITHFULNESS — Does the adaptation honor the source material while "
        "making smart choices for the visual medium?\n\n"
        "Be specific in your feedback. Don't just say 'this is bad' — explain "
        "exactly what's wrong and how to fix it. Score 1-10 and approve only "
        "if the score is 7 or above."
    )

    def review(
        self,
        metadata: StoryMetadata,
        style_guide: VisualStyleGuide,
        scripts: list[PanelScript],
        panels: list[GeneratedPanel],
    ) -> EditorialReview:
        """Review the complete graphic novel draft."""
        # Build a summary of the draft for review
        draft_summary = self._build_draft_summary(
            metadata, style_guide, scripts, panels
        )

        prompt = (
            f"Review this graphic novel draft thoroughly.\n\n"
            f"{draft_summary}\n\n"
            f"Evaluate visual consistency, narrative coherence, dialogue quality, "
            f"pacing, and faithfulness to the source material.\n"
            f"Score 1-10. Approve only if score >= 7."
        )
        return self.invoke_structured(prompt, EditorialReview)

    def _build_draft_summary(
        self,
        metadata: StoryMetadata,
        style_guide: VisualStyleGuide,
        scripts: list[PanelScript],
        panels: list[GeneratedPanel],
    ) -> str:
        """Build a text summary of the draft for review."""
        lines = [
            f"GRAPHIC NOVEL: {metadata.title} by {metadata.author}",
            f"Art style: {style_guide.art_style}",
            f"Color palette: {', '.join(style_guide.color_palette)}",
            f"Mood: {style_guide.mood}",
            f"Total scenes: {len(scripts)}",
            f"Total panels: {len(panels)}",
            "",
        ]

        panel_lookup: dict[tuple[int, int], GeneratedPanel] = {
            (p.scene_number, p.panel_number): p for p in panels
        }

        for script in scripts:
            lines.append(f"--- SCENE {script.scene_number}: {script.scene_title} ---")
            lines.append(f"Layout: {script.layout_notes}")
            for panel in script.panels:
                key = (script.scene_number, panel.panel_number)
                gen = panel_lookup.get(key)
                lines.append(f"  Panel {panel.panel_number}:")
                lines.append(f"    Visual: {panel.visual_direction}")
                lines.append(f"    Dialogue: {panel.dialogue}")
                lines.append(f"    Narration: {panel.narration}")
                if gen:
                    lines.append(f"    Image prompt: {gen.image_prompt[:200]}...")
            lines.append("")

        return "\n".join(lines)
