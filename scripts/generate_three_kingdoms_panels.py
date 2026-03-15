#!/usr/bin/env python3
"""Generate panels for Romance of the Three Kingdoms scenes 1-2.

Uses character reference portraits for visual consistency:
  1. Generate reference portraits for major characters (Recraft V4 Pro)
  2. Generate scene panels using character refs (FLUX Pro Kontext)

Usage:
    FAL_KEY=your-key python scripts/generate_three_kingdoms_panels.py
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

import httpx

NOVEL_DIR = Path(__file__).resolve().parent.parent / "output" / "romance-of-the-three-kingdoms"
PANELS_DIR = NOVEL_DIR / "panels"
REFS_DIR = NOVEL_DIR / "character_refs"
NOVEL_JSON = NOVEL_DIR / "novel.json"

# Scenes to generate
SCENES = [1, 2]

# Model settings
RECRAFT_MODEL = "fal-ai/recraft/v4/pro/text-to-image"
KONTEXT_MODEL = "fal-ai/flux-pro/kontext"
KONTEXT_GUIDANCE_SCALE = 4.0
BASE_SEED = 77  # Three Kingdoms seed

MAX_RETRIES = 3
RETRY_BACKOFF = 2.0
MIN_IMAGE_BYTES = 1024


def parse_hex_colors(palette: list[str]) -> list[dict]:
    """Parse hex colors from style guide palette into Recraft RGB dicts."""
    colors = []
    for entry in palette:
        match = re.search(r"#([0-9A-Fa-f]{6})", entry)
        if match:
            h = match.group(1)
            colors.append({"r": int(h[0:2], 16), "g": int(h[2:4], 16), "b": int(h[4:6], 16)})
    return colors


def generate_recraft(prompt: str, colors: list[dict], aspect: str = "portrait_4_3") -> tuple[bytes, str]:
    """Generate with Recraft V4 Pro. Returns (PNG bytes, CDN URL)."""
    import fal_client

    arguments: dict = {
        "prompt": prompt,
        "image_size": aspect,
        "output_format": "png",
    }
    if colors:
        arguments["colors"] = colors

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = fal_client.subscribe(RECRAFT_MODEL, arguments=arguments)
            image_url = result["images"][0]["url"]
            response = httpx.get(image_url, timeout=60.0)
            response.raise_for_status()
            if len(response.content) < MIN_IMAGE_BYTES:
                raise ValueError(f"Image too small ({len(response.content)} bytes)")
            return response.content, image_url
        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES:
                wait = RETRY_BACKOFF ** attempt
                print(f"  Attempt {attempt}/{MAX_RETRIES} failed: {e} — retrying in {wait:.1f}s")
                time.sleep(wait)
    raise RuntimeError(f"Recraft failed after {MAX_RETRIES} attempts: {last_error}") from last_error


def generate_kontext(prompt: str, seed: int, *, image_url: str) -> tuple[bytes, str]:
    """Generate with FLUX Pro Kontext. Returns (PNG bytes, CDN URL)."""
    import fal_client

    arguments = {
        "prompt": prompt + " No text, words, lettering, or typography in the image.",
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
                raise ValueError(f"Image too small ({len(response.content)} bytes)")
            return response.content, result_url
        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES:
                wait = RETRY_BACKOFF ** attempt
                print(f"  Attempt {attempt}/{MAX_RETRIES} failed: {e} — retrying in {wait:.1f}s")
                time.sleep(wait)
    raise RuntimeError(f"Kontext failed after {MAX_RETRIES} attempts: {last_error}") from last_error


def extract_prompt(text: str) -> str:
    """Extract the raw image prompt from a .prompt.txt file."""
    text = re.sub(r"^\[MOCK IMAGE[^\]]*\]\s*\n*", "", text)
    text = re.sub(r"^SEED:\s*\d+\s*\n*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^REFERENCE:.*\n*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^IMAGE PROMPT:\s*\n?", "", text)
    return text.strip()


def build_character_prompt(cd: dict, art_style: str) -> str:
    """Build a portrait prompt from a character design dict."""
    parts = [f"Portrait of {cd['character_name']}: {cd['appearance']}."]
    if cd.get("clothing"):
        parts.append(f"{cd['clothing']}.")
    if cd.get("distinguishing_features"):
        parts.append(f"Distinguishing features: {', '.join(cd['distinguishing_features'])}.")
    parts.append(f"Art style: {art_style}.")
    parts.append("Neutral background. No text, words, lettering, or typography.")
    return " ".join(parts)


def detect_characters_in_prompt(prompt: str, character_names: list[str]) -> list[str]:
    """Find which characters are mentioned in a prompt.

    Matches on full name OR any individual word in the name (e.g. "Liu" matches
    "Liu Pei (Liu Yuan-te)"), but skips short words and parentheses.
    """
    prompt_lower = prompt.lower()
    found = []
    for name in character_names:
        # Try full name first
        if name.lower() in prompt_lower:
            found.append(name)
            continue
        # Try individual name parts (skip short words and parens)
        parts = re.findall(r"[A-Za-z]{3,}", name)
        for part in parts:
            # Use word boundary to avoid false matches
            if re.search(r"\b" + re.escape(part.lower()) + r"\b", prompt_lower):
                found.append(name)
                break
    return found


def select_reference(
    panel_chars: list[str],
    char_refs: dict[str, str],
    group_refs: dict[str, str],
    style_anchor_url: str | None,
) -> tuple[str | None, str]:
    """Select best reference: group > individual > style anchor."""
    # Check group refs (2+ members present)
    for key, url in group_refs.items():
        names = key.split("+")
        if sum(1 for n in names if n in panel_chars) >= 2:
            return url, f"group:{key}"

    # Check individual refs
    for name in panel_chars:
        if name in char_refs:
            return char_refs[name], f"character:{name}"

    # Style anchor fallback
    if style_anchor_url:
        return style_anchor_url, "style_anchor"

    return None, ""


def main() -> None:
    if not os.environ.get("FAL_KEY"):
        print("ERROR: FAL_KEY environment variable is required.", file=sys.stderr)
        sys.exit(1)

    # Load novel data
    novel = json.loads(NOVEL_JSON.read_text(encoding="utf-8"))
    style_guide = novel["style_guide"]
    art_style = style_guide["art_style"]
    colors = parse_hex_colors(style_guide["color_palette"])

    # Characters to generate references for (the three sworn brothers + Tsao Tsao)
    # These are the ones most likely to appear in scenes 1-2
    priority_characters = ["Liu Pei (Liu Yuan-te)", "Kuan Yu (Yun-chang)", "Chang Fei (I-te)"]
    all_designs = {cd["character_name"]: cd for cd in style_guide["character_designs"]}

    REFS_DIR.mkdir(parents=True, exist_ok=True)

    # ── Phase 1: Generate character reference portraits ──
    print("=" * 60)
    print("PHASE 1: Character Reference Portraits (Recraft V4 Pro)")
    print("=" * 60)
    print()

    char_refs: dict[str, str] = {}  # name -> CDN URL

    # Check if refs already exist in novel.json (from a previous run)
    existing_refs = {
        cd["character_name"]: cd.get("reference_image_url", "")
        for cd in style_guide["character_designs"]
        if cd.get("reference_image_url")
    }

    for i, name in enumerate(priority_characters):
        cd = all_designs.get(name)
        if not cd:
            print(f"WARNING: No design found for '{name}', skipping")
            continue

        # Reuse existing ref if available
        if name in existing_refs and existing_refs[name]:
            char_refs[name] = existing_refs[name]
            print(f"[{i+1}/{len(priority_characters)}] {name} — reusing existing ref")
            print(f"  CDN: {existing_refs[name]}")
            print()
            continue

        slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
        png_path = REFS_DIR / f"ref_{slug}.png"

        prompt = build_character_prompt(cd, art_style)
        print(f"[{i+1}/{len(priority_characters)}] {name}")
        print(f"  Prompt: {prompt[:120]}...")

        png_bytes, cdn_url = generate_recraft(prompt, colors)
        png_path.write_bytes(png_bytes)
        char_refs[name] = cdn_url
        print(f"  Saved: {png_path.name} ({len(png_bytes):,} bytes)")
        print(f"  CDN: {cdn_url}")
        print()

    # ── Phase 1.5: Generate group portrait of the three brothers ──
    print("=" * 60)
    print("PHASE 1.5: Group Reference Portrait")
    print("=" * 60)
    print()

    group_refs: dict[str, str] = {}  # "A+B+C" -> CDN URL

    group_names = priority_characters
    group_prompt_parts = [
        f"Group portrait of the three sworn brothers standing together under peach blossoms.",
    ]
    for name in group_names:
        cd = all_designs.get(name)
        if cd:
            group_prompt_parts.append(f"{name}: {cd['appearance'][:150]}.")
            if cd.get("clothing"):
                group_prompt_parts.append(f"Wearing {cd['clothing'][:100]}.")
    group_prompt_parts.append(f"Art style: {art_style}.")
    group_prompt_parts.append("No text, words, lettering, or typography.")
    group_prompt = " ".join(group_prompt_parts)

    group_key = "+".join(group_names)

    # Check if group ref exists from previous run
    existing_groups = novel["style_guide"].get("group_references", [])
    existing_group_url = ""
    for gr in existing_groups:
        if set(gr["character_names"]) == set(group_names) and gr.get("reference_image_url"):
            existing_group_url = gr["reference_image_url"]
            break

    if existing_group_url:
        group_refs[group_key] = existing_group_url
        print(f"  Reusing existing group ref: {', '.join(group_names)}")
        print(f"  CDN: {existing_group_url}")
    else:
        print(f"  Generating group portrait: {', '.join(group_names)}")
        png_bytes, cdn_url = generate_recraft(group_prompt, colors, aspect="landscape_16_9")
        group_path = REFS_DIR / "ref_group_three_brothers.png"
        group_path.write_bytes(png_bytes)
        group_refs[group_key] = cdn_url
        print(f"  Saved: {group_path.name} ({len(png_bytes):,} bytes)")
    print()

    # ── Phase 2: Generate scene panels with character refs ──
    print("=" * 60)
    print("PHASE 2: Scene Panels (FLUX Pro Kontext + character refs)")
    print("=" * 60)
    print()

    # Collect panels for target scenes
    panels_to_generate = []
    for scene_num in SCENES:
        prompt_files = sorted(PANELS_DIR.glob(f"scene{scene_num:02d}_panel*.prompt.txt"))
        for f in prompt_files:
            match = re.match(r"scene(\d+)_panel(\d+)\.prompt\.txt", f.name)
            if match:
                panels_to_generate.append((int(match.group(1)), int(match.group(2)), f))

    if not panels_to_generate:
        print("ERROR: No panels found for scenes", SCENES)
        sys.exit(1)

    print(f"Generating {len(panels_to_generate)} panels for scenes {SCENES}")
    print(f"  Character refs: {list(char_refs.keys())}")
    print(f"  Group refs: {list(group_refs.keys())}")
    print()

    # Also need a style anchor for panels without character matches
    style_anchor_url: str | None = None
    character_names = list(all_designs.keys())
    generated_files = []

    for scene_num, panel_num, prompt_file in panels_to_generate:
        seed = BASE_SEED + scene_num * 100 + panel_num
        png_path = PANELS_DIR / f"scene{scene_num:02d}_panel{panel_num:02d}.png"

        raw_text = prompt_file.read_text(encoding="utf-8")
        prompt = extract_prompt(raw_text)

        # Detect characters in this panel's prompt
        panel_chars = detect_characters_in_prompt(prompt, character_names)

        # Select reference
        ref_url, ref_source = select_reference(panel_chars, char_refs, group_refs, style_anchor_url)

        if ref_url is None and style_anchor_url is None:
            # First panel with no character ref — use Recraft as style anchor
            print(f"[{len(generated_files)+1}/{len(panels_to_generate)}] "
                  f"scene {scene_num}, panel {panel_num} — Recraft V4 Pro (style anchor)")
            png_bytes, cdn_url = generate_recraft(prompt + " No text, words, lettering, or typography.", colors, aspect="landscape_16_9")
            style_anchor_url = cdn_url
            ref_source = "style_anchor (recraft)"
        else:
            ref_label = f" [{ref_source}]" if ref_source != "style_anchor" else ""
            print(f"[{len(generated_files)+1}/{len(panels_to_generate)}] "
                  f"scene {scene_num}, panel {panel_num} (seed={seed}) — Kontext{ref_label}")
            print(f"  Characters detected: {panel_chars or '(none)'}")
            png_bytes, cdn_url = generate_kontext(prompt, seed, image_url=ref_url or style_anchor_url)

        png_path.write_bytes(png_bytes)
        print(f"  Saved: {png_path.name} ({len(png_bytes):,} bytes)")
        print()

        generated_files.append((scene_num, panel_num, png_path, ref_source))

    # ── Update novel.json ──
    print("=" * 60)
    print("Updating novel.json...")
    print("=" * 60)

    # Update character designs with reference URLs
    for cd in novel["style_guide"]["character_designs"]:
        name = cd["character_name"]
        if name in char_refs:
            cd["reference_image_url"] = char_refs[name]
            slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
            cd["reference_image_path"] = f"character_refs/ref_{slug}.png"
            print(f"  {name}: reference_image_url set")

    # Update group references
    novel["style_guide"]["group_references"] = [
        {
            "character_names": key.split("+"),
            "reference_image_url": url,
            "reference_image_path": "character_refs/ref_group_three_brothers.png",
        }
        for key, url in group_refs.items()
    ]

    # Update panel image paths and reference sources
    generated_set = {(s, p): ref for s, p, _, ref in generated_files}
    updated = 0
    for gp in novel["generated_panels"]:
        key = (gp["scene_number"], gp["panel_number"])
        if key in generated_set:
            s, p = key
            gp["image_path"] = f"panels/scene{s:02d}_panel{p:02d}.png"
            gp["reference_source"] = generated_set[key]
            updated += 1

    NOVEL_JSON.write_text(
        json.dumps(novel, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"\nDone! Generated {len(char_refs)} character refs, {len(group_refs)} group refs, "
          f"{len(generated_files)} panels. Updated {updated} entries in novel.json.")


if __name__ == "__main__":
    main()
