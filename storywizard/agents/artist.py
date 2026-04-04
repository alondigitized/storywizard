"""Artist agent — generates image prompts and calls image generation."""

from __future__ import annotations

import logging
import random
import subprocess
import time
from pathlib import Path

import httpx

from storywizard.agents.base import BaseAgent
from storywizard.models import (
    CharacterDesign,
    GeneratedPanel,
    Panel,
    PanelScript,
    VisualStyleGuide,
)

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
        "and distinguishing features as specified in the character designs\n"
        "7. NEVER include text, words, lettering, titles, captions, speech bubbles, "
        "or typography in the image — AI generators render text as illegible "
        "garbled shapes. All dialogue and narration will be overlaid separately.\n\n"
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
        # Style anchor: CDN URL of the first generated panel (Flux only)
        style_anchor_url: str | None = None

        total = sum(len(s.panels) for s in scripts)
        count = 0

        for script in scripts:
            for panel in script.panels:
                count += 1
                logger.info(
                    "Generating panel %d/%d (scene %d, panel %d)%s",
                    count, total, script.scene_number, panel.panel_number,
                    " (style anchor)" if style_anchor_url is None else "",
                )
                prompt = self._craft_image_prompt(
                    panel, script, style_guide, character_prompt_registry
                )

                # Compute deterministic seed if base seed is set
                seed = None
                base_seed = (
                    self.config.mflux_seed
                    if self.config.image_backend == "mflux"
                    else self.config.flux_seed
                )
                if base_seed is not None:
                    seed = (
                        base_seed
                        + script.scene_number * 100
                        + panel.panel_number
                    )

                # Select best reference image (character > group > style anchor)
                ref_url, ref_source, is_char_ref = self._select_reference_image(
                    panel, script, style_guide, style_anchor_url,
                )

                image_path, cdn_url = self._generate_image(
                    prompt, script.scene_number, panel.panel_number, output_dir,
                    seed=seed, reference_image_url=ref_url,
                    is_character_ref=is_char_ref, reference_source=ref_source,
                )

                # First panel becomes the style anchor for all subsequent panels
                if style_anchor_url is None and cdn_url is not None:
                    style_anchor_url = cdn_url
                    logger.info("Style anchor set: %s", cdn_url)

                generated.append(
                    GeneratedPanel(
                        scene_number=script.scene_number,
                        panel_number=panel.panel_number,
                        image_prompt=prompt,
                        image_path=str(image_path),
                        alt_text=panel.visual_direction,
                        seed=seed,
                        reference_source=ref_source,
                    )
                )

                # Register first appearances of characters in this panel
                panel_chars = self._detect_panel_characters(panel, style_guide)
                for char_name in panel_chars:
                    if char_name not in character_prompt_registry:
                        character_prompt_registry[char_name] = (
                            f"scene {script.scene_number}, panel {panel.panel_number}"
                        )

        return generated

    def _detect_panel_characters(
        self, panel: Panel, style_guide: VisualStyleGuide,
    ) -> list[str]:
        """Detect which characters are in a panel.

        Uses explicit panel.characters list if available, falls back to
        substring matching on visual_direction + narration.
        """
        if panel.characters:
            return panel.characters
        panel_text = f"{panel.visual_direction} {panel.narration}".lower()
        return [
            cd.character_name
            for cd in style_guide.character_designs
            if cd.character_name.lower() in panel_text
        ]

    def _select_reference_image(
        self,
        panel: Panel,
        script: PanelScript,
        style_guide: VisualStyleGuide,
        style_anchor_url: str | None,
    ) -> tuple[str | None, str, bool]:
        """Select the best reference image for this panel.

        Priority: group reference > individual character reference > style anchor.
        Returns (url, source_description, is_character_ref).
        """
        panel_chars = self._detect_panel_characters(panel, style_guide)
        panel_chars_set = set(panel_chars)

        # 1. Check group references — match if 2+ group members are present
        for group_ref in style_guide.group_references:
            overlap = panel_chars_set & set(group_ref.character_names)
            if len(overlap) >= 2 and group_ref.reference_image_url:
                source = f"group:{'+'.join(sorted(group_ref.character_names))}"
                logger.debug("Using group reference for panel %d: %s", panel.panel_number, source)
                return group_ref.reference_image_url, source, True

        # 2. Check individual character references — use primary character
        for char_name in panel_chars:
            for cd in style_guide.character_designs:
                if cd.character_name == char_name and cd.reference_image_url:
                    source = f"character:{cd.character_name}"
                    logger.debug("Using character reference for panel %d: %s", panel.panel_number, source)
                    return cd.reference_image_url, source, True

        # 3. Fall back to style anchor
        if style_anchor_url:
            return style_anchor_url, "style_anchor", False

        return None, "", False

    def _build_character_identity_block(
        self,
        panel: Panel,
        style_guide: VisualStyleGuide,
    ) -> str:
        """Build a frozen, verbatim character identity block for prompt injection.

        Unlike the Claude-rephrased approach, this produces a deterministic text
        block that is inserted into every prompt unchanged. This ensures mflux
        (which has no reference image input) sees identical character descriptions
        across all panels, maximizing visual consistency.
        """
        panel_chars = self._detect_panel_characters(panel, style_guide)
        if not panel_chars:
            return ""

        lines = []
        for char_name in panel_chars:
            for cd in style_guide.character_designs:
                if cd.character_name == char_name:
                    parts = [cd.appearance]
                    if cd.clothing:
                        parts.append(cd.clothing)
                    if cd.distinguishing_features:
                        parts.append(", ".join(cd.distinguishing_features))
                    if cd.color_associations:
                        parts.append(
                            "color palette: " + ", ".join(cd.color_associations)
                        )
                    lines.append(f"{cd.character_name}: {'; '.join(parts)}")
                    break

        if not lines:
            return ""
        return "CHARACTERS IN SCENE — " + " | ".join(lines)

    def _craft_image_prompt(
        self,
        panel: Panel,
        script: PanelScript,
        style_guide: VisualStyleGuide,
        character_prompt_registry: dict[str, str] | None = None,
    ) -> str:
        """Use Claude to craft a detailed image generation prompt.

        For the mflux backend, the prompt is structured to maximize character
        consistency without reference images: a frozen character identity block
        is injected verbatim, and Claude is instructed to incorporate it exactly
        rather than paraphrasing.
        """
        is_mflux = self.config.image_backend == "mflux"

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

        # For mflux: build the frozen identity block appended at the end
        identity_anchor = ""
        consistency_instruction = ""
        if is_mflux:
            identity_anchor = self._build_character_identity_block(panel, style_guide)
            if identity_anchor:
                consistency_instruction = (
                    "\n\nPROMPT STRUCTURE RULE: Your prompt MUST follow this exact structure:\n"
                    f"1. FIRST LINE — art style declaration: \"{style_guide.art_style[:150]}\"\n"
                    f"2. SCENE CONTENT — the specific composition, action, camera angle, "
                    "environment, and lighting unique to THIS panel (this is the bulk)\n"
                    f"3. CHARACTER DETAILS — include verbatim: {identity_anchor}\n"
                    "The art style MUST appear in the first sentence. "
                    "The scene content MUST be unique and specific to this panel — "
                    "do not repeat generic descriptions across panels."
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
            f"{consistency_instruction}\n\n"
            f"Return ONLY the image generation prompt text, nothing else. "
            f"Keep it under 500 words.\n\n"
            f"IMPORTANT: Do NOT include any text, words, lettering, or speech bubbles "
            f"in the prompt — text will be added separately in post-production."
        )
        return self.invoke(prompt)

    def _generate_image(
        self, prompt: str, scene_num: int, panel_num: int, output_dir: Path,
        *, seed: int | None = None, reference_image_url: str | None = None,
        is_character_ref: bool = False, reference_source: str = "",
    ) -> tuple[Path, str | None]:
        """Generate an image using the configured backend.

        Returns (local_path, cdn_url). cdn_url is None for mock backend.
        When is_character_ref is True and backend is "flux", routes to Kontext
        instead of flux-general for character-consistent generation.
        """
        filename = f"scene{scene_num:02d}_panel{panel_num:02d}"

        if self.config.image_backend == "mock":
            return self._mock_generate(
                prompt, filename, output_dir,
                seed=seed, reference_source=reference_source,
            ), None
        elif self.config.image_backend == "flux":
            if is_character_ref and reference_image_url:
                return self._kontext_generate(
                    prompt, filename, output_dir,
                    seed=seed, image_url=reference_image_url,
                )
            return self._flux_generate(
                prompt, filename, output_dir,
                seed=seed, reference_image_url=reference_image_url,
            )
        elif self.config.image_backend == "mflux":
            return self._mflux_generate(
                prompt, filename, output_dir, seed=seed,
            ), None
        else:
            raise NotImplementedError(
                f"Image backend '{self.config.image_backend}' not yet implemented. "
                f"Use 'mock', 'flux', or 'mflux'."
            )

    def _mock_generate(
        self, prompt: str, filename: str, output_dir: Path,
        *, seed: int | None = None, reference_source: str = "",
    ) -> Path:
        """Mock image generation — saves the prompt as a text file."""
        path = output_dir / f"{filename}.prompt.txt"
        seed_line = f"SEED: {seed}\n" if seed is not None else ""
        ref_line = f"REFERENCE: {reference_source}\n" if reference_source else ""
        path.write_text(
            f"[MOCK IMAGE — would be generated by AI image API]\n\n"
            f"{seed_line}"
            f"{ref_line}"
            f"IMAGE PROMPT:\n{prompt}\n",
            encoding="utf-8",
        )
        logger.info("Mock image saved: %s", path)
        return path

    def _mflux_generate(
        self, prompt: str, filename: str, output_dir: Path,
        *, seed: int | None = None,
    ) -> Path:
        """Generate an image locally using mflux on Apple Silicon.

        Routes to mflux-generate-flux2 (Klein 4B, 4 steps) or
        mflux-generate-z-image-turbo (9 steps) based on config.
        """
        path = output_dir / f"{filename}.png"

        if seed is None:
            seed = random.randint(0, 2**31 - 1)

        model = self.config.mflux_model
        if model == "turbo":
            cmd = "mflux-generate-z-image-turbo"
            steps = 9
        else:
            cmd = "mflux-generate-flux2"
            steps = 4

        args = [
            cmd,
            "--prompt", prompt,
            "--width", str(self.config.mflux_width),
            "--height", str(self.config.mflux_height),
            "--steps", str(steps),
            "--seed", str(seed),
            "--output", str(path),
        ]

        logger.info(
            "Calling mflux (%s, %dx%d, seed=%d): %s",
            model, self.config.mflux_width, self.config.mflux_height, seed, filename,
        )

        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=1200,  # 20 minute timeout (turbo at 1024x768 takes ~13 min)
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"mflux exited with code {result.returncode}: {result.stderr}"
                )
        except FileNotFoundError:
            raise RuntimeError(
                f"mflux command '{cmd}' not found. Install with: pip install mflux"
            )

        if not path.exists() or path.stat().st_size < 1024:
            raise RuntimeError(
                f"mflux produced no valid image at {path}. "
                f"stderr: {result.stderr[:500] if result.stderr else '(empty)'}"
            )

        # Save prompt alongside for reference
        prompt_path = output_dir / f"{filename}.prompt.txt"
        prompt_path.write_text(
            f"SEED: {seed}\nMODEL: mflux-{model}\n"
            f"SIZE: {self.config.mflux_width}x{self.config.mflux_height}\n"
            f"IMAGE PROMPT:\n{prompt}\n",
            encoding="utf-8",
        )

        logger.info(
            "mflux image saved: %s (%d bytes)", path, path.stat().st_size,
        )
        return path

    _FLUX_MAX_RETRIES = 3
    _FLUX_RETRY_BACKOFF = 2.0
    _MIN_IMAGE_BYTES = 1024  # Reject suspiciously small images

    def _flux_generate(
        self, prompt: str, filename: str, output_dir: Path,
        *, seed: int | None = None, reference_image_url: str | None = None,
    ) -> tuple[Path, str]:
        """Generate an image using Flux via fal.ai API.

        Retries on transient failures with exponential backoff and validates
        that the downloaded image meets a minimum size threshold.

        Returns (local_path, cdn_url) so the CDN URL can be used as a style
        anchor for subsequent panels.
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
        if reference_image_url:
            # negative_prompt (NAG) is incompatible with reference_image on flux-general
            arguments["reference_image_url"] = reference_image_url
            arguments["reference_strength"] = self.config.flux_reference_strength
        elif self.config.flux_negative_prompt:
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
                return path, image_url

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

    def _kontext_generate(
        self, prompt: str, filename: str, output_dir: Path,
        *, seed: int | None = None, image_url: str,
    ) -> tuple[Path, str]:
        """Generate an image using FLUX Pro Kontext for character consistency.

        Uses a character/group reference image via image_url to maintain
        character identity across panels.

        Returns (local_path, cdn_url).
        """
        import fal_client

        model = self.config.kontext_model
        logger.info("Calling Kontext model via fal.ai: %s", model)

        prompt_with_suffix = prompt + " No text, words, lettering, or typography in the image."

        arguments: dict = {
            "prompt": prompt_with_suffix,
            "image_url": image_url,
            "guidance_scale": self.config.kontext_guidance_scale,
            "num_images": 1,
            "output_format": "png",
            "aspect_ratio": "16:9",
            "safety_tolerance": "6",
        }
        if seed is not None:
            arguments["seed"] = seed

        last_error = None
        for attempt in range(1, self._FLUX_MAX_RETRIES + 1):
            try:
                result = fal_client.subscribe(model, arguments=arguments)
                result_url = result["images"][0]["url"]

                path = output_dir / f"{filename}.png"
                response = httpx.get(result_url, timeout=60.0)
                response.raise_for_status()

                if len(response.content) < self._MIN_IMAGE_BYTES:
                    raise ValueError(
                        f"Image too small ({len(response.content)} bytes), "
                        f"likely corrupted"
                    )

                path.write_bytes(response.content)

                # Save prompt alongside for reference
                prompt_path = output_dir / f"{filename}.prompt.txt"
                seed_line = f"SEED: {seed}\n" if seed is not None else ""
                prompt_path.write_text(
                    f"{seed_line}IMAGE PROMPT:\n{prompt}\n", encoding="utf-8"
                )

                logger.info(
                    "Kontext image saved: %s (%d bytes)", path, len(response.content)
                )
                return path, result_url

            except Exception as e:
                last_error = e
                if attempt < self._FLUX_MAX_RETRIES:
                    wait = self._FLUX_RETRY_BACKOFF ** attempt
                    logger.warning(
                        "Kontext generation failed (attempt %d/%d): %s — retrying in %.1fs",
                        attempt, self._FLUX_MAX_RETRIES, e, wait,
                    )
                    time.sleep(wait)

        raise RuntimeError(
            f"Kontext image generation failed after {self._FLUX_MAX_RETRIES} attempts: "
            f"{last_error}"
        ) from last_error
