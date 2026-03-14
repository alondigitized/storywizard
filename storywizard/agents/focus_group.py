"""Focus Group agent — evaluates from target persona perspectives."""

from __future__ import annotations

from pydantic import BaseModel, Field

from storywizard.agents.base import BaseAgent
from storywizard.models import (
    EditorialReview,
    FocusGroupFeedback,
    GraphicNovel,
    PanelScript,
    StoryMetadata,
    VisualStyleGuide,
)


class FocusGroupResponse(BaseModel):
    """Container for all focus group persona responses."""

    feedback: list[FocusGroupFeedback]


PERSONAS = [
    {
        "name": "Reluctant Teen Reader",
        "description": (
            "A 15-year-old who finds traditional books boring and intimidating. "
            "Loves visual media — anime, comics, video games, TikTok. "
            "Will disengage quickly if the pacing is slow or dialogue feels old-fashioned. "
            "Responds to action, emotion, and cool visuals."
        ),
    },
    {
        "name": "Visual Learner Adult",
        "description": (
            "A 35-year-old professional who prefers visual communication. "
            "Reads graphic novels and illustrated non-fiction. Appreciates "
            "artistic quality and narrative depth. Wants the adaptation to "
            "honor the original while being visually stunning."
        ),
    },
    {
        "name": "ESL Student",
        "description": (
            "A 22-year-old learning English as a second language. "
            "Visual context helps with comprehension. Needs clear, simple "
            "dialogue. Benefits from visual storytelling that conveys meaning "
            "even when some words are unfamiliar. Values accessibility."
        ),
    },
]


class FocusGroup(BaseAgent):
    """Evaluates the graphic novel from multiple target persona perspectives.

    The Focus Group simulates reader reactions from different demographics
    to ensure the graphic novel is accessible and engaging for its intended
    audience.
    """

    name = "Focus Group"
    system_prompt = (
        "You are a focus group facilitator running reader testing for a graphic "
        "novel adaptation of a classic novel. You will evaluate the graphic novel "
        "from the perspective of MULTIPLE reader personas.\n\n"
        "For EACH persona, assess:\n"
        "1. ACCESSIBILITY — How easy is it for this reader to follow the story?\n"
        "2. ENGAGEMENT — Would this reader stay interested? What hooks them?\n"
        "3. STRENGTHS — What works well for this type of reader?\n"
        "4. CONCERNS — What might turn this reader off or confuse them?\n"
        "5. SUGGESTIONS — Specific changes that would improve the experience\n\n"
        "Be honest and specific. Each persona should have a distinct voice and "
        "distinct concerns. The goal is to make classic literature accessible "
        "to everyone."
    )

    def evaluate(
        self,
        metadata: StoryMetadata,
        style_guide: VisualStyleGuide,
        scripts: list[PanelScript],
        editorial_review: EditorialReview,
    ) -> list[FocusGroupFeedback]:
        """Run focus group evaluation with all personas."""
        personas_desc = "\n\n".join(
            f"PERSONA: {p['name']}\n{p['description']}" for p in PERSONAS
        )

        scripts_summary = "\n".join(
            f"Scene {s.scene_number} ({s.scene_title}): {len(s.panels)} panels — "
            + "; ".join(
                p.visual_direction[:80] for p in s.panels[:3]
            )
            for s in scripts
        )

        prompt = (
            f"Evaluate this graphic novel from each persona's perspective.\n\n"
            f"GRAPHIC NOVEL: {metadata.title} by {metadata.author}\n"
            f"Genre: {metadata.genre}\n"
            f"Art style: {style_guide.art_style}\n"
            f"Mood: {style_guide.mood}\n\n"
            f"SCENES:\n{scripts_summary}\n\n"
            f"EDITOR'S REVIEW: Score {editorial_review.overall_score}/10\n"
            f"{editorial_review.summary}\n\n"
            f"PERSONAS TO EVALUATE AS:\n{personas_desc}\n\n"
            f"Provide feedback from each persona."
        )
        response = self.invoke_structured(prompt, FocusGroupResponse)
        return response.feedback
