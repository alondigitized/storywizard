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

# Scenes to generate
SCENES = list(range(3, 16))  # 3-15 (1-2 already done)

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

    prompt += " No text, words, lettering, or typography in the image."

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

    prompt += " No text, words, lettering, or typography in the image."

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


def load_character_refs(novel_json: Path) -> dict[str, str]:
    """Load character reference URLs from novel.json character_designs.

    Returns a mapping of character_name -> reference_image_url.
    """
    if not novel_json.exists():
        return {}
    novel = json.loads(novel_json.read_text(encoding="utf-8"))
    style_guide = novel.get("style_guide", {})
    refs = {}
    for cd in style_guide.get("character_designs", []):
        url = cd.get("reference_image_url", "")
        if url:
            refs[cd["character_name"]] = url
    # Also load group references
    for gr in style_guide.get("group_references", []):
        url = gr.get("reference_image_url", "")
        if url:
            key = "+".join(sorted(gr["character_names"]))
            refs[f"group:{key}"] = url
    return refs


def select_reference_for_panel(
    prompt_text: str,
    character_refs: dict[str, str],
    style_anchor_url: str | None,
) -> tuple[str | None, str]:
    """Select best reference image for a panel.

    Returns (url, source_description).
    Priority: group ref > individual character ref > style anchor.
    """
    if not character_refs:
        return style_anchor_url, "style_anchor" if style_anchor_url else ""

    prompt_lower = prompt_text.lower()

    # Check group references first
    for key, url in character_refs.items():
        if key.startswith("group:"):
            names = key[6:].split("+")
            matches = sum(1 for n in names if n.lower() in prompt_lower)
            if matches >= 2:
                return url, key

    # Check individual character references
    for name, url in character_refs.items():
        if not name.startswith("group:") and name.lower() in prompt_lower:
            return url, f"character:{name}"

    # Fall back to style anchor
    if style_anchor_url:
        return style_anchor_url, "style_anchor"

    return None, ""


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Generate panels for Frankenstein")
    parser.add_argument(
        "--character-refs", action="store_true",
        help="Use character reference portraits from novel.json for consistency",
    )
    script_args = parser.parse_args()

    if not os.environ.get("FAL_KEY"):
        print("ERROR: FAL_KEY environment variable is required.", file=sys.stderr)
        sys.exit(1)

    # Load character references if requested
    character_refs: dict[str, str] = {}
    if script_args.character_refs:
        character_refs = load_character_refs(NOVEL_JSON)
        if character_refs:
            print(f"Loaded {len(character_refs)} character/group references from novel.json")
        else:
            print("WARNING: --character-refs specified but no references found in novel.json",
                  file=sys.stderr)

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
    if character_refs:
        print(f"  Character references: enabled ({len(character_refs)} refs)")
    print()

    generated_files = []

    # Use existing style anchor if available, otherwise generate with Recraft
    style_anchor_url: str | None = os.environ.get("STYLE_ANCHOR_URL")
    if style_anchor_url:
        print(f"Using existing style anchor: {style_anchor_url}")
        print()

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
            # Select reference: character ref > style anchor
            ref_url, ref_source = select_reference_for_panel(
                prompt, character_refs, style_anchor_url,
            )
            ref_label = f" [{ref_source}]" if ref_source != "style_anchor" else ""
            print(f"[{len(generated_files)+1}/{len(panels_to_generate)}] "
                  f"scene {scene_num}, panel {panel_num} (seed={seed}) — Kontext{ref_label}")
            png_bytes, cdn_url = generate_kontext(
                prompt, seed, image_url=ref_url or style_anchor_url,
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
