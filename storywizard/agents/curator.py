"""The Curator agent — articulates why a book matters and deserves to be read."""

from __future__ import annotations

from storywizard.agents.base import BaseAgent
from storywizard.models import CuratorStatement, StoryAnalysis


class Curator(BaseAgent):
    """A literary historian who explains why a book stood the test of time.

    The Curator understands cultural significance, historical impact, and
    timeless human themes. They write compelling statements that connect
    a story's deepest ideas to the reader's own life — adapted for the
    target audience's age and background.
    """

    name = "The Curator"
    system_prompt = (
        "You are The Curator — a passionate literary historian and storyteller "
        "who helps people understand why great books matter. You believe stories "
        "are humanity's most powerful technology for transmitting wisdom across "
        "generations.\n\n"
        "For each book, you articulate:\n\n"
        "1. THE HUMAN TRUTH — What universal human experience does this story "
        "capture? Why does it resonate across centuries and cultures? What does "
        "it say about who we are?\n\n"
        "2. THE HISTORICAL MOMENT — When and why was this written? What was "
        "happening in the world? What was the author's life like? What made "
        "this book revolutionary for its time?\n\n"
        "3. THE LIVING RELEVANCE — Why does this story matter NOW? How do its "
        "themes connect to the reader's modern life? What will they see "
        "differently after reading it?\n\n"
        "4. THE INVITATION — A warm, compelling reason to pick up this book "
        "right now. Not a sales pitch — a genuine invitation from someone who "
        "loves this story and wants to share it.\n\n"
        "Guidelines:\n"
        "- Write with warmth and conviction, not academic distance\n"
        "- Adapt your language and framing to the target audience's age\n"
        "- For children: focus on wonder, adventure, and emotional truths\n"
        "- For teens: focus on identity, rebellion, and seeing the world differently\n"
        "- For adults: focus on complexity, historical depth, and re-examination\n"
        "- Never spoil key plot twists\n"
        "- Connect the old to the new — show how ancient themes live in today's world\n"
        "- Be specific, not generic — every book's significance is unique"
    )

    def curate(
        self, analysis: StoryAnalysis, target_audience: str = ""
    ) -> CuratorStatement:
        """Write a curator's statement explaining why this book matters."""
        themes_str = ", ".join(analysis.themes) if analysis.themes else "not yet identified"
        characters_str = ", ".join(c.name for c in analysis.characters[:5])

        prompt = (
            f"Write a curator's statement for this book.\n\n"
            f"TITLE: {analysis.metadata.title}\n"
            f"AUTHOR: {analysis.metadata.author}\n"
            f"GENRE: {analysis.metadata.genre}\n"
            f"SETTING: {analysis.metadata.setting}, {analysis.metadata.time_period}\n"
            f"THEMES: {themes_str}\n"
            f"NARRATIVE ARC: {analysis.narrative_arc}\n"
            f"KEY CHARACTERS: {characters_str}\n"
        )

        if target_audience:
            prompt += (
                f"\nTARGET AUDIENCE: {target_audience}\n"
                f"Adapt your language, framing, and examples for this audience. "
                f"Meet them where they are.\n"
            )

        prompt += (
            f"\nProvide:\n"
            f"- human_truth: The universal human experience this book captures (2-3 sentences)\n"
            f"- historical_moment: When/why it was written and what made it revolutionary (2-3 sentences)\n"
            f"- living_relevance: Why it matters right now, today (2-3 sentences)\n"
            f"- invitation: A warm, compelling reason to read it (2-3 sentences)\n"
            f"- one_line: A single powerful sentence that captures why this book endures\n"
            f"- target_audience: Who this statement is written for\n"
        )

        return self.invoke_structured(prompt, CuratorStatement)
