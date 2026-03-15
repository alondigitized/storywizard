"""Tests for Pydantic data models."""

import pytest
from pydantic import ValidationError

from storywizard.models import (
    Character,
    CuratorStatement,
    EditorialReview,
    FocusGroupFeedback,
    GeneratedPanel,
    GraphicNovel,
    Panel,
    PanelScript,
    Scene,
    StoryAnalysis,
    StoryMetadata,
    VisualStyleGuide,
)


# --- Fixtures ---

def make_metadata(**overrides):
    defaults = {
        "title": "Test Novel",
        "author": "Test Author",
        "gutenberg_id": 1,
        "genre": "Fiction",
        "setting": "London",
        "time_period": "Victorian era",
    }
    defaults.update(overrides)
    return StoryMetadata(**defaults)


def make_character(**overrides):
    defaults = {
        "name": "Alice",
        "description": "A curious young girl",
        "visual_traits": ["blonde hair", "blue dress"],
        "role": "protagonist",
    }
    defaults.update(overrides)
    return Character(**defaults)


def make_scene(**overrides):
    defaults = {
        "scene_number": 1,
        "title": "Opening",
        "summary": "The story begins",
        "characters": ["Alice"],
        "emotional_tone": "curious",
        "key_dialogue": ["Curiouser and curiouser!"],
        "visual_description": "A garden on a sunny day",
    }
    defaults.update(overrides)
    return Scene(**defaults)


def make_style_guide(**overrides):
    defaults = {
        "art_style": "Watercolor illustration",
        "color_palette": ["#FFD700 - wonder", "#87CEEB - sky"],
        "mood": "Whimsical and dreamlike",
    }
    defaults.update(overrides)
    return VisualStyleGuide(**defaults)


# --- StoryMetadata ---

class TestStoryMetadata:
    def test_basic_creation(self):
        m = make_metadata()
        assert m.title == "Test Novel"
        assert m.author == "Test Author"

    def test_defaults(self):
        m = StoryMetadata(title="T", author="A")
        assert m.source_url == ""
        assert m.gutenberg_id is None
        assert m.genre == ""

    def test_json_round_trip(self):
        m = make_metadata()
        json_str = m.model_dump_json()
        restored = StoryMetadata.model_validate_json(json_str)
        assert restored == m


# --- Character ---

class TestCharacter:
    def test_basic_creation(self):
        c = make_character()
        assert c.name == "Alice"
        assert len(c.visual_traits) == 2

    def test_empty_visual_traits(self):
        c = Character(name="Bob", description="A man", role="minor")
        assert c.visual_traits == []


# --- Scene ---

class TestScene:
    def test_basic_creation(self):
        s = make_scene()
        assert s.scene_number == 1
        assert s.title == "Opening"

    def test_empty_dialogue(self):
        s = make_scene(key_dialogue=[])
        assert s.key_dialogue == []


# --- StoryAnalysis ---

class TestStoryAnalysis:
    def test_basic_creation(self):
        analysis = StoryAnalysis(
            metadata=make_metadata(),
            characters=[make_character()],
            scenes=[make_scene()],
            themes=["identity", "wonder"],
            narrative_arc="A journey of discovery",
        )
        assert len(analysis.characters) == 1
        assert len(analysis.scenes) == 1
        assert len(analysis.themes) == 2

    def test_json_round_trip(self):
        analysis = StoryAnalysis(
            metadata=make_metadata(),
            characters=[make_character()],
            scenes=[make_scene()],
            themes=["wonder"],
        )
        json_str = analysis.model_dump_json()
        restored = StoryAnalysis.model_validate_json(json_str)
        assert restored.metadata.title == "Test Novel"
        assert restored.characters[0].name == "Alice"


# --- Panel and PanelScript ---

class TestPanel:
    def test_basic_creation(self):
        p = Panel(
            panel_number=1,
            visual_direction="Wide shot of the garden",
            dialogue=["Hello!", "Welcome."],
            narration="It was a sunny day.",
        )
        assert p.panel_number == 1
        assert len(p.dialogue) == 2

    def test_defaults(self):
        p = Panel(panel_number=1, visual_direction="A shot")
        assert p.dialogue == []
        assert p.narration == ""
        assert p.sound_effects == []


class TestPanelScript:
    def test_basic_creation(self):
        script = PanelScript(
            scene_number=1,
            scene_title="Opening",
            layout_notes="Two-panel spread",
            panels=[
                Panel(panel_number=1, visual_direction="Wide shot"),
                Panel(panel_number=2, visual_direction="Close-up"),
            ],
        )
        assert len(script.panels) == 2


# --- GeneratedPanel ---

class TestGeneratedPanel:
    def test_basic_creation(self):
        gp = GeneratedPanel(
            scene_number=1,
            panel_number=2,
            image_prompt="A wide shot of the garden",
            image_path="panels/scene01_panel02.png",
        )
        assert gp.scene_number == 1
        assert gp.seed is None

    def test_with_seed(self):
        gp = GeneratedPanel(
            scene_number=3,
            panel_number=1,
            image_prompt="Close-up",
            seed=4201,
        )
        assert gp.seed == 4201

    def test_json_round_trip_with_seed(self):
        gp = GeneratedPanel(
            scene_number=1,
            panel_number=1,
            image_prompt="prompt",
            seed=12345,
        )
        restored = GeneratedPanel.model_validate_json(gp.model_dump_json())
        assert restored.seed == 12345


# --- EditorialReview ---

class TestEditorialReview:
    def test_approved(self):
        r = EditorialReview(overall_score=8, approved=True)
        assert r.approved
        assert r.overall_score == 8

    def test_score_bounds(self):
        with pytest.raises(ValidationError):
            EditorialReview(overall_score=0, approved=False)
        with pytest.raises(ValidationError):
            EditorialReview(overall_score=11, approved=False)

    def test_score_boundaries_valid(self):
        r1 = EditorialReview(overall_score=1, approved=False)
        r10 = EditorialReview(overall_score=10, approved=True)
        assert r1.overall_score == 1
        assert r10.overall_score == 10


# --- FocusGroupFeedback ---

class TestFocusGroupFeedback:
    def test_basic_creation(self):
        fb = FocusGroupFeedback(
            persona_name="Teen Reader",
            accessibility_score=7,
            engagement_score=8,
            would_read=True,
        )
        assert fb.persona_name == "Teen Reader"
        assert fb.would_read

    def test_score_bounds(self):
        with pytest.raises(ValidationError):
            FocusGroupFeedback(
                persona_name="X",
                accessibility_score=0,
                engagement_score=5,
            )


# --- CuratorStatement ---

class TestCuratorStatement:
    def test_basic_creation(self):
        cs = CuratorStatement(
            human_truth="We all struggle with identity",
            historical_moment="Written during the Victorian era",
            living_relevance="Social media creates dual identities",
            invitation="Step into a world of shadows",
            one_line="A mirror held up to our hidden selves",
        )
        assert "identity" in cs.human_truth


# --- GraphicNovel ---

class TestGraphicNovel:
    def test_minimal_creation(self):
        novel = GraphicNovel(
            metadata=make_metadata(),
            style_guide=make_style_guide(),
            panel_scripts=[],
            generated_panels=[],
        )
        assert novel.metadata.title == "Test Novel"
        assert novel.editorial_review is None
        assert novel.curator_statement is None
        assert novel.focus_group_feedback == []

    def test_full_creation(self):
        novel = GraphicNovel(
            metadata=make_metadata(),
            curator_statement=CuratorStatement(
                human_truth="truth",
                historical_moment="history",
                living_relevance="relevance",
                invitation="invitation",
                one_line="one line",
            ),
            style_guide=make_style_guide(),
            panel_scripts=[
                PanelScript(
                    scene_number=1,
                    scene_title="Opening",
                    panels=[Panel(panel_number=1, visual_direction="Wide shot")],
                )
            ],
            generated_panels=[
                GeneratedPanel(
                    scene_number=1,
                    panel_number=1,
                    image_prompt="A wide shot",
                    image_path="panels/scene01_panel01.png",
                    alt_text="Opening scene",
                )
            ],
            editorial_review=EditorialReview(overall_score=8, approved=True),
            focus_group_feedback=[
                FocusGroupFeedback(
                    persona_name="Teen",
                    accessibility_score=7,
                    engagement_score=8,
                )
            ],
        )
        assert len(novel.panel_scripts) == 1
        assert len(novel.generated_panels) == 1
        assert novel.editorial_review.approved

    def test_json_round_trip(self):
        novel = GraphicNovel(
            metadata=make_metadata(),
            style_guide=make_style_guide(),
            panel_scripts=[],
            generated_panels=[],
        )
        json_str = novel.model_dump_json()
        restored = GraphicNovel.model_validate_json(json_str)
        assert restored.metadata.title == novel.metadata.title
