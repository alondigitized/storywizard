#!/usr/bin/env python3
"""Run the Storywizard publishing pipeline on a candidate story."""

import argparse
import logging
import sys

from storywizard.config import PipelineConfig
from storywizard.ingestion.gutenberg import fetch_book
from storywizard.pipeline import PublishingPipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("storywizard")


def main() -> None:
    parser = argparse.ArgumentParser(description="Storywizard AI Publishing Pipeline")
    parser.add_argument(
        "book_id", nargs="?", type=int, default=43,
        help="Project Gutenberg book ID (default: 43 = Jekyll & Hyde)",
    )
    parser.add_argument(
        "--backend", choices=["mock", "flux"], default="mock",
        help="Image generation backend (default: mock)",
    )
    parser.add_argument(
        "--max-scenes", type=int, default=15,
        help="Maximum number of scenes to extract (default: 15)",
    )
    parser.add_argument(
        "--flux-model", default="fal-ai/flux/dev",
        help="fal.ai model ID for Flux (default: fal-ai/flux/dev)",
    )
    parser.add_argument(
        "--flux-aspect", default="landscape_16_9",
        help="Aspect ratio for Flux images (default: landscape_16_9)",
    )
    parser.add_argument(
        "--flux-seed", type=int, default=None,
        help="Base seed for deterministic image generation (default: random)",
    )
    parser.add_argument(
        "--flux-guidance", type=float, default=3.5,
        help="Guidance scale for prompt adherence, 1.0-20.0 (default: 3.5)",
    )
    parser.add_argument(
        "--flux-steps", type=int, default=28,
        help="Number of inference steps, 1-100 (default: 28)",
    )
    parser.add_argument(
        "--flux-negative", default="",
        help="Negative prompt — concepts to exclude from generation",
    )
    args = parser.parse_args()

    config = PipelineConfig(
        image_backend=args.backend,
        max_scenes=args.max_scenes,
        flux_model=args.flux_model,
        flux_aspect_ratio=args.flux_aspect,
        flux_seed=args.flux_seed,
        flux_guidance_scale=args.flux_guidance,
        flux_num_inference_steps=args.flux_steps,
        flux_negative_prompt=args.flux_negative,
    )

    errors = config.validate()
    if errors:
        for error in errors:
            logger.error(error)
        sys.exit(1)

    if args.backend == "flux":
        logger.info("Using Flux image generation via fal.ai (%s)", args.flux_model)

    logger.info("Fetching book %d from Project Gutenberg...", args.book_id)
    metadata, text = fetch_book(args.book_id, config)
    logger.info("Loaded '%s' by %s (%d chars)", metadata.title, metadata.author, len(text))

    pipeline = PublishingPipeline(config)
    novel = pipeline.run(text, metadata)

    logger.info("=" * 60)
    logger.info("COMPLETE!")
    logger.info("Title: %s", novel.metadata.title)
    logger.info("Scenes: %d", len(novel.panel_scripts))
    logger.info("Panels: %d", len(novel.generated_panels))
    if novel.editorial_review:
        logger.info(
            "Editorial score: %d/10 (%s)",
            novel.editorial_review.overall_score,
            "approved" if novel.editorial_review.approved else "not approved",
        )
    logger.info("Output: %s/", config.output_dir)


if __name__ == "__main__":
    main()
