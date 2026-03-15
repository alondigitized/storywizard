"""Tests for agent base class, JSON extraction, and Artist agent."""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from storywizard.agents.artist import Artist
from storywizard.agents.base import BaseAgent, MAX_RETRIES
from storywizard.config import PipelineConfig
from storywizard.models import (
    CharacterDesign,
    Panel,
    PanelScript,
    VisualStyleGuide,
)


class SimpleModel(BaseModel):
    name: str
    value: int


class TestExtractJson:
    def test_plain_json(self):
        raw = '{"name": "test", "value": 42}'
        assert BaseAgent._extract_json(raw) == raw

    def test_json_with_code_fences(self):
        raw = '```json\n{"name": "test", "value": 42}\n```'
        result = BaseAgent._extract_json(raw)
        parsed = json.loads(result)
        assert parsed["name"] == "test"
        assert parsed["value"] == 42

    def test_json_with_plain_fences(self):
        raw = '```\n{"name": "test", "value": 42}\n```'
        result = BaseAgent._extract_json(raw)
        parsed = json.loads(result)
        assert parsed["name"] == "test"

    def test_json_with_whitespace(self):
        raw = '  \n{"name": "test", "value": 42}\n  '
        result = BaseAgent._extract_json(raw)
        parsed = json.loads(result)
        assert parsed["name"] == "test"

    def test_multiline_json(self):
        raw = '```json\n{\n  "name": "test",\n  "value": 42\n}\n```'
        result = BaseAgent._extract_json(raw)
        parsed = json.loads(result)
        assert parsed["name"] == "test"


def _mock_cli_result(stdout, returncode=0, stderr=""):
    """Create a mock subprocess.CompletedProcess."""
    return subprocess.CompletedProcess(
        args=["claude"], returncode=returncode, stdout=stdout, stderr=stderr
    )


class TestBaseAgentInvoke:
    @patch("storywizard.agents.base.subprocess.run")
    def test_invoke_returns_text(self, mock_run):
        mock_run.return_value = _mock_cli_result("Hello world")

        config = PipelineConfig()
        agent = BaseAgent(config)
        result = agent.invoke("test prompt")

        assert result == "Hello world"
        mock_run.assert_called_once()

    @patch("storywizard.agents.base.subprocess.run")
    def test_invoke_with_context(self, mock_run):
        mock_run.return_value = _mock_cli_result("Response")

        config = PipelineConfig()
        agent = BaseAgent(config)
        agent.invoke("prompt", context="some context")

        call_args = mock_run.call_args
        # Context should be prepended to the prompt via input kwarg
        assert "some context" in call_args.kwargs["input"]
        assert "prompt" in call_args.kwargs["input"]

    @patch("storywizard.agents.base.subprocess.run")
    def test_invoke_structured_success(self, mock_run):
        mock_run.return_value = _mock_cli_result('{"name": "test", "value": 42}')

        config = PipelineConfig()
        agent = BaseAgent(config)
        result = agent.invoke_structured("test", SimpleModel)

        assert isinstance(result, SimpleModel)
        assert result.name == "test"
        assert result.value == 42

    @patch("storywizard.agents.base.subprocess.run")
    def test_invoke_structured_with_code_fences(self, mock_run):
        mock_run.return_value = _mock_cli_result(
            '```json\n{"name": "fenced", "value": 99}\n```'
        )

        config = PipelineConfig()
        agent = BaseAgent(config)
        result = agent.invoke_structured("test", SimpleModel)

        assert result.name == "fenced"
        assert result.value == 99

    @patch("storywizard.agents.base.subprocess.run")
    def test_invoke_structured_retries_on_invalid_json(self, mock_run):
        # First call returns invalid JSON, second returns valid
        mock_run.side_effect = [
            _mock_cli_result("not json at all"),
            _mock_cli_result('{"name": "retry", "value": 1}'),
        ]

        config = PipelineConfig()
        agent = BaseAgent(config)
        result = agent.invoke_structured("test", SimpleModel)

        assert result.name == "retry"
        assert mock_run.call_count == 2

    @patch("storywizard.agents.base.subprocess.run")
    def test_invoke_structured_fails_after_max_retries(self, mock_run):
        mock_run.return_value = _mock_cli_result("not valid json")

        config = PipelineConfig()
        agent = BaseAgent(config)

        with pytest.raises(RuntimeError, match="Failed to get valid structured"):
            agent.invoke_structured("test", SimpleModel)

        assert mock_run.call_count == MAX_RETRIES


# --- Artist: character designs in prompts ---

def _make_style_guide_with_characters():
    return VisualStyleGuide(
        art_style="Dark gothic ink",
        color_palette=["#000000 - darkness", "#8B0000 - blood"],
        mood="Brooding",
        character_designs=[
            CharacterDesign(
                character_name="Dr. Jekyll",
                appearance="Tall, thin man with sharp features and grey temples",
                clothing="Victorian frock coat, top hat",
                distinguishing_features=["wire-rimmed spectacles", "silver cane"],
                color_associations=["grey", "white"],
            ),
            CharacterDesign(
                character_name="Mr. Hyde",
                appearance="Short, hunched figure with simian features",
                clothing="Ill-fitting dark cloak",
                distinguishing_features=["crooked teeth", "wild dark hair"],
                color_associations=["black", "sickly green"],
            ),
        ],
    )


def _make_panel_script(scene_num=1, visual_direction="Dr. Jekyll walks through fog"):
    return PanelScript(
        scene_number=scene_num,
        scene_title="The Transformation",
        panels=[
            Panel(
                panel_number=1,
                visual_direction=visual_direction,
                narration="The doctor emerges from shadow.",
            ),
        ],
    )


class TestArtistCharacterDesigns:
    @patch("storywizard.agents.base.subprocess.run")
    def test_character_designs_in_prompt(self, mock_run):
        """Character designs from the style guide should appear in the Claude prompt."""
        mock_run.return_value = _mock_cli_result("A gothic image prompt")

        config = PipelineConfig()
        artist = Artist(config)
        style_guide = _make_style_guide_with_characters()
        script = _make_panel_script()

        artist._craft_image_prompt(
            script.panels[0], script, style_guide
        )

        call_args = mock_run.call_args
        prompt_sent = call_args.kwargs["input"]
        assert "CHARACTER DESIGNS:" in prompt_sent
        assert "Dr. Jekyll" in prompt_sent
        assert "wire-rimmed spectacles" in prompt_sent
        assert "Victorian frock coat" in prompt_sent

    @patch("storywizard.agents.base.subprocess.run")
    def test_previously_established_characters(self, mock_run):
        """Returning characters should get a 'PREVIOUSLY ESTABLISHED' block."""
        mock_run.return_value = _mock_cli_result("A gothic image prompt")

        config = PipelineConfig()
        artist = Artist(config)
        style_guide = _make_style_guide_with_characters()
        script = _make_panel_script(visual_direction="Dr. Jekyll enters the lab")

        registry = {"Dr. Jekyll": "scene 1, panel 1"}
        artist._craft_image_prompt(
            script.panels[0], script, style_guide, registry
        )

        call_args = mock_run.call_args
        prompt_sent = call_args.kwargs["input"]
        assert "PREVIOUSLY ESTABLISHED CHARACTERS" in prompt_sent
        assert "scene 1, panel 1" in prompt_sent


class TestArtistSeedDerivation:
    def test_seed_computed_from_base(self):
        """Seed should be base + scene*100 + panel."""
        config = PipelineConfig(flux_seed=42)
        # scene 3, panel 2 → 42 + 300 + 2 = 344
        expected = 42 + 3 * 100 + 2
        assert expected == 344

    @patch("storywizard.agents.base.subprocess.run")
    def test_generate_panels_assigns_seeds(self, mock_run):
        """generate_panels should set seed on GeneratedPanel when flux_seed is set."""
        mock_run.return_value = _mock_cli_result("prompt text")

        config = PipelineConfig(flux_seed=42)
        artist = Artist(config)
        style_guide = _make_style_guide_with_characters()
        scripts = [_make_panel_script(scene_num=2)]

        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            panels = artist.generate_panels(scripts, style_guide, Path(tmpdir))

        assert len(panels) == 1
        # seed = 42 + 2*100 + 1 = 243
        assert panels[0].seed == 243

    @patch("storywizard.agents.base.subprocess.run")
    def test_generate_panels_no_seed_when_unset(self, mock_run):
        """generate_panels should leave seed as None when flux_seed is not set."""
        mock_run.return_value = _mock_cli_result("prompt text")

        config = PipelineConfig()
        artist = Artist(config)
        style_guide = _make_style_guide_with_characters()
        scripts = [_make_panel_script()]

        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            panels = artist.generate_panels(scripts, style_guide, Path(tmpdir))

        assert panels[0].seed is None


class TestArtistFluxArguments:
    def test_mock_generate_includes_seed(self):
        """Mock backend should write seed to prompt file."""
        config = PipelineConfig()
        artist = Artist(config)

        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            path = artist._mock_generate(
                "test prompt", "test_file", Path(tmpdir), seed=12345
            )
            content = path.read_text()
            assert "SEED: 12345" in content

    def test_mock_generate_no_seed(self):
        """Mock backend should omit seed line when seed is None."""
        config = PipelineConfig()
        artist = Artist(config)

        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            path = artist._mock_generate(
                "test prompt", "test_file", Path(tmpdir), seed=None
            )
            content = path.read_text()
            assert "SEED:" not in content
