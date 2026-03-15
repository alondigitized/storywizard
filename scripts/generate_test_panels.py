#!/usr/bin/env python3
"""Generate high-quality panels for scenes 1-2 of Frankenstein.

Uses a hybrid approach for visual consistency:
  - Panel 1: Recraft V4 Pro (highest quality, color palette from style guide)
  - Panels 2+: FLUX Pro Kontext (style-anchored to panel 1 via image_url)

Reads existing .prompt.txt files, extracts the image prompt, calls fal.ai
to generate PNGs, and updates novel.json to point to the new images.

Usage:
    FAL_KEY=your-key python scripts/generate_test_panels.py
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

import httpx

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "frankenstein"
PANELS_DIR = DATA_DIR / "panels"
NOVEL_JSON = DATA_DIR / "novel.json"

# Scenes to generate (1 and 2)
SCENES = [1, 2]

# Model settings
RECRAFT_MODEL = "fal-ai/recraft/v4/pro/text-to-image"
KONTEXT_MODEL = "fal-ai/flux-pro/kontext"
KONTEXT_GUIDANCE_SCALE = 4.0
BASE_SEED = 42  # seed = 42 + scene*100 + panel

# Frankenstein style guide color palette (RGB tuples from hex)
STYLE_COLORS = [
    {"r": 27, "g": 42, "b": 74},     # Midnight Prussian Blue #1B2A4A
    {"r": 197, "g": 196, "b": 106},   # Corpse Yellow-Green #C5C46A
    {"r": 110, "g": 110, "b": 110},   # Charnel Ash Grey #6E6E6E
    {"r": 139, "g": 26, "b": 26},     # Blood Crimson #8B1A1A
    {"r": 212, "g": 136, "b": 42},    # Amber Candlelight #D4882A
]

MAX_RETRIES = 3
RETRY_BACKOFF = 2.0
MIN_IMAGE_BYTES = 1024


def extract_prompt(text: str) -> str:
    """Extract the raw image prompt from a .prompt.txt file.

    Strips the [MOCK IMAGE...] header and IMAGE PROMPT: prefix.
    Also strips any SEED: line.
    """
    # Remove [MOCK IMAGE ...] header line
    text = re.sub(r"^\[MOCK IMAGE[^\]]*\]\s*\n*", "", text)
    # Remove SEED: line
    text = re.sub(r"^SEED:\s*\d+\s*\n*", "", text, flags=re.MULTILINE)
    # Remove IMAGE PROMPT: prefix
    text = re.sub(r"^IMAGE PROMPT:\s*\n?", "", text)
    return text.strip()


def generate_recraft(prompt: str) -> tuple[bytes, str]:
    """Generate with Recraft V4 Pro. Returns (PNG bytes, CDN URL)."""
    import fal_client

    arguments = {
        "prompt": prompt,
        "image_size": "landscape_16_9",
        "output_format": "png",
        "colors": STYLE_COLORS,
    }

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = fal_client.subscribe(RECRAFT_MODEL, arguments=arguments)
            image_url = result["images"][0]["url"]

            response = httpx.get(image_url, timeout=60.0)
            response.raise_for_status()

            if len(response.content) < MIN_IMAGE_BYTES:
                raise ValueError(
                    f"Image too small ({len(response.content)} bytes), likely corrupted"
                )

            return response.content, image_url

        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES:
                wait = RETRY_BACKOFF**attempt
                print(f"  Attempt {attempt}/{MAX_RETRIES} failed: {e} — retrying in {wait:.1f}s")
                time.sleep(wait)

    raise RuntimeError(
        f"Recraft generation failed after {MAX_RETRIES} attempts: {last_error}"
    ) from last_error


def generate_kontext(
    prompt: str, seed: int, *, image_url: str,
) -> tuple[bytes, str]:
    """Generate with FLUX Pro Kontext. Returns (PNG bytes, CDN URL)."""
    import fal_client

    arguments = {
        "prompt": prompt,
        "image_url": image_url,
        "guidance_scale": KONTEXT_GUIDANCE_SCALE,
        "seed": seed,
        "num_images": 1,
        "output_format": "png",
        "aspect_ratio": "16:9",
        "safety_tolerance": "6",
    }

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = fal_client.subscribe(KONTEXT_MODEL, arguments=arguments)
            result_url = result["images"][0]["url"]

            response = httpx.get(result_url, timeout=60.0)
            response.raise_for_status()

            if len(response.content) < MIN_IMAGE_BYTES:
                raise ValueError(
                    f"Image too small ({len(response.content)} bytes), likely corrupted"
                )

            return response.content, result_url

        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES:
                wait = RETRY_BACKOFF**attempt
                print(f"  Attempt {attempt}/{MAX_RETRIES} failed: {e} — retrying in {wait:.1f}s")
                time.sleep(wait)

    raise RuntimeError(
        f"Kontext generation failed after {MAX_RETRIES} attempts: {last_error}"
    ) from last_error


def main() -> None:
    if not os.environ.get("FAL_KEY"):
        print("ERROR: FAL_KEY environment variable is required.", file=sys.stderr)
        sys.exit(1)

    # Discover panels for target scenes
    panels_to_generate = []
    for scene in SCENES:
        scene_files = sorted(PANELS_DIR.glob(f"scene{scene:02d}_panel*.prompt.txt"))
        if not scene_files:
            print(f"WARNING: No prompt files found for scene {scene}", file=sys.stderr)
            continue
        for f in scene_files:
            match = re.match(r"scene(\d+)_panel(\d+)\.prompt\.txt", f.name)
            if match:
                panels_to_generate.append((int(match.group(1)), int(match.group(2)), f))

    if not panels_to_generate:
        print("ERROR: No panels found to generate.", file=sys.stderr)
        sys.exit(1)

    print(f"Generating {len(panels_to_generate)} panels for scenes {SCENES}")
    print(f"  Panel 1: Recraft V4 Pro (style anchor with color palette)")
    print(f"  Panels 2-{len(panels_to_generate)}: FLUX Pro Kontext (style-anchored)")
    print()

    generated_files = []
    style_anchor_url: str | None = None

    for scene_num, panel_num, prompt_file in panels_to_generate:
        seed = BASE_SEED + scene_num * 100 + panel_num
        png_path = prompt_file.parent / f"scene{scene_num:02d}_panel{panel_num:02d}.png"

        # Extract prompt
        raw_text = prompt_file.read_text(encoding="utf-8")
        prompt = extract_prompt(raw_text)

        if style_anchor_url is None:
            # First panel: Recraft V4 Pro
            print(f"[{len(generated_files)+1}/{len(panels_to_generate)}] "
                  f"scene {scene_num}, panel {panel_num} — Recraft V4 Pro (style anchor)")
            png_bytes, cdn_url = generate_recraft(prompt)
            style_anchor_url = cdn_url
            print(f"  Style anchor URL: {cdn_url}")
        else:
            # Subsequent panels: FLUX Pro Kontext
            print(f"[{len(generated_files)+1}/{len(panels_to_generate)}] "
                  f"scene {scene_num}, panel {panel_num} (seed={seed}) — Kontext")
            png_bytes, cdn_url = generate_kontext(
                prompt, seed, image_url=style_anchor_url,
            )

        png_path.write_bytes(png_bytes)
        print(f"  Saved: {png_path.name} ({len(png_bytes):,} bytes)")

        generated_files.append((scene_num, panel_num, png_path))

    # Update novel.json — change image_path for generated panels
    print()
    print("Updating novel.json...")
    novel = json.loads(NOVEL_JSON.read_text(encoding="utf-8"))

    updated_count = 0
    generated_set = {(s, p) for s, p, _ in generated_files}
    for gp in novel["generated_panels"]:
        key = (gp["scene_number"], gp["panel_number"])
        if key in generated_set:
            scene_num, panel_num = key
            new_path = f"panels/scene{scene_num:02d}_panel{panel_num:02d}.png"
            old_path = gp["image_path"]
            gp["image_path"] = new_path
            print(f"  {old_path} -> {new_path}")
            updated_count += 1

    NOVEL_JSON.write_text(
        json.dumps(novel, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"\nDone! Updated {updated_count} panel paths in novel.json.")
    print(f"Generated {len(generated_files)} PNGs in {PANELS_DIR}")


if __name__ == "__main__":
    main()
