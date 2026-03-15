"""Artist agent — generates image prompts and calls image generation."""

from __future__ import annotations

import logging
import time
from pathlib import Path

import httpx

from storywizard.agents.base import BaseAgent
from storywizard.models import GeneratedPanel, Panel, PanelScript, VisualStyleGuide

logger = logging.getLogger(__name__)


class Artist(BaseAgent):
    """Creates image generation prompts and produces panel artwork.

    The Artist takes panel scripts and the visual style guide, then crafts
    detailed image generation prompts. Supports multiple backends:
    - "mock": saves prompts as text files (free, for testing)
    - "flux": uses Flux via fal.ai API (high quality, fast inference)
    """

    name = "Artist"
    system_prompt = (
        "You are a graphic novel artist who creates detailed image generation "
        "prompts. For each panel, you craft a prompt that:\n\n"
        "1. Describes the COMPOSITION — camera angle, framing, focal point\n"
        "2. Specifies CHARACTERS — their appearance, expression, pose, position\n"
        "3. Sets the ENVIRONMENT — background, lighting, atmosphere, weather\n"
        "4. Maintains STYLE CONSISTENCY — references the art style, color palette, "
        "and visual rules from the style guide\n"
        "5. Captures the EMOTION — the feeling the image should evoke\n"
        "6. Maintains CHARACTER IDENTITY — always include exact appearance, clothing, "
        "and distinguishing features as specified in the character designs\n\n"
        "Your prompts should be detailed enough for an AI image generator to "
        "produce a high-quality, consistent result. Always reference the style "
        "guide to maintain visual coherence across all panels.\n\n"
        "Keep prompts under 500 words. Be specific and visual, not abstract."
    )

    def generate_panels(
        self,
        scripts: list[PanelScript],
        style_guide: VisualStyleGuide,
        output_dir: Path,
    ) -> list[GeneratedPanel]:
        """Generate all panel images (or prompts in mock mode)."""
        output_dir.mkdir(parents=True, exist_ok=True)
        generated = []
        # Track first appearance of each character for cross-panel consistency
        character_prompt_registry: dict[str, str] = {}

        total = sum(len(s.panels) for s in scripts)
        count = 0

        for script in scripts:
            for panel in script.panels:
                count += 1
                logger.info(
                    "Generating panel %d/%d (scene %d, panel %d)",
                    count, total, script.scene_number, panel.panel_number,
                )
                prompt = self._craft_image_prompt(
                    panel, script, style_guide, character_prompt_registry
                )

                # Compute deterministic seed if base seed is set
                seed = None
                if self.config.flux_seed is not None:
                    seed = (
                        self.config.flux_seed
                        + script.scene_number * 100
                        + panel.panel_number
                    )

                image_path = self._generate_image(
                    prompt, script.scene_number, panel.panel_number, output_dir,
                    seed=seed,
                )
                generated.append(
                    GeneratedPanel(
                        scene_number=script.scene_number,
                        panel_number=panel.panel_number,
                        image_prompt=prompt,
                        image_path=str(image_path),
                        alt_text=panel.visual_direction,
                        seed=seed,
                    )
                )

                # Register first appearances of characters in this panel
                panel_text = f"{panel.visual_direction} {panel.narration}"
                for cd in style_guide.character_designs:
                    if (
                        cd.character_name not in character_prompt_registry
                        and cd.character_name.lower() in panel_text.lower()
                    ):
                        character_prompt_registry[cd.character_name] = (
                            f"scene {script.scene_number}, panel {panel.panel_number}"
                        )

        return generated

    def _craft_image_prompt(
        self,
        panel: Panel,
        script: PanelScript,
        style_guide: VisualStyleGuide,
        character_prompt_registry: dict[str, str] | None = None,
    ) -> str:
        """Use Claude to craft a detailed image generation prompt."""
        # Build character designs block
        char_designs_block = ""
        if style_guide.character_designs:
            lines = ["CHARACTER DESIGNS:"]
            for cd in style_guide.character_designs:
                lines.append(f"- {cd.character_name}:")
                lines.append(f"  Appearance: {cd.appearance}")
                if cd.clothing:
                    lines.append(f"  Clothing: {cd.clothing}")
                if cd.distinguishing_features:
                    lines.append(
                        f"  Distinguishing features: {', '.join(cd.distinguishing_features)}"
                    )
                if cd.color_associations:
                    lines.append(
                        f"  Color associations: {', '.join(cd.color_associations)}"
                    )
            char_designs_block = "\n".join(lines) + "\n\n"

        # Build previously-established characters block
        prev_chars_block = ""
        if character_prompt_registry:
            panel_text = f"{panel.visual_direction} {panel.narration}"
            returning = [
                f"- {name} (first depicted in {location})"
                for name, location in character_prompt_registry.items()
                if name.lower() in panel_text.lower()
            ]
            if returning:
                prev_chars_block = (
                    "PREVIOUSLY ESTABLISHED CHARACTERS (maintain exact same appearance):\n"
                    + "\n".join(returning)
                    + "\n\n"
                )

        prompt = (
            f"Craft a detailed image generation prompt for this graphic novel panel.\n\n"
            f"SCENE: {script.scene_title}\n"
            f"PANEL {panel.panel_number} DIRECTION: {panel.visual_direction}\n"
            f"NARRATION: {panel.narration}\n\n"
            f"STYLE GUIDE:\n"
            f"- Art style: {style_guide.art_style}\n"
            f"- Color palette: {', '.join(style_guide.color_palette)}\n"
            f"- Mood: {style_guide.mood}\n"
            f"- Environment: {style_guide.environment_notes}\n"
            f"- Consistency rules: {'; '.join(style_guide.consistency_rules)}\n\n"
            f"{char_designs_block}"
            f"{prev_chars_block}"
            f"Return ONLY the image generation prompt text, nothing else. "
            f"Keep it under 500 words."
        )
        return self.invoke(prompt)

    def _generate_image(
        self, prompt: str, scene_num: int, panel_num: int, output_dir: Path,
        *, seed: int | None = None,
    ) -> Path:
        """Generate an image using the configured backend."""
        filename = f"scene{scene_num:02d}_panel{panel_num:02d}"

        if self.config.image_backend == "mock":
            return self._mock_generate(prompt, filename, output_dir, seed=seed)
        elif self.config.image_backend == "flux":
            return self._flux_generate(prompt, filename, output_dir, seed=seed)
        else:
            raise NotImplementedError(
                f"Image backend '{self.config.image_backend}' not yet implemented. "
                f"Use 'mock' or 'flux'."
            )

    def _mock_generate(
        self, prompt: str, filename: str, output_dir: Path,
        *, seed: int | None = None,
    ) -> Path:
        """Mock image generation — saves the prompt as a text file."""
        path = output_dir / f"{filename}.prompt.txt"
        seed_line = f"SEED: {seed}\n" if seed is not None else ""
        path.write_text(
            f"[MOCK IMAGE — would be generated by AI image API]\n\n"
            f"{seed_line}"
            f"IMAGE PROMPT:\n{prompt}\n",
            encoding="utf-8",
        )
        logger.info("Mock image saved: %s", path)
        return path

    _FLUX_MAX_RETRIES = 3
    _FLUX_RETRY_BACKOFF = 2.0
    _MIN_IMAGE_BYTES = 1024  # Reject suspiciously small images

    def _flux_generate(
        self, prompt: str, filename: str, output_dir: Path,
        *, seed: int | None = None,
    ) -> Path:
        """Generate an image using Flux via fal.ai API.

        Retries on transient failures with exponential backoff and validates
        that the downloaded image meets a minimum size threshold.
        """
        import fal_client

        model = self.config.flux_model
        logger.info("Calling Flux model via fal.ai: %s", model)

        arguments: dict = {
            "prompt": prompt,
            "image_size": self.config.flux_aspect_ratio,
            "num_images": 1,
            "output_format": "png",
            "guidance_scale": self.config.flux_guidance_scale,
            "num_inference_steps": self.config.flux_num_inference_steps,
        }
        if seed is not None:
            arguments["seed"] = seed
        if self.config.flux_negative_prompt:
            arguments["negative_prompt"] = self.config.flux_negative_prompt

        last_error = None
        for attempt in range(1, self._FLUX_MAX_RETRIES + 1):
            try:
                result = fal_client.subscribe(model, arguments=arguments)

                image_url = result["images"][0]["url"]

                # Download the image
                path = output_dir / f"{filename}.png"
                response = httpx.get(image_url, timeout=60.0)
                response.raise_for_status()

                if len(response.content) < self._MIN_IMAGE_BYTES:
                    raise ValueError(
                        f"Image too small ({len(response.content)} bytes), "
                        f"likely corrupted"
                    )

                path.write_bytes(response.content)

                # Also save the prompt alongside for reference
                prompt_path = output_dir / f"{filename}.prompt.txt"
                seed_line = f"SEED: {seed}\n" if seed is not None else ""
                prompt_path.write_text(
                    f"{seed_line}IMAGE PROMPT:\n{prompt}\n", encoding="utf-8"
                )

                logger.info(
                    "Flux image saved: %s (%d bytes)", path, len(response.content)
                )
                return path

            except Exception as e:
                last_error = e
                if attempt < self._FLUX_MAX_RETRIES:
                    wait = self._FLUX_RETRY_BACKOFF ** attempt
                    logger.warning(
                        "Flux generation failed (attempt %d/%d): %s — retrying in %.1fs",
                        attempt, self._FLUX_MAX_RETRIES, e, wait,
                    )
                    time.sleep(wait)

        raise RuntimeError(
            f"Flux image generation failed after {self._FLUX_MAX_RETRIES} attempts: "
            f"{last_error}"
        ) from last_error
