"""Pipeline configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class PipelineConfig:
    """Configuration for the Storywizard publishing pipeline."""

    # Claude CLI model
    model_name: str = "claude-sonnet-4-6"

    # Image generation
    image_backend: str = "mock"  # "mock" | "flux"
    image_api_key: str = field(
        default_factory=lambda: os.environ.get("IMAGE_API_KEY", "")
    )

    # Flux (via fal.ai) settings
    flux_model: str = "fal-ai/flux-general"
    flux_aspect_ratio: str = "landscape_16_9"
    flux_seed: int | None = None  # None = random; set for reproducibility
    flux_guidance_scale: float = 7.0  # 1.0-20.0; higher = more prompt-adherent
    flux_num_inference_steps: int = 28  # 1-100; higher = better quality
    flux_negative_prompt: str = (
        "text, words, lettering, typography, title, caption, speech bubble, subtitle, "
        "watermark, signature, "
        "photograph, photo, photorealistic, 3D render, CGI, anime, manga, "
        "cartoon, cel-shaded, flat color, vector art, stock photo, film still, "
        "movie screenshot"
    )
    flux_reference_strength: float = 0.50  # 0.0-1.0; style anchor strength

    # Character reference generation
    character_ref_enabled: bool = True
    character_ref_model: str = "fal-ai/recraft/v4/pro/text-to-image"
    character_ref_aspect_ratio: str = "portrait_4_3"
    character_ref_roles: list[str] = field(
        default_factory=lambda: ["protagonist", "antagonist"]
    )

    # Kontext (character-consistent panel generation)
    kontext_model: str = "fal-ai/flux-pro/kontext"
    kontext_guidance_scale: float = 4.0

    # Group references
    group_ref_enabled: bool = True
    group_ref_min_appearances: int = 3

    # Pipeline tuning
    max_scenes: int = 15
    max_panels_per_scene: int = 6
    max_revision_rounds: int = 2

    # Output
    output_dir: str = "output"
    stories_dir: str = "stories"

    def validate(self) -> list[str]:
        """Validate configuration and return list of errors (empty = valid)."""
        errors = []

        if self.image_backend not in ("mock", "flux"):
            errors.append(
                f"Invalid image_backend '{self.image_backend}'. Must be 'mock' or 'flux'."
            )

        if self.image_backend == "flux" and not os.environ.get("FAL_KEY"):
            errors.append(
                "FAL_KEY environment variable is required when using the 'flux' backend."
            )

        if self.max_scenes < 1 or self.max_scenes > 50:
            errors.append(
                f"max_scenes must be between 1 and 50, got {self.max_scenes}."
            )

        if self.max_panels_per_scene < 1 or self.max_panels_per_scene > 12:
            errors.append(
                f"max_panels_per_scene must be between 1 and 12, got {self.max_panels_per_scene}."
            )

        if self.max_revision_rounds < 0 or self.max_revision_rounds > 5:
            errors.append(
                f"max_revision_rounds must be between 0 and 5, got {self.max_revision_rounds}."
            )

        if not (1.0 <= self.flux_guidance_scale <= 20.0):
            errors.append(
                f"flux_guidance_scale must be between 1.0 and 20.0, got {self.flux_guidance_scale}."
            )

        if not (1 <= self.flux_num_inference_steps <= 100):
            errors.append(
                f"flux_num_inference_steps must be between 1 and 100, got {self.flux_num_inference_steps}."
            )

        if not (0.0 <= self.flux_reference_strength <= 1.0):
            errors.append(
                f"flux_reference_strength must be between 0.0 and 1.0, got {self.flux_reference_strength}."
            )

        if not (1.0 <= self.kontext_guidance_scale <= 20.0):
            errors.append(
                f"kontext_guidance_scale must be between 1.0 and 20.0, got {self.kontext_guidance_scale}."
            )

        return errors
