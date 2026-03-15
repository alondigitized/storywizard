"""Tests for PipelineConfig validation."""

import os
from unittest.mock import patch

from storywizard.config import PipelineConfig


class TestPipelineConfigValidation:
    def test_valid_config(self):
        config = PipelineConfig()
        errors = config.validate()
        assert errors == []

    def test_invalid_backend(self):
        config = PipelineConfig(image_backend="dalle")
        errors = config.validate()
        assert any("image_backend" in e for e in errors)

    def test_flux_without_fal_key(self):
        with patch.dict(os.environ, {}, clear=True):
            config = PipelineConfig(image_backend="flux")
            # Ensure FAL_KEY is not set
            os.environ.pop("FAL_KEY", None)
            errors = config.validate()
            assert any("FAL_KEY" in e for e in errors)

    def test_flux_with_fal_key(self):
        with patch.dict(os.environ, {"FAL_KEY": "test-fal-key"}):
            config = PipelineConfig(image_backend="flux")
            errors = config.validate()
            assert errors == []

    def test_max_scenes_too_low(self):
        config = PipelineConfig(max_scenes=0)
        errors = config.validate()
        assert any("max_scenes" in e for e in errors)

    def test_max_scenes_too_high(self):
        config = PipelineConfig(max_scenes=100)
        errors = config.validate()
        assert any("max_scenes" in e for e in errors)

    def test_max_panels_per_scene_bounds(self):
        config = PipelineConfig(max_panels_per_scene=0)
        errors = config.validate()
        assert any("max_panels_per_scene" in e for e in errors)

        config2 = PipelineConfig(max_panels_per_scene=20)
        errors2 = config2.validate()
        assert any("max_panels_per_scene" in e for e in errors2)

    def test_max_revision_rounds_bounds(self):
        config = PipelineConfig(max_revision_rounds=-1)
        errors = config.validate()
        assert any("max_revision_rounds" in e for e in errors)

    def test_multiple_errors(self):
        config = PipelineConfig(
            image_backend="invalid",
            max_scenes=0,
        )
        errors = config.validate()
        assert len(errors) >= 2

    def test_flux_guidance_scale_bounds(self):
        config = PipelineConfig(flux_guidance_scale=0.5)
        errors = config.validate()
        assert any("flux_guidance_scale" in e for e in errors)

        config2 = PipelineConfig(flux_guidance_scale=25.0)
        errors2 = config2.validate()
        assert any("flux_guidance_scale" in e for e in errors2)

    def test_flux_guidance_scale_valid(self):
        config = PipelineConfig(flux_guidance_scale=5.0)
        errors = config.validate()
        assert not any("flux_guidance_scale" in e for e in errors)

    def test_flux_num_inference_steps_bounds(self):
        config = PipelineConfig(flux_num_inference_steps=0)
        errors = config.validate()
        assert any("flux_num_inference_steps" in e for e in errors)

        config2 = PipelineConfig(flux_num_inference_steps=200)
        errors2 = config2.validate()
        assert any("flux_num_inference_steps" in e for e in errors2)

    def test_flux_num_inference_steps_valid(self):
        config = PipelineConfig(flux_num_inference_steps=35)
        errors = config.validate()
        assert not any("flux_num_inference_steps" in e for e in errors)

    def test_default_values(self):
        config = PipelineConfig()
        assert config.model_name == "claude-sonnet-4-6"
        assert config.image_backend == "mock"
        assert config.max_scenes == 15
        assert config.max_panels_per_scene == 6
        assert config.max_revision_rounds == 2
        assert config.output_dir == "output"
        assert config.stories_dir == "stories"
        assert config.flux_seed is None
        assert config.flux_guidance_scale == 7.0
        assert config.flux_num_inference_steps == 28
        assert config.flux_negative_prompt != ""
        assert config.flux_reference_strength == 0.50
