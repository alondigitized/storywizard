"""Data models for the Storywizard publishing pipeline."""

from __future__ import annotations

from pydantic import BaseModel, Field


class StoryMetadata(BaseModel):
    """Metadata about the source novel."""

    title: str
    author: str
    source_url: str = ""
    gutenberg_id: int | None = None
    genre: str = ""
    setting: str = ""
    time_period: str = ""


class Character(BaseModel):
    """A character extracted from the novel."""

    name: str
    description: str = Field(description="Physical and personality description")
    visual_traits: list[str] = Field(
        default_factory=list,
        description="Distinctive visual features for consistent rendering",
    )
    role: str = Field(description="protagonist, antagonist, supporting, minor")


class Scene(BaseModel):
    """A crucial scene identified for the graphic novel."""

    scene_number: int
    chapter: str = ""
    title: str
    summary: str
    characters: list[str] = Field(description="Character names present in the scene")
    emotional_tone: str = ""
    key_dialogue: list[str] = Field(
        default_factory=list, description="Important dialogue lines"
    )
    visual_description: str = Field(
        default="", description="What should be visually depicted"
    )


class StoryAnalysis(BaseModel):
    """Complete output from the Story Analyst."""

    metadata: StoryMetadata
    characters: list[Character]
    scenes: list[Scene]
    themes: list[str] = Field(default_factory=list)
    narrative_arc: str = ""


class Panel(BaseModel):
    """A single panel in the graphic novel."""

    panel_number: int
    visual_direction: str = Field(
        description="What the artist should depict — composition, framing, action"
    )
    dialogue: list[str] = Field(
        default_factory=list, description="Speech bubbles"
    )
    narration: str = Field(default="", description="Caption/narration box text")
    sound_effects: list[str] = Field(default_factory=list)


class PanelScript(BaseModel):
    """Script for all panels in one scene."""

    scene_number: int
    scene_title: str
    layout_notes: str = Field(
        default="", description="Page layout guidance for the artist"
    )
    panels: list[Panel]


class CharacterDesign(BaseModel):
    """Visual design specification for a character."""

    character_name: str
    appearance: str
    clothing: str = ""
    distinguishing_features: list[str] = Field(default_factory=list)
    color_associations: list[str] = Field(default_factory=list)


class VisualStyleGuide(BaseModel):
    """The production designer's visual bible for the graphic novel."""

    art_style: str = Field(
        description="Overall art style (e.g., noir, watercolor, manga)"
    )
    color_palette: list[str] = Field(
        description="Primary colors and their narrative associations"
    )
    mood: str = ""
    character_designs: list[CharacterDesign] = Field(default_factory=list)
    environment_notes: str = Field(
        default="", description="Guidance for backgrounds and settings"
    )
    typography_notes: str = Field(
        default="", description="Font and lettering style guidance"
    )
    consistency_rules: list[str] = Field(
        default_factory=list,
        description="Rules to maintain visual coherence across panels",
    )
    full_style_document: str = Field(
        default="",
        description="Complete style guide as markdown for reference",
    )


class GeneratedPanel(BaseModel):
    """An artist-produced panel with image prompt and result."""

    scene_number: int
    panel_number: int
    image_prompt: str = Field(description="The prompt sent to the image generator")
    image_path: str = Field(default="", description="Path to the generated image")
    alt_text: str = Field(default="", description="Accessibility description")


class EditorialReview(BaseModel):
    """Critical editor's review of the graphic novel draft."""

    overall_score: int = Field(ge=1, le=10, description="Quality score 1-10")
    approved: bool
    visual_consistency: str = ""
    narrative_coherence: str = ""
    dialogue_quality: str = ""
    pacing: str = ""
    issues: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    summary: str = ""


class FocusGroupFeedback(BaseModel):
    """Feedback from one focus group persona."""

    persona_name: str = Field(description="e.g., 'Reluctant Teen Reader'")
    persona_description: str = ""
    accessibility_score: int = Field(ge=1, le=10)
    engagement_score: int = Field(ge=1, le=10)
    strengths: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    would_read: bool = True
    summary: str = ""


class GraphicNovel(BaseModel):
    """The complete graphic novel output."""

    metadata: StoryMetadata
    style_guide: VisualStyleGuide
    panel_scripts: list[PanelScript]
    generated_panels: list[GeneratedPanel]
    editorial_review: EditorialReview | None = None
    focus_group_feedback: list[FocusGroupFeedback] = Field(default_factory=list)
