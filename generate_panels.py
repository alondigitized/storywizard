#!/usr/bin/env python3
"""Generate panel images from existing novel.json using mflux.

This script loads the panel scripts and style guide from an existing
novel.json and runs just the Artist stage to generate actual PNG images
via the mflux backend. Avoids re-running the full 9-stage pipeline.

Usage:
    python3 generate_panels.py [--slug SLUG] [--model klein|turbo] [--seed N] [--size WxH]
"""

import argparse
import json
import logging
import shutil
from pathlib import Path

from storywizard.agents.artist import Artist
from storywizard.config import PipelineConfig
from storywizard.models import PanelScript, VisualStyleGuide

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("generate_panels")

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate panels from existing novel.json")
    parser.add_argument("--slug", default="the-strange-case-of-dr.-jekyll-and-m",
                        help="Novel directory slug under output/")
    parser.add_argument("--model", choices=["klein", "turbo"], default="turbo")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--size", default="1024x768")
    parser.add_argument("--resume", action="store_true",
                        help="Skip panels that already have PNGs")
    args = parser.parse_args()

    w, h = [int(x) for x in args.size.split("x")]

    output_dir = Path("output") / args.slug
    panels_dir = output_dir / "panels"
    public_panels_dir = Path("public/panels") / args.slug

    # Load novel.json
    novel_path = output_dir / "novel.json"
    logger.info("Loading %s", novel_path)
    data = json.loads(novel_path.read_text())

    # Reconstruct models from JSON
    style_guide = VisualStyleGuide(**data["style_guide"])
    scripts = [PanelScript(**s) for s in data["panel_scripts"]]

    total_panels = sum(len(s.panels) for s in scripts)
    logger.info(
        "Loaded %d scenes, %d panels. Backend: mflux-%s, size: %dx%d, seed: %d",
        len(scripts), total_panels, args.model, w, h, args.seed,
    )

    # Configure for mflux
    config = PipelineConfig(
        image_backend="mflux",
        mflux_model=args.model,
        mflux_width=w,
        mflux_height=h,
        mflux_seed=args.seed,
    )

    if not args.resume:
        # Remove old PNGs to prevent mflux from appending _1 suffix
        for old_png in panels_dir.glob("*.png"):
            old_png.unlink()
            logger.info("Removed old panel: %s", old_png.name)
    else:
        # Filter out scripts/panels that already have PNGs
        existing = {p.stem for p in panels_dir.glob("*.png")}
        filtered_scripts = []
        skipped = 0
        for s in scripts:
            remaining_panels = []
            for p in s.panels:
                key = f"scene{s.scene_number:02d}_panel{p.panel_number:02d}"
                if key in existing:
                    skipped += 1
                else:
                    remaining_panels.append(p)
            if remaining_panels:
                from copy import deepcopy
                fs = deepcopy(s)
                fs.panels = remaining_panels
                filtered_scripts.append(fs)
        scripts = filtered_scripts
        total_panels = sum(len(s.panels) for s in scripts)
        logger.info("Resuming: skipped %d existing panels, %d remaining", skipped, total_panels)

    # Generate panels
    artist = Artist(config)
    generated = artist.generate_panels(scripts, style_guide, panels_dir)

    logger.info("Generated %d panels", len(generated))

    # Update novel.json with real image paths (merge with existing if resuming)
    if args.resume and "generated_panels" in data:
        existing = {(gp["scene_number"], gp["panel_number"]): gp for gp in data["generated_panels"]}
        for gp in generated:
            existing[(gp.scene_number, gp.panel_number)] = gp.model_dump()
        data["generated_panels"] = list(existing.values())
    else:
        data["generated_panels"] = [gp.model_dump() for gp in generated]
    novel_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Updated %s with generated panel data", novel_path)

    # Copy PNGs to public/ for Vercel static serving
    public_panels_dir.mkdir(parents=True, exist_ok=True)
    png_count = 0
    for f in panels_dir.glob("*.png"):
        shutil.copy2(f, public_panels_dir / f.name)
        png_count += 1
    logger.info("Copied %d PNGs to %s", png_count, public_panels_dir)

    logger.info("Done! %d panels generated.", len(generated))


if __name__ == "__main__":
    main()
