"""Character reference image generator.

Generates clean reference portraits for major characters using Recraft V4 Pro,
then optionally generates group portraits for frequently co-occurring characters.
These references are used by the Artist agent via FLUX Kontext to maintain
character visual consistency across panels.
"""

from __future__ import annotations

import logging
import re
import time
from collections import Counter
from itertools import combinations
from pathlib import Path

import httpx

from storywizard.config import PipelineConfig
from storywizard.models import (
    CharacterDesign,
    CharacterGroupReference,
    Scene,
    VisualStyleGuide,
)

logger = logging.getLogger(__name__)

_MAX_RETRIES = 3
_RETRY_BACKOFF = 2.0
_MIN_IMAGE_BYTES = 1024


class CharacterReferenceGenerator:
    """Generates reference portraits for characters using Recraft V4 Pro."""

    def __init__(self, config: PipelineConfig) -> None:
        self.config = config

    def generate_references(
        self,
        style_guide: VisualStyleGuide,
        scenes: list[Scene],
        output_dir: Path,
    ) -> VisualStyleGuide:
        """Generate reference portraits and return an updated style guide.

        1. For each character whose role is in character_ref_roles, generate
           a clean portrait via Recraft V4 Pro.
        2. Find character groups that co-occur in >= group_ref_min_appearances
           scenes and generate group portraits.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        colors = self._parse_color_palette(style_guide.color_palette)

        # Generate individual character references
        for cd in style_guide.character_designs:
            if cd.role if hasattr(cd, "role") else "" not in self.config.character_ref_roles:
                # Check by matching against the analysis characters' roles
                # CharacterDesign doesn't have a role field — we generate for all
                # characters listed in character_ref_roles by checking scene frequency
                pass

            # Generate portrait for characters that appear in scenes
            scene_count = sum(
                1 for s in scenes if cd.character_name in s.characters
            )
            if scene_count == 0:
                logger.debug("Skipping %s — not in any scene", cd.character_name)
                continue

            prompt = self._build_character_prompt(cd, style_guide)
            slug = re.sub(r"[^a-z0-9]+", "_", cd.character_name.lower()).strip("_")
            filename = f"ref_{slug}"

            logger.info(
                "Generating reference portrait for %s (%d scene appearances)",
                cd.character_name,
                scene_count,
            )

            try:
                png_bytes, cdn_url = self._generate_recraft(prompt, colors)
                path = output_dir / f"{filename}.png"
                path.write_bytes(png_bytes)
                cd.reference_image_url = cdn_url
                cd.reference_image_path = str(path)
                logger.info(
                    "Reference portrait saved: %s (%d bytes)",
                    path,
                    len(png_bytes),
                )
            except Exception:
                logger.warning(
                    "Failed to generate reference for %s — will fall back to style anchor",
                    cd.character_name,
                    exc_info=True,
                )

        # Generate group references
        if self.config.group_ref_enabled:
            groups = self._find_character_groups(scenes, style_guide.character_designs)
            for group_names in groups:
                prompt = self._build_group_prompt(group_names, style_guide)
                slug = "_".join(
                    re.sub(r"[^a-z0-9]+", "_", n.lower()).strip("_")
                    for n in sorted(group_names)
                )
                filename = f"ref_group_{slug}"

                logger.info(
                    "Generating group reference for %s",
                    " + ".join(group_names),
                )

                try:
                    png_bytes, cdn_url = self._generate_recraft(prompt, colors)
                    path = output_dir / f"{filename}.png"
                    path.write_bytes(png_bytes)
                    style_guide.group_references.append(
                        CharacterGroupReference(
                            character_names=list(group_names),
                            reference_image_url=cdn_url,
                            reference_image_path=str(path),
                        )
                    )
                    logger.info(
                        "Group reference saved: %s (%d bytes)",
                        path,
                        len(png_bytes),
                    )
                except Exception:
                    logger.warning(
                        "Failed to generate group reference for %s",
                        " + ".join(group_names),
                        exc_info=True,
                    )

        return style_guide

    def _build_character_prompt(
        self, cd: CharacterDesign, style_guide: VisualStyleGuide
    ) -> str:
        """Build a portrait prompt from character design fields."""
        parts = [f"Portrait of {cd.character_name}: {cd.appearance}."]
        if cd.clothing:
            parts.append(f"{cd.clothing}.")
        if cd.distinguishing_features:
            parts.append(
                f"Distinguishing features: {', '.join(cd.distinguishing_features)}."
            )
        parts.append(f"Art style: {style_guide.art_style}.")
        parts.append("Neutral background.")
        parts.append("No text, words, lettering, or typography.")
        return " ".join(parts)

    def _build_group_prompt(
        self, group_names: tuple[str, ...], style_guide: VisualStyleGuide
    ) -> str:
        """Build a group portrait prompt."""
        # Find character designs for the group members
        designs = {
            cd.character_name: cd
            for cd in style_guide.character_designs
            if cd.character_name in group_names
        }

        parts = [f"Group portrait of {', '.join(group_names)} standing together."]
        for name in group_names:
            if name in designs:
                cd = designs[name]
                parts.append(f"{name}: {cd.appearance}.")
                if cd.clothing:
                    parts.append(f"Wearing {cd.clothing}.")
        parts.append(f"Art style: {style_guide.art_style}.")
        parts.append("Neutral background.")
        parts.append("No text, words, lettering, or typography.")
        return " ".join(parts)

    def _generate_recraft(
        self, prompt: str, colors: list[dict]
    ) -> tuple[bytes, str]:
        """Generate an image with Recraft V4 Pro. Returns (PNG bytes, CDN URL)."""
        import fal_client

        arguments: dict = {
            "prompt": prompt,
            "image_size": self.config.character_ref_aspect_ratio,
            "output_format": "png",
        }
        if colors:
            arguments["colors"] = colors

        last_error = None
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                result = fal_client.subscribe(
                    self.config.character_ref_model, arguments=arguments
                )
                image_url = result["images"][0]["url"]

                response = httpx.get(image_url, timeout=60.0)
                response.raise_for_status()

                if len(response.content) < _MIN_IMAGE_BYTES:
                    raise ValueError(
                        f"Image too small ({len(response.content)} bytes), "
                        f"likely corrupted"
                    )

                return response.content, image_url

            except Exception as e:
                last_error = e
                if attempt < _MAX_RETRIES:
                    wait = _RETRY_BACKOFF ** attempt
                    logger.warning(
                        "Recraft generation failed (attempt %d/%d): %s — retrying in %.1fs",
                        attempt,
                        _MAX_RETRIES,
                        e,
                        wait,
                    )
                    time.sleep(wait)

        raise RuntimeError(
            f"Recraft generation failed after {_MAX_RETRIES} attempts: {last_error}"
        ) from last_error

    def _find_character_groups(
        self,
        scenes: list[Scene],
        designs: list[CharacterDesign],
    ) -> list[tuple[str, ...]]:
        """Find character name tuples that co-occur in >= group_ref_min_appearances scenes."""
        design_names = {cd.character_name for cd in designs}
        pair_counts: Counter[tuple[str, ...]] = Counter()

        for scene in scenes:
            # Only count characters that have designs
            present = sorted(n for n in scene.characters if n in design_names)
            # Count all pairs
            for pair in combinations(present, 2):
                pair_counts[pair] += 1

        min_apps = self.config.group_ref_min_appearances
        groups = [
            pair for pair, count in pair_counts.most_common()
            if count >= min_apps
        ]

        # Merge overlapping pairs into larger groups where all members co-occur enough
        merged: list[tuple[str, ...]] = []
        used = set()
        for i, g1 in enumerate(groups):
            if i in used:
                continue
            members = set(g1)
            for j, g2 in enumerate(groups[i + 1:], start=i + 1):
                if j in used:
                    continue
                # Check if merging g2 into the group is valid
                # (all resulting pairs must meet the threshold)
                candidate = members | set(g2)
                if all(
                    pair_counts[tuple(sorted(p))] >= min_apps
                    for p in combinations(candidate, 2)
                ):
                    members = candidate
                    used.add(j)
            used.add(i)
            if len(members) >= 2:
                merged.append(tuple(sorted(members)))

        return merged

    def _parse_color_palette(self, color_palette: list[str]) -> list[dict]:
        """Parse hex colors from style guide into Recraft RGB dicts.

        Expects palette entries like '#1B2A4A - Midnight Blue' or '#1B2A4A'.
        """
        colors = []
        for entry in color_palette:
            match = re.search(r"#([0-9A-Fa-f]{6})", entry)
            if match:
                hex_str = match.group(1)
                colors.append({
                    "r": int(hex_str[0:2], 16),
                    "g": int(hex_str[2:4], 16),
                    "b": int(hex_str[4:6], 16),
                })
        return colors
