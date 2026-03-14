"""Pipeline configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class PipelineConfig:
    """Configuration for the Storywizard publishing pipeline."""

    # Anthropic
    anthropic_api_key: str = field(
        default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY", "")
    )
    model_name: str = "claude-sonnet-4-6"

    # Image generation
    image_backend: str = "mock"  # "mock" | "flux"
    image_api_key: str = field(
        default_factory=lambda: os.environ.get("IMAGE_API_KEY", "")
    )

    # Flux (via fal.ai) settings
    flux_model: str = "fal-ai/flux/dev"
    flux_aspect_ratio: str = "landscape_16_9"

    # Pipeline tuning
    max_scenes: int = 15
    max_panels_per_scene: int = 6
    max_revision_rounds: int = 2

    # Output
    output_dir: str = "output"
    stories_dir: str = "stories"
