"""Tests for the output renderer."""

import json
from pathlib import Path

from storywizard.models import (
    EditorialReview,
    FocusGroupFeedback,
    GeneratedPanel,
    GraphicNovel,
    Panel,
    PanelScript,
    StoryMetadata,
    VisualStyleGuide,
)
from storywizard.output.renderer import render_graphic_novel


def _make_novel(**overrides):
    defaults = dict(
        metadata=StoryMetadata(
            title="Test Novel", author="Test Author", genre="Fiction"
        ),
        style_guide=VisualStyleGuide(
            art_style="Watercolor",
            color_palette=["#FFD700 - gold"],
            mood="Warm",
        ),
        panel_scripts=[
            PanelScript(
                scene_number=1,
                scene_title="Opening",
                layout_notes="Full page spread",
                panels=[
                    Panel(
                        panel_number=1,
                        visual_direction="Wide establishing shot",
                        dialogue=["Hello!"],
                        narration="It was a dark and stormy night.",
                        sound_effects=["CRASH"],
                    )
                ],
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
    )
    defaults.update(overrides)
    return GraphicNovel(**defaults)


class TestRenderGraphicNovel:
    def test_creates_output_files(self, tmp_path):
        novel = _make_novel()
        result = render_graphic_novel(novel, tmp_path)

        assert result.exists()
        assert (tmp_path / "novel.json").exists()
        assert (tmp_path / "graphic_novel.md").exists()
        assert (tmp_path / "style_guide.md").exists()

    def test_creates_directory(self, tmp_path):
        novel = _make_novel()
        output = tmp_path / "sub" / "dir"
        render_graphic_novel(novel, output)
        assert output.exists()

    def test_novel_json_valid(self, tmp_path):
        novel = _make_novel()
        render_graphic_novel(novel, tmp_path)

        json_path = tmp_path / "novel.json"
        data = json.loads(json_path.read_text())
        assert data["metadata"]["title"] == "Test Novel"

    def test_graphic_novel_md_content(self, tmp_path):
        novel = _make_novel()
        render_graphic_novel(novel, tmp_path)

        md = (tmp_path / "graphic_novel.md").read_text()
        assert "# Test Novel" in md
        assert "Scene 1: Opening" in md
        assert "Panel 1" in md
        assert "Hello!" in md
        assert "dark and stormy night" in md
        assert "CRASH" in md

    def test_style_guide_md_content(self, tmp_path):
        novel = _make_novel()
        render_graphic_novel(novel, tmp_path)

        md = (tmp_path / "style_guide.md").read_text()
        assert "Watercolor" in md
        assert "#FFD700" in md

    def test_editorial_review_rendered(self, tmp_path):
        novel = _make_novel(
            editorial_review=EditorialReview(
                overall_score=8,
                approved=True,
                summary="Good work",
                issues=["Minor pacing issue"],
            )
        )
        render_graphic_novel(novel, tmp_path)

        review_path = tmp_path / "editorial_review.md"
        assert review_path.exists()
        md = review_path.read_text()
        assert "8/10" in md
        assert "APPROVED" in md
        assert "Minor pacing issue" in md

    def test_no_editorial_review_skipped(self, tmp_path):
        novel = _make_novel()
        render_graphic_novel(novel, tmp_path)
        assert not (tmp_path / "editorial_review.md").exists()

    def test_focus_group_rendered(self, tmp_path):
        novel = _make_novel(
            focus_group_feedback=[
                FocusGroupFeedback(
                    persona_name="Teen Reader",
                    accessibility_score=7,
                    engagement_score=8,
                    strengths=["Great visuals"],
                    would_read=True,
                )
            ]
        )
        render_graphic_novel(novel, tmp_path)

        focus_path = tmp_path / "focus_group.md"
        assert focus_path.exists()
        md = focus_path.read_text()
        assert "Teen Reader" in md
        assert "Great visuals" in md

    def test_no_focus_group_skipped(self, tmp_path):
        novel = _make_novel()
        render_graphic_novel(novel, tmp_path)
        assert not (tmp_path / "focus_group.md").exists()
