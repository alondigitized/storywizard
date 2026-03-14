"""Story Analyst agent — reads the novel and extracts structure."""

from __future__ import annotations

from storywizard.agents.base import BaseAgent
from storywizard.models import StoryAnalysis, StoryMetadata


class StoryAnalyst(BaseAgent):
    """Reads a novel and breaks it into chapters, key scenes, and characters.

    The Story Analyst is the first agent in the pipeline. It identifies the
    crucial moments worth depicting as graphic novel panels and extracts
    character descriptions for visual consistency.
    """

    name = "Story Analyst"
    system_prompt = (
        "You are a literary analyst specializing in adapting novels into graphic novels. "
        "Your job is to read a complete novel and identify:\n"
        "1. The major CHARACTERS with detailed physical and personality descriptions\n"
        "2. The most CRUCIAL SCENES that must be depicted visually — moments of high drama, "
        "key plot turns, emotional peaks, and visually striking moments\n"
        "3. The core THEMES of the story\n"
        "4. The overall NARRATIVE ARC\n\n"
        "For each scene, provide enough detail that an artist could visualize it. "
        "Include the emotional tone, which characters are present, key dialogue, "
        "and what should be visually depicted.\n\n"
        "Focus on scenes that will translate powerfully to a visual medium. "
        "A graphic novel cannot include everything — select the moments that "
        "carry the story's essence."
    )

    def analyze(self, text: str, metadata: StoryMetadata) -> StoryAnalysis:
        """Analyze the novel and return structured story analysis."""
        prompt = (
            f"Analyze this novel for graphic novel adaptation.\n\n"
            f"Title: {metadata.title}\n"
            f"Author: {metadata.author}\n"
            f"Genre: {metadata.genre}\n"
            f"Setting: {metadata.setting}, {metadata.time_period}\n\n"
            f"Identify up to {self.config.max_scenes} crucial scenes, "
            f"all major characters, themes, and the narrative arc.\n\n"
            f"NOVEL TEXT:\n{text[:80000]}"  # Truncate if extremely long
        )
        return self.invoke_structured(prompt, StoryAnalysis)
